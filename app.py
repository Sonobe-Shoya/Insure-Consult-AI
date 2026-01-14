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
# 診断で見つかった最強モデルを指定（そのまま維持）
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    model = genai.GenerativeModel('gemini-flash-latest')

# --- 3. セッション状態の初期化（チャット履歴用） ---
# これがチャット形式を実現する鍵です
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは。日新火災のリスクコンサルタントAIです。\n左側のサイドバーに企業の財務データを入力し、「分析を実行」ボタンを押してください。最適なリスク対策をご提案します。"}
    ]

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
    # ボタンが押されたかどうかのフラグ
    analyze_pressed = st.button("AI分析を実行する", type="primary", use_container_width=True)

# --- 5. メイン画面（チャットエリア） ---
st.title("🛡️ 経営コンサルティング・チャット")
st.caption(f"Target: {company_name} 様 （業種: {industry}）")

# ▼▼▼ ここがデザイン変更の核心部分 ▼▼▼

# 保存されているチャット履歴を順番に表示する
for message in st.session_state.messages:
    # roleが'assistant'ならAIのアイコン、それ以外なら人型アイコン
    avatar = "🛡️" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 分析ボタンが押された時の処理
if analyze_pressed:
    # ユーザーの操作をチャット履歴に追加（今回は「分析実行」という合図として）
    # ※ユーザーの発言として表示したくない場合は、この2行をコメントアウトしてもOKです
    user_action = f"【分析リクエスト】\n企業名: {company_name}, 売上高: {revenue}万円..."
    st.session_state.messages.append({"role": "user", "content": user_action})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_action)

    # AIの思考中...を表示
    with st.chat_message("assistant", avatar="🛡️"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🧠 *データを分析し、レポートを作成しています...*")
        
        # プロンプト作成（内容は以前と同じ）
        prompt = f"""
        あなたは日新火災海上保険のプロフェッショナルなリスクコンサルタントです。
        チャット形式で、経営者に語りかけるように分かりやすく、かつ説得力のある分析結果を提示してください。
        Markdownを駆使して見やすく装飾してください。

        【対象企業データ】
        - 企業名: {company_name} ({industry})
        - 売上高: {revenue}万円 (前期: {prev_revenue}万円)
        - 営業利益: {operating_profit}万円
        - 流動資産: {current_assets}万円
        - 流動負債: {current_liabilities}万円
        - 総資産: {total_assets}万円
        - 純資産: {total_equity}万円

        【回答の構成案】
        挨拶と、財務状況の簡単なフィードバックから始めてください。

        ### 1. 経営診断サマリー（強みと課題）
        (箇条書きや太字を使って端的に)

        ### 2. 想定される重要リスク（3選）
        (具体的なシナリオと、放置した場合の危険性)

        ### 3. 日新火災からのソリューション提案
        (以下の保険から最適なものを提案し、なぜ今必要なのかを熱く語る)
        - **ビジサポ (事業活動包括保険)**
        - **労災あんしん保険**
        - **サイバーリスク保険**
        - **ビジネスプロパティ**

        最後に、経営者を勇気づける言葉で締めくくってください。
        """

        try:
            # AIに回答を生成させる
            response = model.generate_content(prompt)
            full_response = response.text
            
            # 生成された回答をチャットに表示
            message_placeholder.markdown(full_response)
            
            # 回答を履歴に保存（これでリロードしても消えない）
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_message = f"申し訳ありません、分析中にエラーが発生しました。\n\nエラー内容: {e}"
            message_placeholder.error(error_message)
            # エラーも履歴に残す場合
            # st.session_state.messages.append({"role": "assistant", "content": error_message})
