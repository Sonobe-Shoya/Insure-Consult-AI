import streamlit as st
import google.generativeai as genai
import re

# Plotlyの読み込み（エラー回避用）
try:
    import plotly.graph_objects as go
    plotly_available = True
except ImportError:
    plotly_available = False

# --- 1. アプリ設定とCSSデザイン ---
st.set_page_config(
    page_title="経営分析AI for Nisshin Fire",
    page_icon="🛡️",
    layout="wide"
)

# プロフェッショナルなレポート風デザインにするCSS
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { font-family: 'Helvetica Neue', Arial, sans-serif; color: #333; }
    
    /* 3大指標カード（スコア＋解説） */
    .metric-card {
        background-color: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        height: 100%;
        border-top: 5px solid #ccc;
    }
    .card-blue { border-top-color: #2962FF; }
    .card-green { border-top-color: #00C853; }
    .card-orange { border-top-color: #FF6D00; }
    
    .metric-header { display: flex; align-items: center; margin-bottom: 15px; }
    .metric-icon { font-size: 1.5rem; margin-right: 10px; padding: 10px; border-radius: 10px; color: white; }
    .icon-blue { background-color: #2962FF; }
    .icon-green { background-color: #00C853; }
    .icon-orange { background-color: #FF6D00; }
    
    .metric-title { font-weight: bold; font-size: 1.1rem; color: #555; }
    
    .metric-score { font-size: 3.5rem; font-weight: 800; line-height: 1; margin-bottom: 10px; }
    .metric-score span { font-size: 1rem; color: #999; font-weight: normal; }
    .text-blue { color: #2962FF; }
    .text-green { color: #00C853; }
    .text-orange { color: #FF6D00; }
    
    .metric-desc { font-size: 0.9rem; color: #666; line-height: 1.6; margin-top: 15px; text-align: left; }

    /* 経営課題カード */
    .issue-card {
        background-color: white; border-radius: 10px; padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-left: 5px solid #FF5252;
    }
    .issue-title { font-weight: bold; font-size: 1.1rem; color: #D32F2F; margin-bottom: 8px; display: flex; align-items: center; }

    /* 提案カード */
    .proposal-card {
        background-color: #E8F5E9; border: 1px solid #C8E6C9; border-radius: 10px; padding: 20px; margin-bottom: 15px;
    }
    .proposal-title { color: #2E7D32; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# APIキー設定
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    try: model = genai.GenerativeModel('gemini-2.5-flash')
    except: model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("APIキーの設定が必要です。")
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

# --- 3. サイドバー
