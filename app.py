import streamlit as st
import google.generativeai as genai

# --- 1. アプリの基本設定 ---
st.set_page_config(
    page_title="経営分析AI for Nisshin Fire",
    page_icon="🛡️",
    layout="wide"
)

# APIキーの設定
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("APIキーの設定が必要です。")
    st.stop()

# --- 2. AIモデルの指定 ---
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    model = genai.GenerativeModel('gemini-flash-latest')

# --- 3. セッション状態の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは。日新火災のリスクコンサルタントAIです。\n左側のサイドバーに数値を入力し、分析を開始してください。"}
    ]

# --- ヘルパー関数: テキストをカード形式で表示する ---
def display_as_cards(text):
    # 区切り文字で3つのパートに分割を試みる
    parts = text.split("---SPLIT---")
    
    if len(parts) >= 3:
        # 成功したらカード形式で表示
        
        # 1枚目：診断サマリー（青）
        with st.container(border=True):
            st.markdown("### 🏢 1. 経営診断サマリー")
            st.info(parts[0].strip())

        # 2枚目：リスク（黄色）
        with st.container(border=True):
            st.markdown("### ⚠️ 2. 想定される経営リスク")
            st.warning(parts[1].strip())
            
        # 3枚目：提案（緑/成功色）
        with st.container(border=True):
            st.markdown("### 🛡️ 3. 日新火災からのソリューション提案")
            st.success(parts[2].strip())
            
    else:
        # 分割に失敗した場合はそのまま表示（フォールバック）
        st.markdown(text)


# --- 4. サイドバー（入力エリア） ---
with st.sidebar:
    st.title("🛡️ 企業データ入力")
    
    st.markdown("### 基本情報")
    company_name = st.text_input("企業名", value="株式会社サンプル技研")
    industry = st.selectbox("業種", ["製造業", "建設業", "運輸業", "小売・卸売業", "IT・通信", "医療・福祉", "その他"])

    st.markdown("---")
    st.markdown("### 📊 財務数値 (単位:万円)")
    
    tab1, tab2 = st.tabs(["損益(P/L)", "資産(B/S)"])
    
    with tab1:
        revenue = st.number_input("売上高", value=50000, step=100)
        prev_revenue = st.number_input("前期売上", value=48000, step=100)
        operating_profit = st.number_input("営業利益", value=2500, step=10)

    with tab2:
        current_assets = st.number_input("流動資産", value=20000, step=100)
        current_liabilities = st.number_input("流動負債", value=15000, step=100)
        total_assets = st.number_input("総資産", value=40000, step=100)
        total_equity = st.number_input("純資産(自己資本)", value=18000, step=100)

    st.markdown("---")
    analyze_btn = st.button("AI分析を実行する", type="primary", use_container_width=True)

# --- 5. メイン画面（チャットエリア） ---
st.title("🛡️ 経営コンサルティング・レポート")
st.caption(f"Target: {company_name} 様 （業種: {industry}）")

# 履歴の表示
for message in st.session_state.messages:
    avatar = "🛡️" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        # AIの回答かつ、区切り文字が含まれている場合はカード表示
        if message["role"] == "assistant" and "---SPLIT---" in message["content"]:
            display_as_cards(message["content"])
        else:
            st.markdown(message["content"])

# 分析実行時の処理
if analyze_btn:
    # ユーザーのアクションを表示
    user_text = f"【分析リクエスト】\n企業名: {company_name}\n売上: {revenue:,
