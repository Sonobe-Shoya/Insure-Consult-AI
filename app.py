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

# モダン・プロフェッショナルデザインの適用
st.markdown("""
<style>
    /* Google Fontsの読み込み (日本語対応) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap');

    /* 全体の設定 */
    .stApp {
        background-color: #f4f6f9; /* 背景色：薄いグレー */
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* ヘッダー周り */
    .header-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-bottom: 3px solid #b71c1c; /* 日新火災イメージの赤 */
    }
    .main-title {
        font-size: 1.8rem;
        font-weight: 900;
        color: #1a237e;
    }
    .sub-info {
        font-size: 0.9rem;
        color: #666;
    }

    /* カードデザイン（共通） */
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .card:hover {
        transform: translateY(-2px);
    }

    /* スコア表示 */
    .score-label {
        font-size: 1.0rem;
        font-weight: bold;
        color: #555;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .score-number {
        font-size: 3.8rem;
        font-weight: 900;
        line-height: 1.0;
        margin: 10px 0;
    }
    .score-desc {
        font-size: 0.85rem;
        color: #888;
        border-top: 1px solid #eee;
        padding-top: 5px;
        margin-top: 5px;
    }

    /* 色定義 */
    .text-safe { color: #00c853; }   /* 安全：緑 */
    .text-profit { color: #2962ff; } /* 収益：青 */
    .text-growth { color: #ff6d00; } /* 成長：オレンジ */
    .text-danger { color: #d32f2f; } /* 危険：赤 */

    /* コンサルタントコメントBOX */
    .consultant-box {
        background: linear-gradient(to right, #ffffff, #fff8e1);
        border-left: 6px solid #ff8f00;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin: 20px 0;
    }
    .consultant-head {
        font-weight: bold;
        font-size: 1.2rem;
        color: #ef6c00;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }

    /* セクション見出し */
    .section-header {
        font-size: 1.4rem;
        font-weight: bold;
        color: #333;
        margin: 30px 0 15px 0;
        border-left: 5px solid #1a237e;
        padding-left: 15px;
    }

    /* 印刷時の設定（サイドバーを消す） */
    @media print {
        section[data-testid="stSidebar"] { display: none; }
        .stApp { background-color: white; }
        .card { box-shadow: none; border: 1px solid #ddd; }
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
    st.markdown("---")
    
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

# ヘッダーエリア
st.markdown(f"""
<div class="header-container">
    <div class="sub-info">経営財務・リスク診断レポート</div>
    <div class="main-title">{company_name} 御中</div>
    <div class="sub-info" style="text-align:right;">作成日: 2026/01/14 | 分析担当: 園部</div>
</div>
""", unsafe_allow_html=True)

if analyze_btn:
    # スコア計算
    s_profit, s_safety, s_growth, val_profit, val_safety, val_growth = calculate_scores(
        revenue, prev_revenue, operating_profit, total_assets, total_equity, current_assets, current_liabilities
    )

    # === SECTION 1: スコアカード ===
    st.markdown('<div class="section-header">1. 経営健全性スコア</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1.3])
    
    # 安全性（最重要）
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="score-label">🛡️ 安全性(B/S)</div>
            <div class="score-number text-safe">{s_safety}</div>
            <div class="score-desc">
                <b>自己資本比率: {val_safety:.1f}%</b><br>
                不況への耐久力
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 収益性
    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="score-label">💰 収益性(P/L)</div>
            <div class="score-number text-profit">{s_profit}</div>
            <div class="score-desc">
                <b>営業利益率: {val_profit:.1f}%</b><br>
                本業で稼ぐ力
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 成長性
    with col3:
        st.markdown(f"""
        <div class="card">
            <div class="score-label">📈 成長性</div>
            <div class="score-number text-growth">{s_growth}</div>
            <div class="score-desc">
                <b>対前期比: {val_growth:.1f}%</b><br>
                事業の勢い
            </div>
        </div>
        """, unsafe_allow_html=True)

    # レーダー
