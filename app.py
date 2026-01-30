import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import datetime

# --- 1. アプリ設定とCSSデザイン ---
st.set_page_config(
    page_title="経営財務診断レポート | Nisshin Fire",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# デザインCSS
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
    .meta-info { font-size: 0.9rem; color: #666; text-align: right; line-height: 1.5; }

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
    .c-gray { color: #B0BEC5; } /* データなし用 */

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

# --- 2. 計算ロジック (Null対応版) ---
def calculate_scores(rev, prev_rev, op_profit, assets, equity, cur_assets, cur_liab):
    
    # 安全な割り算関数 (NoneがあったらNoneを返す)
    def safe_calc(numerator, denominator, multiplier=100):
        if numerator is None or denominator is None or denominator == 0:
            return None
        return (numerator / denominator) * multiplier

    # --- 安全性 (B/S) ---
    equity_ratio = safe_calc(equity, assets)
    current_ratio = safe_calc(cur_assets, cur_liab)
    
    if equity_ratio is not None and current_ratio is not None:
        # 両方データがある場合
        score_safety = min(100, max(0, int((equity_ratio * 1.2) + (current_ratio * 0.15))))
    elif equity_ratio is not None:
        # 自己資本比率だけある場合（簡易計算）
        score_safety = min(100, max(0, int(equity_ratio * 1.5)))
    else:
        # データ不足
        score_safety = None

    # --- 収益性 (P/L) ---
    op_margin = safe_calc(op_profit, rev)
    
    if op_margin is not None:
        score_profit = min(100, max(0, int(op_margin * 8)))
    else:
        score_profit = None

    # --- 成長性 ---
    if rev is not None and prev_rev is not None and prev_rev > 0:
        growth_rate = (rev / prev_rev) * 100
        score_growth = min(100, max(0, int((growth_rate - 95) * 4)))
    else:
        growth_rate = None
        score_growth = None

    return score_profit, score_safety, score_growth, op_margin, equity_ratio, growth_rate

# --- 3. サイドバー入力 (Null許容) ---
with st.sidebar:
    st.markdown("## 🛡️ 経営診断ツール")
    
    agent_name = st.text_input("担当者名", value="園部", placeholder="氏名を入力")
    
    st.markdown(f"日新火災海上保険株式会社<br>担当: {agent_name}", unsafe_allow_html=True)
    st.divider()
    
    company_name = st.text_input("企業名", value="株式会社サンプル技研")
    industry = st.selectbox("業種", ["建設業", "製造業", "運送業", "卸売・小売", "サービス", "IT・通信", "医療・福祉", "その他"])
    
    st.info("💡 数字が不明な箇所は「空欄」のままでOKです。")

    # value=None に設定することで、初期値を空欄にします
    with st.expander("① 決算書 P/L (概算)", expanded=True):
        revenue = st.number_input("売上高 (万円)", value=None, step=100, placeholder="不明な場合は空欄")
        prev_revenue = st.number_input("前期売上 (万円)", value=None, step=100, placeholder="不明な場合は空欄")
        operating_profit = st.number_input("営業利益 (万円)", value=None, step=10, placeholder="不明な場合は空欄")

    with st.expander("② 決算書 B/S (重要)", expanded=True):
        st.caption("※ここが「会社の倒産確率」を分けます")
        current_assets = st.number_input("流動資産 (現金等)", value=None, step=100, placeholder="不明な場合は空欄")
        current_liabilities = st.number_input("流動負債 (借入等)", value=None, step=100, placeholder="不明な場合は空欄")
        total_assets = st.number_input("総資産", value=None, step=100, placeholder="不明な場合は空欄")
        total_equity = st.number_input("純資産 (自己資本)", value=None, step=100, placeholder="不明な場合は空欄")

    st.markdown("---")
    analyze_btn = st.button("レポートを作成する", type="primary", use_container_width=True)

# --- 4. メインコンテンツ ---

# ヘッダー
today_str = datetime.date.today().strftime('%Y/%m/%d')
st.markdown(f"""
<div class="report-header">
    <div class="company-name">{company_name} 御中</div>
    <div class="meta-info">
        経営財務・リスク診断レポート<br>
        作成日: {today_str} | 分析担当: {agent_name}
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

        # 安全性表示ロジック
        if s_safety is not None:
            safe_disp = s_safety
            safe_sub = f"自己資本比率: {val_safety:.1f}%<br>不況耐久力"
            css_safe = "c-safe"
        else:
            safe_disp = "-"
            safe_sub = "データ不足<br>入力が必要です"
            css_safe = "c-gray"

        with col1:
            st.markdown(f"""
            <div class="score-box">
                <div class="score-lbl">🛡️ 安全性 (B/S)</div>
                <div class="score-val {css_safe}">{safe_disp}</div>
                <div class="score-sub">{safe_sub}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 収益性表示ロジック
        if s_profit is not None:
            prof_disp = s_profit
            prof_sub = f"営業利益率: {val_profit:.1f}%<br>稼ぐ力"
            css_prof = "c-profit"
        else:
            prof_disp = "-"
            prof_sub = "データ不足<br>入力が必要です"
            css_prof = "c-gray"

        with col2:
            st.markdown(f"""
            <div class="score-box">
                <div class="score-lbl">💰 収益性 (P/L)</div>
                <div class="score-val {css_prof}">{prof_disp}</div>
                <div class="score-sub">{prof_sub}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # 成長性表示ロジック
        if s_growth is not None:
            grow_disp = s_growth
            grow_sub = f"対前期比: {val_growth:.1f}%<br>事業の勢い"
            css_grow = "c-growth"
        else:
            grow_disp = "-"
            grow_sub = "データ不足<br>入力が必要です"
            css_grow = "c-gray"

        with col3:
            st.markdown(f"""
            <div class="score-box">
                <div class="score-lbl">📈 成長性</div>
                <div class="score-val {css_grow}">{grow_disp}</div>
                <div class="score-sub">{grow_sub}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # チャート (Noneの場合は0として描画し、見た目を整える)
        with col4:
            categories = ['安全性', '収益性', '成長性']
            # Noneを0に変換してチャート用データ作成
            plot_vals = [
                s_safety if s_safety is not None else 0,
                s_profit if s_profit is not None else 0,
                s_growth if s_growth is not None else 0
            ]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=plot_vals,
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

    # AI分析の実行
    with st.spinner("AIコンサルタントがリスク分析と提案書を作成中..."):
        # プロンプト用に数値を文字列化（None対応）
        fmt = lambda x, unit="": f"{x}{unit}" if x is not None else "データなし"
        
        prompt = f"""
        あなたは日新火災海上保険のリスクコンサルタント（担当:{agent_name}）です。
        以下の企業データに基づき、「経営リスク」と「日新火災の保険による解決策」を提案してください。
        
        【企業データ】
        企業名: {company_name} ({industry})
        財務スコア: 安全性{fmt(s_safety)}, 収益性{fmt(s_profit)}, 成長性{fmt(s_growth)}
        (自己資本比率{fmt(val_safety, "%")}, 営業利益率{fmt(val_profit, "%")})
        
        【重要なお願い】
        数値が「データなし」となっている項目については、分析を行わず、「データ不足のため分析できません」と記述してください。
        判明しているデータのみを使って、鋭いリスク指摘と保険提案を行ってください。

        【出力フォーマット】
        以下の区切り文字 "|||" を使って、2つのパートに完全に分けて出力してください。
        
        Part 1: 現在の経営リスク (3つ)
        - 判明している財務数値から読み取れる具体的なリスク。
        - 箇条書きで、各リスクに短いタイトルをつけてください。
        - 警告アイコン(⚠️)などは不要です。テキストのみ。
        
        |||
        
        Part 2: 日新火災からのご提案 (3つ)
        - 上記リスクに対応する日新火災の商品（ビジサポ・事業活動包括、労災あんしん、サイバー保険、企業財産包括など）を具体的に挙げる。
        - なぜその保険が必要か、経営メリット（B/Sを守る等）を添えて。
        - 担当者の「{agent_name}」が親身にサポートする旨を少し匂わせて。
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
        # Markdownの整形
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
        # Markdownの整形
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
    st.markdown(f"""
    <div style="text-align: center; margin-top: 50px; color: #888; font-size: 0.8rem;">
        ※本レポートはAIによる簡易診断です。詳細なリスク分析については、担当者（{agent_name}）までご相談ください。<br>
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
            不明な数字は「空欄」のままで構いません。<br>
            AIが入力された情報のみから、貴社の「隠れたリスク」と「最適な解決策」を提示します。
        </p>
    </div>
    """, unsafe_allow_html=True)
