import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go

# --- 1. アプリ設定とCSSデザイン ---
st.set_page_config(
    page_title="経営財務診断レポート | Nisshin Fire",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# デザインCSS: 美しさ、信頼感、可読性を重視
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');
    
    .stApp {
        background-color: #f0f2f6;
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* ヘッダー */
    .report-header {
        background: white;
        padding: 20px 30px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-bottom: 4px solid #b71c1c; /* 日新レッド */
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .company-name { font-size: 1.8rem; font-weight: 700; color: #1a237e; }
    .meta-info { font-size: 0.9rem; color: #666; text-align: right; }

    /* 共通カードスタイル */
    .card-container {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    
    /* セクションタイトル */
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #333;
        margin: 30px 0 15px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-icon { font-size: 1.5rem; }

    /* スコアカード */
    .score-box {
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        background: #fff;
        border: 1px solid #eee;
    }
    .score-val { font-size: 3.2rem; font-weight: 800; line-height: 1.0; margin: 10px 0; }
    .score-lbl { font-size: 0.9rem; font-weight: bold; color: #555; }
    .score-sub { font-size: 0.8rem; color: #888; margin-top: 5px; }
    
    /* カラー定義 */
    .c-safe { color: #00C853; }
    .c-profit { color: #2962FF; }
    .c-growth { color: #FF6D00; }

    /* リスクカード（警告） */
    .risk-card {
        background-color: #fff5f5;
        border-left: 5px solid #e53935;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .risk-title { color: #c62828; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; display: flex; align-items: center; gap:8px;}
    
    /* 提案カード（ソリューション） */
    .proposal-card {
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .proposal-title { color: #1b5e20; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; display: flex; align-items: center; gap:8px;}

    /* 印刷時の調整 */
    @media print {
        section[data-testid="stSidebar"] { display: none; }
        .stApp { background: white; }
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
    st.error("APIキー設定エラー: secrets.tomlを確認してください。")
    st.stop()

# --- 2. 計算ロジック ---
def calculate_scores(rev, prev_rev, op_profit, assets, equity, cur_assets, cur_liab):
    # 安全性 (B/S重視)
    equity_ratio = (equity / assets) * 100 if assets > 0 else 0
    current_ratio = (cur_assets / cur_liab) * 100 if cur_liab > 0 else 0
    score_safety = min(100, max(0, int((equity_ratio * 1.2) + (current_ratio * 0.15))))

    # 収益性 (P/L)
    op_margin = (op_profit / rev) * 100 if rev > 0 else 0
    score_profit = min(100, max(0, int(op_margin * 8)))
    
    # 成長性
    growth_rate = (rev / prev_rev) * 100 if prev_rev > 0 else 100
    score_growth = min(100, max(0, int((growth_rate - 95) * 4)))

    return score_profit, score_safety, score_growth, op_margin, equity_ratio, growth_rate

# --- 3. サイドバー入力 ---
with st.sidebar:
    st.markdown("## 🛡️ 経営診断ツール")
    st.markdown("日新火災海上保険株式会社<br>担当: 園部", unsafe_allow_html=True)
    st.divider()
    
    company_name = st.text_input("企業名", value="株式会社サンプル技研")
    industry = st.selectbox("業種", ["建設業", "製造業", "運送業", "卸売・小売", "サービス", "IT・通信", "医療・福祉", "その他"])
    
    with st.expander("① 決算書 P/L (概算)", expanded=True):
        revenue = st.number_input("売上高 (万円)", value=12000, step=100)
        prev_revenue = st.number_input("前期売上 (万円)", value=11000, step=100)
        operating_profit = st.number_input("営業利益 (万円)", value=600, step=10)

    with st.expander("② 決算書 B/S (重要)", expanded=True):
        st.caption("※ここが「会社の倒産確率」を分けます")
        current_assets = st.number_input("流動資産 (現金等)", value=8000, step=100)
        current_liabilities = st.number_input("流動負債 (借入等)", value=5000, step=100)
        total_assets = st.number_input("総資産", value=15000, step=100)
        total_equity = st.number_input("純資産 (自己資本)", value=6000, step=100)

    st.markdown("---")
    analyze_btn = st.button("レポートを作成する", type="primary", use_container_width=True)

# --- 4. メインコンテンツ ---

# ヘッダー
st.markdown(f"""
<div class="report-header">
    <div class="company-name">{company_name} 御中</div>
    <div class="meta-info">
        経営財務・リスク診断レポート<br>
        作成日: 2026/01/21 | 分析担当: 園部
    </div>
</div>
""", unsafe_allow_html=True)

if analyze_btn:
    # 計算実行
    s_profit, s_safety, s_growth, val_profit, val_safety, val_growth = calculate_scores(
        revenue, prev_revenue, operating_profit, total_assets, total_equity, current_assets, current_liabilities
    )

    # ==========================================
    # 1. 企業経営スコア (Safety, Profit, Growth)
    # ==========================================
    st.markdown('<div class="section-title"><span class="section-icon">📊</span> 1. 企業経営スコア診断</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2])

        # 安全性
        with col1:
            st.markdown(f"""
            <div class="score-box">
                <div class="score-lbl">🛡️ 安全性 (B/S)</div>
                <div class="score-val c-safe">{s_safety}</div>
                <div class="score-sub">自己資本比率: {val_safety:.1f}%<br>不況耐久力</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 収益性
        with col2:
            st.markdown(f"""
            <div class="score-box">
                <div class="score-lbl">💰 収益性 (P/L)</div>
                <div class="score-val c-profit">{s_profit}</div>
                <div class="score-sub">営業利益率: {val_profit:.1f}%<br>稼ぐ力</div>
            </div>
            """, unsafe_allow_html=True)
            
        # 成長性
        with col3:
            st.markdown(f"""
            <div class="score-box">
                <div class="score-lbl">📈 成長性</div>
                <div class="score-val c-growth">{s_growth}</div>
                <div class="score-sub">対前期比: {val_growth:.1f}%<br>事業の勢い</div>
            </div>
            """, unsafe_allow_html=True)
            
        # チャート
        with col4:
            categories = ['安全性', '収益性', '成長性']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[s_safety, s_profit, s_growth],
                theta=categories,
                fill='toself',
                name='Score',
                line_color='#1a237e'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)),
                margin=dict(l=20, r=20, t=10, b=10),
                height=180,
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)

    # AI分析の実行（リスクと提案を分離して生成）
    with st.spinner("AIコンサルタントがリスク分析と提案書を作成中..."):
        prompt = f"""
        あなたは日新火災海上保険のリスクコンサルタントです。
        以下の企業データに基づき、「経営リスク」と「日新火災の保険による解決策」を提案してください。
        
        【企業データ】
        企業名: {company_name} ({industry})
        財務スコア: 安全性{s_safety}, 収益性{s_profit}, 成長性{s_growth}
        (自己資本比率{val_safety:.1f}%, 営業利益率{val_profit:.1f}%)

        【出力フォーマット】
        以下の区切り文字 "|||" を使って、2つのパートに完全に分けて出力してください。
        
        Part 1: 現在の経営リスク (3つ)
        - 財務数値から読み取れる具体的なリスク（資金ショート、人材流出、賠償リスクなど）。
        - 箇条書きで、各リスクに短いタイトルをつけてください。
        - 警告アイコン(⚠️)などは不要です。テキストのみ。
        
        |||
        
        Part 2: 日新火災からのご提案 (3つ)
        - 上記リスクに対応する日新火災の商品（ビジサポ・事業活動包括、労災あんしん、サイバー保険、企業財産包括など）を具体的に挙げる。
        - なぜその保険が必要か、経営メリット（B/Sを守る等）を添えて。
        """
        
        try:
            response = model.generate_content(prompt)
            parts = response.text.split("|||")
            risk_text = parts[0] if len(parts) > 0 else "分析中..."
            proposal_text = parts[1] if len(parts) > 1 else "分析中..."
            
        except Exception as e:
            risk_text = "分析エラーが発生しました。"
            proposal_text = "分析エラーが発生しました。"

    # ==========================================
    # 2. 現在の経営リスク & 3. ご提案
    # ==========================================
    col_risk, col_prop = st.columns(2)
    
    # 左側：経営リスク
    with col_risk:
        st.markdown('<div class="section-title"><span class="section-icon">⚠️</span> 2. 現在の経営リスク</div>', unsafe_allow_html=True)
        # Markdownの内容をパースしてカード化（簡易処理）
        lines = risk_text.strip().split('\n')
        content_buffer = ""
        for line in lines:
            if line.strip():
                content_buffer += line + "<br>"
        
        st.markdown(f"""
        <div class="risk-card">
            <div class="risk-title">⚠️ 財務・事業リスク診断</div>
            <div style="line-height: 1.6; color: #444;">
                {content_buffer}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 右側：日新火災からのご提案
    with col_prop:
        st.markdown('<div class="section-title"><span class="section-icon">🎁</span> 3. 日新火災からのご提案</div>', unsafe_allow_html=True)
        # Markdownの内容をパース
        lines = proposal_text.strip().split('\n')
        content_buffer = ""
        for line in lines:
            if line.strip():
                content_buffer += line + "<br>"

        st.markdown(f"""
        <div class="proposal-card">
            <div class="proposal-title">✅ ソリューション提案</div>
            <div style="line-height: 1.6; color: #444;">
                {content_buffer}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # フッターメッセージ
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; color: #888; font-size: 0.8rem;">
        ※本レポートはAIによる簡易診断です。詳細なリスク分析については、担当者までご相談ください。<br>
        日新火災海上保険株式会社
    </div>
    """, unsafe_allow_html=True)

else:
    # 初期画面
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h2 style="color:#1a237e;">経営財務・リスク診断システム</h2>
        <p style="color:#666; font-size:1.1rem;">
            左側のメニューに数値を入力し、<b>「レポートを作成する」</b>ボタンを押してください。<br>
            AIが財務数値を分析し、貴社の「隠れたリスク」と「最適な解決策」を提示します。
        </p>
    </div>
    """, unsafe_allow_html=True)
