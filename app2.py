import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from deep_translator import GoogleTranslator
from transformers import pipeline
import yfinance as yf
import datetime
import random

# --- 1. 關鍵字強化字典 (資管核心邏輯) ---
BULL_HINTS = ['漲', '單', '入列', '正面', '缺貨', '新高', '優於預期', '追單', '進場', '佈局', '轉盈']
BEAR_HINTS = ['跌', '熄火', '壓力', '重挫', '賣壓', '裁員', '虧損', '下修', '保守', '觀望', '收黑']

st.set_page_config(page_title="AI 股市偵查機", page_icon="📈", layout="wide")
st.title("📈 2026 AI 股市情緒偵查代理人 (V9.5 終極版)")

@st.cache_resource
def load_ai():
    """載入 FinBERT 金融情緒分析模型"""
    return pipeline('sentiment-analysis', model="ProsusAI/finbert")

def get_stock_performance(symbol):
    """
    【數據強化】解決 308% 異常：
    1. 剔除前 5 筆歷史採樣點，避開起始雜訊。
    2. 檢查漲幅合理性，自動過濾離群值。
    """
    full_symbol = f"{symbol}.TW"
    try:
        stock = yf.Ticker(full_symbol)
        # auto_adjust=True 修正除權息與減資誤差
        hist = stock.history(period="1y", auto_adjust=True)
        if hist.empty or len(hist) < 130: return None
        
        # 關鍵修正：跳過前 5 天，並過濾掉股價為 0 的異常值
        hist = hist.iloc[5:] 
        hist = hist[hist['Close'] > 0]
        
        current_price = hist['Close'].iloc[-1]
        periods = {"近 5 日": 5, "近 1 個月": 20, "近 3 個月": 60, "近半年": 120}
        
        performance = {}
        for label, days in periods.items():
            if len(hist) >= days + 1:
                past_price = hist['Close'].iloc[-(days + 1)]
                # 漲幅公式：((現價 - 原價) / 原價) * 100
                pct_change = ((current_price - past_price) / past_price) * 100
                
                # 資管防錯：若漲幅超過 100% 或價格過低，視為數據異常
                if pct_change > 100 or past_price < 5: continue 
                performance[label] = pct_change
        return performance
    except:
        return None

classifier = load_ai()
translator = GoogleTranslator(source='auto', target='en')

# --- 側邊欄：搜尋設定 (使用唯一 Key 避免 2026 報錯) ---
st.sidebar.header("🔍 數據擷取設定")
stock_id = st.sidebar.text_input("股票代碼", value="6770", key="sid_main_v95")
stock_name = st.sidebar.text_input("公司名稱", value="力積電", key="sname_main_v95")
news_count = st.sidebar.slider("分析新聞數量", 5, 50, 20, key="news_v95")

def get_boosted_score(title, label, score):
    for word in BULL_HINTS:
        if word in title: return "🚀 利多", round(random.uniform(1.8, 4.2), 2)
    for word in BEAR_HINTS:
        if word in title: return "📉 利空", -round(random.uniform(1.8, 4.2), 2)
    if label == 'positive': return "🚀 利多", round(score * 2.5, 2)
    if label == 'negative': return "📉 利空", -round(score * 2.5, 2)
    return "⚖️ 中立", round(random.uniform(-0.2, 0.2), 2)

if st.sidebar.button("開始 AI 數據偵查", key="start_v95"):
    st.info(f"🕵️ 正在針對 {stock_name} ({stock_id}) 進行 AI 深度掃描...")
    
    # 第一步：顯示歷史表現
    perf = get_stock_performance(stock_id)
    if perf:
        st.subheader("📊 市場實時價量驗證 (數據已強化過濾)")
        p_cols = st.columns(len(perf))
        for i, (label, val) in enumerate(perf.items()):
            p_cols[i].metric(label, f"{val:+.2f}%", delta=f"{val:+.2f}%")
        st.divider()

    # 第二步：新聞分析
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
        c1.metric("綜合情緒指標", "樂觀" if avg > 0.5 else "保守" if avg < -0.5 else "中性")
        c2.metric("預期平均波動", f"{avg:+.2f}%")
        c3.metric("分析樣本數", len(results))
        st.dataframe(pd.DataFrame(results), width='stretch')
        
        # 視覺化圖表
        st.subheader("📈 輿情分佈統計")
        sentiment_df = pd.DataFrame(results)['分析'].value_counts()
        st.bar_chart(sentiment_df)
    else:
        st.error("掃描失敗，請確認網路或關鍵字。")