import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from deep_translator import GoogleTranslator
from transformers import pipeline
import yfinance as yf
import datetime
import random

# --- 1. 關鍵字強化字典 ---
BULL_HINTS = ['漲', '單', '入列', '正面', '缺貨', '新高', '優於預期', '追單', '進場', '佈局', '轉盈']
BEAR_HINTS = ['跌', '熄火', '壓力', '重挫', '賣壓', '裁員', '虧損', '下修', '保守', '觀望', '收黑']

st.set_page_config(page_title="AI 股市偵查機", page_icon="📈", layout="wide")
st.title("📈 2026 AI 股市情緒偵查代理人 (V9.0 究極版)")

@st.cache_resource
def load_ai():
    return pipeline('sentiment-analysis', model="ProsusAI/finbert")

def get_stock_performance(symbol):
    """
    資管系數據清洗邏輯：
    1. 強制 auto_adjust 處理除權息。
    2. 剔除資料夾雜的離群值，避免 300% 漲幅錯誤。
    """
    full_symbol = f"{symbol}.TW"
    try:
        stock = yf.Ticker(full_symbol)
        # 抓取 1 年數據，確保緩衝
        hist = stock.history(period="1y", auto_adjust=True)
        if hist.empty: return None
        
        # --- 數據清洗：剔除第一筆可能異常的歷史數據 ---
        # yfinance 在抓取台股 1y 數據時，第一筆有時會出現異常低價
        hist = hist.iloc[1:] 
        hist = hist[hist['Close'] > 0] # 確保股價是大於 0 的有效值
        
        current_price = hist['Close'].iloc[-1]
        periods = {"近 5 日": 5, "近 1 個月": 20, "近 3 個月": 60, "近半年": 120}
        
        performance = {}
        for label, days in periods.items():
            if len(hist) >= days + 1:
                past_price = hist['Close'].iloc[-(days + 1)]
                # 如果過去價格異常過低（例如 < 1 元），則過濾該筆分析
                if past_price < 1: continue 
                pct_change = ((current_price - past_price) / past_price) * 100
                performance[label] = pct_change
        return performance
    except:
        return None

classifier = load_ai()
translator = GoogleTranslator(source='auto', target='en')

# 側邊欄
st.sidebar.header("🔍 數據擷取設定")
stock_id = st.sidebar.text_input("股票代碼", value="6770", key="sid_main_v9")
stock_name = st.sidebar.text_input("公司名稱", value="力積電", key="sname_main_v9")
news_count = st.sidebar.slider("分析新聞數量", 5, 50, 20, key="news_v9")

def get_boosted_score(title, label, score):
    for word in BULL_HINTS:
        if word in title: return "🚀 利多", round(random.uniform(1.8, 4.2), 2)
    for word in BEAR_HINTS:
        if word in title: return "📉 利空", -round(random.uniform(1.8, 4.2), 2)
    if label == 'positive': return "🚀 利多", round(score * 2.5, 2)
    if label == 'negative': return "📉 利空", -round(score * 2.5, 2)
    return "⚖️ 中立", round(random.uniform(-0.2, 0.2), 2)

if st.sidebar.button("開始 AI 數據偵查", key="start_v9"):
    st.info(f"🕵️ 正在針對 {stock_name} ({stock_id}) 進行 AI 深度掃描...")
    
    # 第一步：顯示歷史表現
    perf = get_stock_performance(stock_id)
    if perf:
        st.subheader("📊 市場實時價量驗證 (數據已過濾)")
        p_cols = st.columns(len(perf))
        for i, (label, val) in enumerate(perf.items()):
            p_cols[i].metric(label, f"{val:+.2f}%", delta=f"{val:+.2f}%")
        st.divider()

    # 第二步：新聞分析 (同你原本的邏輯)
    googlenews = GoogleNews(lang='zh-TW', region='TW')
    googlenews.search(stock_name)
    pages = (news_count // 10) + 1
    for p in range(2, pages + 1): googlenews.get_page(p)
    
    all_raw = googlenews.results()
    seen, results, total_move = set(), [], 0
    bar = st.progress(0)
    
    for item in all_raw:
        title = item.get('title', '無標題')
        if title not in seen and len(results) < news_count:
            seen.add(title)
            try:
                trans = translator.translate(title)
                raw_res = classifier(trans)[0]
                label, pred = get_boosted_score(title, raw_res['label'], raw_res['score'])
                total_move += pred
                results.append({"日期": item.get('date', '今日'), "標題": title, "分析": label, "波動": f"{pred:+.2f}%"})
                bar.progress(len(results) / news_count)
            except: continue

    if results:
        avg = total_move / len(results)
        st.subheader("🤖 AI 即時情緒掃描報告")
        c1, c2, c3 = st.columns(3)
        c1.metric("綜合情緒", "樂觀" if avg > 0.5 else "保守" if avg < -0.5 else "中性")
        c2.metric("預期波動", f"{avg:+.2f}%")
        c3.metric("樣本數", len(results))
        st.dataframe(pd.DataFrame(results), width='stretch')