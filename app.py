import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go

# --- 1. アプリ設定とCSSデザイン ---
st.set_page_config(
    page_title="経営分析AI - B/S視点診断",
    page_icon="🛡️",
    layout="wide"
)

# プロフェッショナルなレポート風デザイン + コンサル視点強調
st.markdown("""
<style>
    /* 全体の背景とフォント */
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { font-family: 'Helvetica Neue', Arial, sans-serif; color: #333; }
    
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
    .score-title { font-size: 1.1rem; font-weight: bold; color: #555; margin-bottom: 5px; }
    .score-value { font-size: 3.5rem; font-weight: 800; margin: 5px 0; }
    .score-sub { font-size: 0.8rem; color: #888; }
    
    /* 色分け */
    .color-safety { color: #00C853; } /* 緑：安全性（最重要） */
    .color-profit { color: #2962FF; } /* 青：収益性 */
    .color-growth { color: #FF6D00; } /* オレンジ：成長性 */

    /* コンサル視点ボックス（差別化ポイント） */
    .consultant-box {
        background-color: #fff3e0;
        border-left: 6px solid #ff9800;
        padding: 20px;
        border-radius: 5px;
        margin: 20px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .consultant-title {
        color: #ef6c00;
        font-weight: bold;
        font-size: 1.2rem;
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    
    /* AI提案カード */
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
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except:
        model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("APIキーが設定されていません。")
    st.stop()

# --- 2. 計算ロジック（B/S重視） ---
def calculate_scores(rev, prev_rev, op_profit, assets, equity, cur_assets, cur_liab):
    # 1. 安全性 (B/S重視: 最重要指標)
    # 自己資本比率と流動比率から「倒産しにくさ」を算出
    equity_ratio = (equity / assets) * 100 if assets > 0 else 0
    current_ratio = (cur_assets / cur_liab) * 100 if cur_liab > 0 else 0
    # 自己資本比率40%以上、流動比率200%以上を理想とする
    score_safety = min(100, max(0, int((equity_ratio * 1.2) + (current_ratio * 0.15))))

    # 2. 収益性 (P/L)
    op_margin = (op_profit / rev) * 100 if rev > 0 else 0
    score_profit = min(100, max(0, int(op_margin * 8))) # 少し厳しめに
    
    # 3. 成長性
    growth_rate = (rev / prev_rev) * 100 if prev_rev > 0 else 100
    score_growth = min(100, max(0, int((growth_rate - 95) * 4)))

    return score_profit, score_safety, score_growth, op_margin, equity_ratio, growth_rate

# --- 3. サイドバー入力（概算許容） ---
with st.sidebar:
    st.title("🛡️ 簡易・経営診断")
    st.caption("決算書の数字を概算で入力してください。")
    
    company_name = st.text_input("企業名", value="株式会社サンプル")
    industry = st.selectbox("業種", ["製造業", "建設業", "運輸業", "卸売・小売", "サービス", "IT・通信", "その他"])
    
    st.markdown("---")
    st.markdown("### 1. 会社の規模 (P/L)")
    revenue = st.number_input("売上高 (概算)", value=10000, step=100, help="直近の決算数値")
    prev_revenue = st.number_input("前期の売上高 (概算)", value=9500, step=100)
    operating_profit = st.number_input("営業利益 (概算)", value=500, step=10, help="本業の儲け")

    st.markdown("### 2. 会社の体質 (B/S)")
    st.info("ここが重要です！B/Sのバランスを見ます。")
    current_assets = st.number_input("流動資産 (現預金など)", value=6000, step=100)
    current_liabilities = st.number_input("流動負債 (短期借入など)", value=4000, step=100)
    total_assets = st.number_input("総資産 (すべての資産)", value=10000, step=100)
    total_equity = st.number_input("純資産 (自己資本)", value=3000, step=100)

    analyze_btn = st.button("診断レポートを作成", type="primary", use_container_width=True)

# --- 4. メインコンテンツ ---

# ヘッダー
st.title(f"経営財務診断レポート: {company_name} 様")
st.markdown(f"**分析視点:** 財務コンサルタント視点（B/S重視） | **実施日:** 2026/01/14")
st.divider()

if analyze_btn:
    # スコア計算
    s_profit, s_safety, s_growth, val_profit, val_safety, val_growth = calculate_scores(
        revenue, prev_revenue, operating_profit, total_assets, total_equity, current_assets, current_liabilities
    )

    # --- セクション1: スコアカード (安全性を左に配置) ---
    st.subheader("1. 財務健全性スコア")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1.5])
    
    # 安全性（最重要）
    with col1:
        st.markdown(f"""
        <div class="score-card" style="border-top: 5px solid #00C853;">
            <div class="score-title">🟢 安全性 (B/S)</div>
            <div class="score-value color-safety">{s_safety}</div>
            <div class="score-sub">自己資本比率: {val_safety:.1f}%<br>会社の「潰れにくさ」</div>
        </div>
        """, unsafe_allow_html=True)

    # 収益性
    with col2:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-title">🔵 収益性 (P/L)</div>
            <div class="score-value color-profit">{s_profit}</div>
            <div class="score-sub">営業利益率: {val_profit:.1f}%<br>本業で稼ぐ力</div>
        </div>
        """, unsafe_allow_html=True)

    # 成長性
    with col3:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-title">🟠 成長性</div>
            <div class="score-value color-growth">{s_growth}</div>
            <div class="score-sub">売上対前期比: {val_growth:.1f}%<br>事業の勢い</div>
        </div>
        """, unsafe_allow_html=True)

    # チャート
    with col4:
        categories = ['安全性(B/S)', '収益性(P/L)', '成長性']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[s_safety, s_profit, s_growth],
            theta=categories,
            fill='toself',
            name=company_name,
            line_color='#00C853' 
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            margin=dict(l=20, r=20, t=20, b=20),
            height=250
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- セクション2: コンサルタントの視点（税理士との違い） ---
    # ロジック判定によるコメント生成
    consultant_comment = ""
    if s_safety < 40 and s_profit > 60:
        consultant_title = "⚠️ 典型的な「黒字倒産」予備軍のリスクがあります"
        consultant_comment = """
        税理士先生は「利益が出ているので節税しましょう」と言うかもしれません。<br>
        しかし、我々が見ると**「手元の現金余力に対し、稼働が大きすぎる（資金ショートのリスク）」**状態です。<br>
        今は節税よりも、**内部留保を厚くし、銀行評価を高める（B/Sを良くする）**対策が必要です。
        """
    elif s_safety > 70:
        consultant_title = "✅ 盤石な財務基盤です。攻めの投資が可能です"
        consultant_comment = """
        素晴らしい安全性です。税理士先生の指導が行き届いている、あるいは堅実な経営の賜物です。<br>
        この「信用力」を使えば、より有利な条件での資金調達や、**大規模な設備投資・人材投資**が可能です。<br>
        「守り」は完璧ですので、次は「リスクを取って攻める」ための保険活用をご提案します。
        """
    else:
        consultant_title = "💡 P/L（売上）だけでなく、B/S（資産）のバランスを見直しましょう"
        consultant_comment = """
        日々の資金繰りに問題はないかと思いますが、何かあった時の「耐久力」をもう少し高めたい状態です。<br>
        税務上の利益（P/L）を追うだけでなく、**「会社に現金をどう残すか（B/S）」**という視点で、
        退職金準備や有事の資金確保を検討するタイミングです。
        """

    st.markdown(f"""
    <div class="consultant-box">
        <div class="consultant-title">{consultant_title}</div>
        <div>{consultant_comment}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- セクション3: AI分析 ---
    with st.spinner("AIコンサルタントが詳細分析レポートを作成中..."):
        prompt = f"""
        あなたは、中小企業の財務改善を得意とするプロの経営コンサルタントです。
        税理士のような「節税・税務処理」の視点ではなく、
        **「会社を潰さない（安全性）」「財務体質を強くする（B/S重視）」**という視点で分析してください。

        【対象企業】{company_name} ({industry})
        【財務スコア】安全性:{s_safety}, 収益性:{s_profit}, 成長性:{s_growth}
        【詳細数値】自己資本比率:{val_safety:.1f}%, 流動比率:{(current_assets/current_liabilities)*100:.1f}%

        以下の3つのパートを作成してください。セクション区切り文字 "---SPLIT---" を使用すること。

        Part 1: B/S（貸借対照表）から見る財務診断
        → 利益が出ていても倒産するリスクはないか？自己資本の厚みは十分か？など、経営の「安全性」を中心に解説。

        ---SPLIT---

        Part 2: 想定される経営リスク
        → 「資金ショート」「人材流出」「災害時の事業停止」など、財務数値から読み取れる具体的なリスクを3つ挙げる。

        ---SPLIT---

        Part 3: 財務体質強化へのソリューション
        → 節税ではなく「会社を守る」ための提案（日新火災の商材：ビジサポ、労災あんしん、事業活動包括など）を絡めて、
        「なぜ今、保険でリスクヘッジが必要か」を経営者に響く言葉で提案。
        """
        
        try:
            response = model.generate_content(prompt)
            parts = response.text.split("---SPLIT---")
            
            p1 = parts[0] if len(parts) > 0 else "分析中..."
            p2 = parts[1] if len(parts) > 1 else "分析中..."
            p3 = parts[2] if len(parts) > 2 else "分析中..."

            st.subheader("2. 詳細分析レポート")
            st.markdown(p1)

            st.markdown("---")
            st.subheader("3. 潜在的な経営リスク")
            st.markdown(p2)

            st.markdown("---")
            st.subheader("4. 財務強化ソリューション (日新火災)")
            st.success(p3)

        except Exception as e:
            st.error(f"AI分析エラー: {e}")

else:
    # 待機画面
    st.info("👈 左側のサイドバーに、決算書の数字（概算で結構です）を入力してください。")
    st.markdown("""
    ### 経営者様へ：今の顧問税理士とは「違う視点」で会社を見てみませんか？
    
    多くの経営者は**P/L（売上と利益）**を気にされますが、会社を長く存続させるために本当に重要なのは**B/S（資産と負債のバランス）**です。
    
    このツールでは、**「会社がどれくらい潰れにくいか（安全性）」**を瞬時に診断します。
    """)
