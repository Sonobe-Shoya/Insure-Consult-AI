import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="診断モード", page_icon="🔧")
st.title("🔧 接続テスト・診断モード")

# 1. APIキーの読み込み
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # キーの末尾4文字だけ表示して確認
    masked_key = "..." + api_key[-4:] if api_key else "なし"
    st.write(f"🔑 読み込んだAPIキー: `{masked_key}`")
except Exception as e:
    st.error("APIキーの設定が読み込めませんでした。")
    st.stop()

st.divider()

# 2. 使えるモデルを問い合わせる
st.subheader("📋 Googleサーバーからの回答")
st.info("利用可能なモデルリストを取得しています...")

try:
    # サーバーにあるモデル一覧を全取得
    models = list(genai.list_models())
    
    # Gemini系のモデルだけを抜き出す
    gemini_models = [m for m in models if "gemini" in m.name]

    if not gemini_models:
        st.error("❌ APIキーは通りましたが、使えるモデルが1つもありませんでした。")
        st.warning("原因：このプロジェクト(Default Gemini Project)は、外部API利用が無効になっている可能性があります。")
    else:
        st.success(f"✅ 成功！ {len(gemini_models)} 個のモデルが見つかりました。")
        st.markdown("以下のコードを使えば、確実に動きます。コピーして控えてください：")
        
        # 一番新しいモデルを推奨として表示
        best_model = gemini_models[0].name.replace("models/", "")
        st.code(f"model = genai.GenerativeModel('{best_model}')", language="python")

        st.markdown("---")
        st.write("▼ 見つかった全モデルリスト")
        for m in gemini_models:
            st.text(f"- {m.name}")

except Exception as e:
    st.error("❌ 接続エラーが発生しました")
    st.error(f"エラー詳細: {e}")
    st.warning("ヒント: APIキー自体が無効か、プロジェクトの課金設定/API設定に問題がある可能性があります。")
