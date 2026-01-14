import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import re

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
    .main { background-color: #f4f6f9; }
    h1, h2, h3, h4 { font-family: 'Helvetica Neue', Arial, sans-serif; color: #2c3e50; }
    
    /* スコアカードのデザイン */
    .score-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center; height: 100%;
    }
    .score-title { font-size: 1.1rem; font-weight: 600; color: #555; margin-bottom: 8px; }
    .score-value { font-size: 3.2rem; font-weight: 800; margin: 5px 0; }
    .color-profit { color: #2962FF; } .color-safety { color: #00C853; } .color-growth { color: #FF6D00; }

    /* 分析セクションの見出し */
    .section-header {
        margin-top: 30px; margin-bottom: 15px; padding-left: 15px; border-left: 5px solid #1E88E5;
        font-size: 1.5rem; font-weight: bold;
    }

    /* 詳細分析カード */
    .analysis-card {
        background-color: white; border-radius: 10px; padding: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-top: 3px solid #2962FF;
    }

    /* 経営課題カード（重要） */
    .issue-card-container { display: flex; flex-wrap: wrap; gap: 20px; }
    .issue-card {
        flex: 1 1 300px; /* 横並び、狭くなると折り返し */
        background-color: #fff5f5; border-radius: 10px; padding: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); border-left: 5px solid #e53935;
    }
    .issue-title { font-weight: bold; font-size: 1.2rem; color: #c62828; margin-bottom: 10px; display: flex; align-items: center;}
    .issue-title::before { content: "⚠️"; margin-right: 10px; }

    /* 提案カード */
    .proposal-card {
        background-color: #e8f5e9; border-radius: 10px; padding: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 2px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# APIキー設定
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    try: model = genai.GenerativeModel('gemini-2.5-flash')
    except: model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("APIキーが設定されていません。")
    st.stop()

# --- 2. 計算ロジック ---
def calculate_scores(rev, prev_rev, op_profit, assets, equity, cur_assets, cur_liab):
    op_margin = (op_profit / rev) * 100 if rev > 0 else 0
    score_profit = min(100, max(0, int(op_margin * 10))) 
    
    equity_ratio = (equity / assets) * 100 if assets > 0 else 0
    current_ratio = (cur_assets / cur_liab) * 100 if cur_liab > 0 else 0
    raw_safety = (equity_ratio * 1.5) + (current_ratio * 0.1)
    score_safety = min(100, max(0, int(raw_safety)))

    growth_rate = (rev / prev_rev) * 100 if prev_rev > 0 else 100
    score_growth = min(100, max(0, int((growth_rate - 90) * 3.5)))

    return score_profit, score_safety, score_growth, op_margin, equity_ratio, growth_rate

# --- 3. サイドバー入力 ---
with st.sidebar:
    st.title("🛡️ 企業データ入力")
    company_name = st.text_input("企業名", value="株式会社サンプル技研")
    industry = st.selectbox("業種", ["製造業", "建設業", "運輸業", "小売・卸売業", "IT・通信", "医療・福祉", "その他"])
    st.markdown("---")
    with st.expander("📊 財務数値入力", expanded=True):
        revenue = st.number_input("売上高 (万円)", value=52000, step=100)
        prev_revenue = st.number_input("前期売上 (万円)", value=48000, step=100)
        operating_profit = st.number_input("営業利益 (万円)", value=3500, step=10)
        current_assets = st.number_input("流動資産 (万円)", value=25000, step=100)
        current_liabilities = st.number_input("流動負債 (万円)", value=20000, step=100)
        total_assets = st.number_input("総資産 (万円)", value=
