import streamlit as st
import google.generativeai as genai

# --- 1. アプリの基本設定 ---
st.set_page_config(
    page_title="経営分析AI for Nisshin Fire",
    page_icon="🛡️",
    layout="wide"
)

# カスタムCSSでデザインを調整（カードの見た目を良くする）
st.markdown("""
<style>
    .stContainer {
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

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
        {"role": "assistant", "content": "こんにちは。日新火災のリスクコンサルタントAIです。\n左側のサイドバーに企業データを入力し、分析を開始してください。"}
    ]

# --- ヘルパー関数: テキストをカード形式で表示する ---
def display_as_cards(text):
    # 区切り文字で分割
    parts = text.split("---SPLIT---")
    
    if len(parts) >= 3:
        # 1. 診断サマリー（青）
        with st.container():
            st.info(f"### 📊 1. 経営診断サマリー\n\n{parts[0].strip()}")

        # 2. リスク（黄色）
        with st.container():
            st.warning(f"### ⚠️ 2. 想定される経営リスク\n\n{parts[1].strip()}")
            
        # 3. 提案（緑）
        with st.container():
            st.success(f"### 🛡️ 3. 日新火災からのソリューション提案\n\n{parts[2].strip()}")
    else:
        # 分割できなかった場合はそのまま表示
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

# --- 5. メイン画面 ---
st.title("🛡️ 経営コンサルティング・レポート")
st.caption(f"Target: {company_name} 様 （業種: {industry}）")

# チャット履歴の表示
for message in st.session_state.messages:
    avatar = "🛡️" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        if message["role"] == "assistant" and "---SPLIT---" in message["content"]:
            display_as_cards(message["content"])
        else:
            st.markdown(message["content"])

# 分析実行時の処理
if analyze_btn:
    # ユーザー入力を表示（ここがエラーの原因だったので修正しました）
    user_text = f"""【分析リクエスト】
    企業名: {company_name}
    売上: {revenue:,}万円
    利益: {operating_profit:,}万円"""
    
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_text)

    # AI分析開始
    with st.chat_message("assistant", avatar="🛡️"):
        status = st.empty()
        status.markdown("🧠 *AIコンサルタントが分析レポートを作成中...*")

        # プロンプト（カード分割用の区切り文字を指定）
        prompt = f"""
        あなたは日新火災海上保険のプロフェッショナルなリスクコンサルタントです。
        以下の財務データに基づき、3つのセクションに分けたレポートを作成してください。

        【重要：出力ルール】
        各セクションの間に必ず「---SPLIT---」という区切り文字を入れてください。

        【対象企業データ】
        企業名: {company_name} ({industry})
        売上: {revenue}万円 (前期: {prev_revenue}万円)
        利益: {operating_profit}万円
        流動資産: {current_assets}, 流動負債: {current_liabilities}
        総資産: {total_assets}, 純資産: {total_equity}

        【記述内容】
        1. 経営診断サマリー
           (タイトル不要。収益性・安全性・成長性の観点から、箇条書きで強みと課題を指摘)
        
        ---SPLIT---

        2. 想定される経営リスク
           (タイトル不要。この財務状況で起こりうる3つのリスクシナリオを具体的に)

        ---SPLIT---

        3. 日新火災からのソリューション提案
           (タイトル不要。以下の商品から最適なものを提案し、なぜ必要なのかを熱く語る)
           - ビジサポ (事業活動包括保険)
           - 労災あんしん保険
           - サイバーリスク保険
           - ビジネスプロパティ
        """

        try:
            response = model.generate_content(prompt)
            full_text = response.text
            
            # 完了したら表示を更新
            status.empty()
            display_as_cards(full_text)
            
            # 履歴に保存
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            st.error(f"分析中にエラーが発生しました: {e}")
