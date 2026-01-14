import streamlit as st
import google.generativeai as genai

# --- 1. アプリの基本設定 ---
st.set_page_config(
    page_title="経営分析AI for Nisshin Fire",
    page_icon="🛡️",
    layout="wide"
)

# APIキーの設定（エラーハンドリング付き）
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("APIキーが設定されていません。")
    st.stop()

# --- 2. AIモデルの指定（ここが修正ポイント） ---
# Default Projectのキーでも確実に動く「gemini-pro」を使用します
model = genai.GenerativeModel('gemini-pro')

# --- 3. サイドバー（入力エリア） ---
with st.sidebar:
    st.title("🛡️ 企業データ入力")
    
    st.markdown("### 基本情報")
    company_name = st.text_input("企業名", value="株式会社サンプル技研")
    industry = st.selectbox("業種", ["製造業", "建設業", "運輸業", "小売・卸売業", "IT・通信", "医療・福祉", "その他"])

    st.markdown("---")
    st.markdown("### 📊 財務数値 (単位:万円)")
    
    # タブで入力を整理
    tab1, tab2 = st.tabs(["損益(P/L)", "資産(B/S)"])
    
    with tab1:
        revenue = st.number_input("売上高", value=50000, step=100)
        prev_revenue = st.number_input("前期売上", value=48000, step=100)
        operating_profit = st.number_input("営業利益", value=2500, step=10)
        net_income = st.number_input("当期純利益", value=1500, step=10)

    with tab2:
        current_assets = st.number_input("流動資産", value=20000, step=100)
        current_liabilities = st.number_input("流動負債", value=15000, step=100)
        total_assets = st.number_input("総資産", value=40000, step=100)
        total_equity = st.number_input("純資産(自己資本)", value=18000, step=100)

    st.markdown("---")
    analyze_btn = st.button("AI分析を実行する", type="primary", use_container_width=True)

# --- 4. メイン画面（出力エリア） ---
st.title("経営コンサルティング・レポート")
st.markdown(f"**Target:** {company_name} 様 （業種: {industry}）")

# 財務指標の計算と表示
if revenue > 0 and total_assets > 0 and current_liabilities > 0:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("売上高", f"{revenue:,}万円", f"{revenue - prev_revenue:,}万円")
    col2.metric("営業利益率", f"{operating_profit/revenue*100:.1f}%")
    col3.metric("自己資本比率", f"{total_equity/total_assets*100:.1f}%")
    col4.metric("流動比率", f"{current_assets/current_liabilities*100:.1f}%")
st.divider()

# --- 5. AI分析の実行 ---
if analyze_btn:
    with st.spinner("AIコンサルタントが分析中...（約10〜20秒お待ちください）"):
        
        # プロンプト（AIへの命令書）
        prompt = f"""
        あなたは日新火災海上保険のプロフェッショナルなリスクコンサルタントです。
        以下の財務データに基づき、経営者向けの説得力あるレポートを作成してください。
        
        【対象企業データ】
        - 企業名: {company_name} ({industry})
        - 売上高: {revenue}万円 (前期: {prev_revenue}万円)
        - 営業利益: {operating_profit}万円
        - 流動資産: {current_assets}万円
        - 流動負債: {current_liabilities}万円
        - 総資産: {total_assets}万円
        - 純資産: {total_equity}万円

        【出力構成】
        Markdown形式で見やすく出力してください。

        ## 1. 経営診断サマリー
        収益性・安全性・成長性の観点から、現状の強みと課題を簡潔にまとめてください。

        ## 2. 想定される経営リスク
        この財務状況において起こりうる具体的なリスクシナリオを3つ挙げてください。
        (例: 資金繰りの悪化、災害時の操業停止リスク、賠償責任など)

        ## 3. 日新火災からのソリューション提案
        上記のリスクに対応する、以下の保険商品を提案してください。
        提案の際は、「なぜこの会社に今必要なのか」を財務数値と絡めて説明してください。

        - **ビジサポ (事業活動包括保険)**: 賠償リスクや休業損害への備え
        - **労災あんしん保険**: 従業員の怪我や使用者賠償責任への備え
        - **サイバーリスク保険**: 情報漏洩やサイバー攻撃への備え
        - **ビジネスプロパティ**: 建物・設備の損害への備え
        """

        try:
            # AIに回答を生成させる
            response = model.generate_content(prompt)
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.info("※Default Projectのキーを使用しているため、gemini-proモデルで再試行しました。")

else:
    st.info("👈 左側のサイドバーに数値を入力し、「AI分析を実行する」ボタンを押してください。")
