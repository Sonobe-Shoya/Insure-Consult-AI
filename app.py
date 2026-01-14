import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go

# --- 1. アプリ設定とCSSデザイン ---
st.set_page_config(
    page_title="経営分析AI for Nisshin Fire",
    page_icon="🛡️",
    layout="wide"
)

# プロフェッショナルなレポート風デザインにするCSS
st.markdown("""
<style>
    /* 全体の背景とフォント */
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #333;
    }
    
    /* スコアカードのデザイン */
    .score-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
        height: 100%;
    }
    .score-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #555;
        margin-bottom: 10px;
    }
    .score-value {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 10px 0;
    }
    /* 色分け */
    .color-profit { color: #2962FF; } /* 青：収益性 */
    .color-safety { color: #00C853; } /* 緑：安全性 */
    .color-growth { color: #FF6D00; } /* オレンジ：成長性 */

    /* 課題カードのデザイン */
    .issue-card {
        background-color: white;
        border-left: 5px solid #d32f2f;
        padding: 15px 20px;
        margin-bottom: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .issue-title {
        font-weight: bold;
        font-size: 1.1rem;
        color: #d32f2f;
        margin-bottom: 5px;
    }

    /* 提案カードのデザイン */
    .proposal-card {
        background-color: #e3f2fd;
        border: 1px solid #bbdefb;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# APIキー設定
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # 最新モデル設定
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except:
        model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("APIキーが設定されていません。")
    st.stop()

# --- 2. 計算ロジック（スコア化） ---
def calculate_scores(rev, prev_rev, op_profit, assets, equity, cur_assets, cur_liab):
    # 1. 収益性 (営業利益率などから簡易算出)
    # 基準: 利益率10%で100点とする簡易ロジック
    op_margin = (op_profit / rev) * 100 if rev > 0 else 0
    score_profit = min(100, max(0, int(op_margin * 10))) 
    
    # 2. 安全性 (自己資本比率と流動比率から算出)
    # 基準: 自己資本比率40%以上で高得点
    equity_ratio = (equity / assets) * 100 if assets > 0 else 0
    current_ratio = (cur_assets / cur_liab) * 100 if cur_liab > 0 else 0
    # 複合スコア
    raw_safety = (equity_ratio * 1.5) + (current_ratio * 0.1)
    score_safety = min(100, max(0, int(raw_safety)))

    # 3. 成長性 (売上高成長率)
    # 基準: 120%成長で100点
    growth_rate = (rev / prev_rev) * 100 if prev_rev > 0 else 100
    score_growth = min(100, max(0, int((growth_rate - 90) * 3.5)))

    return score_profit, score_safety, score_growth, op_margin, equity_ratio, growth_rate

# --- 3. サイドバー入力 ---
with st.sidebar:
    st.title("🛡️ 企業データ入力")
    company_name = st.text_input("企業名", value="株式会社サンプル技研")
    industry = st.selectbox("業種", ["製造業", "建設業", "運輸業", "小売・卸売業", "IT・通信", "医療・福祉", "その他"])
    st.markdown("---")
    st.markdown("### 📊 財務数値 (単位:万円)")
    
    with st.expander("損益情報 (P/L)", expanded=True):
        revenue = st.number_input("売上高", value=52000, step=100)
        prev_revenue = st.number_input("前期売上", value=48000, step=100)
        operating_profit = st.number_input("営業利益", value=3500, step=10)

    with st.expander("資産情報 (B/S)", expanded=True):
        current_assets = st.number_input("流動資産", value=25000, step=100)
        current_liabilities = st.number_input("流動負債", value=20000, step=100)
        total_assets = st.number_input("総資産", value=45000, step=100)
        total_equity = st.number_input("純資産", value=18000, step=100)

    analyze_btn = st.button("レポートを作成する", type="primary", use_container_width=True)

# --- 4. メインコンテンツ ---

# ヘッダー
st.title(f"{company_name} 様 経営診断レポート")
st.markdown(f"**業種:** {industry} | **分析日:** 2026/01/14")
st.divider()

if analyze_btn:
    # スコア計算
    s_profit, s_safety, s_growth, val_profit, val_safety, val_growth = calculate_scores(
        revenue, prev_revenue, operating_profit, total_assets, total_equity, current_assets, current_liabilities
    )

    # --- セクション1: スコアカードとレーダーチャート ---
    st.subheader("1. 総合診断スコア")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])
    
    with col1:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-title">🔵 収益性</div>
            <div class="score-value color-profit">{s_profit}</div>
            <div style="font-size:0.8rem; color:#666;">営業利益率: {val_profit:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-title">🟢 安全性</div>
            <div class="score-value color-safety">{s_safety}</div>
            <div style="font-size:0.8rem; color:#666;">自己資本比率: {val_safety:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-title">🟠 成長性</div>
            <div class="score-value color-growth">{s_growth}</div>
            <div style="font-size:0.8rem; color:#666;">売上対前期比: {val_growth:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # レーダーチャートの作成 (Plotly)
        categories = ['収益性', '安全性', '成長性']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[s_profit, s_safety, s_growth],
            theta=categories,
            fill='toself',
            name=company_name,
            line_color='#1E88E5'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            margin=dict(l=20, r=20, t=20, b=20),
            height=250
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- AI分析の実行 ---
    with st.spinner("AIコンサルタントが詳細分析レポートを作成中..."):
        prompt = f"""
        あなたは日新火災海上保険の熟練リスクコンサルタントです。
        以下の企業データと、計算されたスコアに基づき、経営者向けの専門的な分析レポートを作成してください。
        
        【企業データ】
        - 企業名: {company_name} ({industry})
        - 売上高: {revenue}万円 (成長率: {val_growth:.1f}%)
        - 営業利益率: {val_profit:.1f}%
        - 流動比率: {(current_assets/current_liabilities)*100:.1f}%
        - 自己資本比率: {val_safety:.1f}%
        
        【算出スコア(100点満点)】
        - 収益性: {s_profit}点
        - 安全性: {s_safety}点
        - 成長性: {s_growth}点

        【出力形式】
        以下のセクション区切り文字 "---SPLIT---" を使って3つのパートに分けて出力してください。

        Part 1: 各指標の詳細分析
        (収益性・安全性・成長性それぞれについて、なぜこの点数なのか、財務数値を用いて具体的に解説)

        ---SPLIT---

        Part 2: 特定された経営課題 (3つ)
        (この財務状況から読み取れる具体的なリスク。例:「設備老朽化リスク」「運転資金不足」など。
        必ず「課題タイトル」と「詳細説明」をセットにすること)

        ---SPLIT---

        Part 3: 日新火災からのソリューション提案
        (特定された課題に対する保険提案。ビジサポ、労災あんしん、サイバー、ビジネスプロパティ等から最適なものを選択し、導入効果を記述)
        """
        
        try:
            response = model.generate_content(prompt)
            parts = response.text.split("---SPLIT---")
            
            # コンテンツがない場合のガード
            part1 = parts[0] if len(parts) > 0 else "分析エラー"
            part2 = parts[1] if len(parts) > 1 else "分析エラー"
            part3 = parts[2] if len(parts) > 2 else "分析エラー"

            st.markdown("---")

            # --- セクション2: 詳細分析 ---
            st.subheader("2. 財務指標の詳細分析")
            st.info(part1)

            # --- セクション3: 経営課題の特定 ---
            st.markdown("---")
            st.subheader("3. 経営課題の特定")
            
            # AIのテキストをそのまま表示するか、少し加工するか
            # ここではシンプルに見やすく表示
            st.markdown(part2)

            # --- セクション4: ソリューション提案 ---
            st.markdown("---")
            st.subheader("4. 日新火災からのソリューション提案")
            st.success(part3)

        except Exception as e:
            st.error(f"分析中にエラーが発生しました: {e}")

else:
    # 待機画面
    st.info("👈 左側のサイドバーに財務数値を入力し、「レポートを作成する」ボタンを押してください。")
    st.markdown("""
    ### このツールの特徴
    * **自動スコアリング:** 収益性・安全性・成長性を瞬時に点数化します。
    * **バランスチャート:** 企業の強み・弱みを三角形のチャートで可視化します。
    * **課題特定:** 財務データから隠れた経営リスクを洗い出します。
    """)
