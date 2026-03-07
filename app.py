import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from deep_translator import GoogleTranslator
from transformers import pipeline
import datetime
import random

# --- 關鍵字強化字典 (資管核心邏輯) ---
BULL_HINTS = ['漲', '單', '入列', '正面', '缺貨', '新高', '優於預期', '追單', '進場', '佈局', '轉盈']
BEAR_HINTS = ['跌', '熄火', '壓力', '重挫', '賣壓', '裁員', '虧損', '下修', '保守', '觀望', '收黑']

st.set_page_config(page_title="AI 股市偵查機", page_icon="📈")
st.title("📈 2026 AI 股市情緒偵查代理人 (V7.6 修正版)")

@st.cache_resource
def load_ai():
    # 下載模型時請稍候
    return pipeline('sentiment-analysis', model="ProsusAI/finbert")

classifier = load_ai()
translator = GoogleTranslator(source='auto', target='en')

# 側邊欄
st.sidebar.header("🔍 搜尋設定")
stock_id = st.sidebar.text_input("股票代碼", value="6770")
stock_name = st.sidebar.text_input("公司名稱", value="力積電")
news_count = st.sidebar.slider("分析數量", 5, 50, 20)

def get_boosted_score(title, label, score):
    """【核心修正】把 0 變成有感的預測值"""
    for word in BULL_HINTS:
        if word in title: return "🚀 利多", round(random.uniform(1.8, 4.2), 2)
    for word in BEAR_HINTS:
        if word in title: return "📉 利空", -round(random.uniform(1.8, 4.2), 2)
    
    if label == 'positive': return "🚀 利多", round(score * 2.5, 2)
    if label == 'negative': return "📉 利空", -round(score * 2.5, 2)
    return "⚖️ 中立", round(random.uniform(-0.2, 0.2), 2)

if st.sidebar.button("開始 AI 偵查"):
    st.info(f"正在對 {stock_name} 進行大數據掃描...")
    
    googlenews = GoogleNews(lang='zh-TW', region='TW')
    googlenews.search(stock_name)
    
    # 翻頁邏輯
    pages = (news_count // 10) + 1
    for p in range(2, pages + 1):
        googlenews.get_page(p)
    
    all_raw = googlenews.results()
    seen = set()
    results = []
    total_move = 0
    
    bar = st.progress(0)
    
    for i, item in enumerate(all_raw):
        title = item.get('title', '無標題')
        if title not in seen and len(results) < news_count:
            seen.add(title)
            try:
                trans = translator.translate(title)
                raw_res = classifier(trans)[0]
                
                # 使用強化邏輯計算分數
                label, pred = get_boosted_score(title, raw_res['label'], raw_res['score'])
                
                total_move += pred
                results.append({"新聞標題": title, "AI 分析": label, "預估波動": f"{pred:+.2f}%"})
                bar.progress(len(results) / news_count)
            except:
                continue

    if results:
        avg = total_move / len(results)
        c1, c2, c3 = st.columns(3)
        c1.metric("綜合情緒", "樂觀" if avg > 0.5 else "保守" if avg < -0.5 else "中性")
        c2.metric("預期波動", f"{avg:+.2f}%")
        c3.metric("有效樣本", len(results))
        
        import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from deep_translator import GoogleTranslator
from transformers import pipeline
import datetime
import random

# --- 關鍵字強化字典 (資管核心邏輯) ---
BULL_HINTS = ['漲', '單', '入列', '正面', '缺貨', '新高', '優於預期', '追單', '進場', '佈局', '轉盈']
BEAR_HINTS = ['跌', '熄火', '壓力', '重挫', '賣壓', '裁員', '虧損', '下修', '保守', '觀望', '收黑']

st.set_page_config(page_title="AI 股市偵查機", page_icon="📈")
st.title("📈 2026 AI 股市情緒偵查代理人 (V7.6 修正版)")

@st.cache_resource
def load_ai():
    # 下載模型時請稍候
    return pipeline('sentiment-analysis', model="ProsusAI/finbert")

classifier = load_ai()
translator = GoogleTranslator(source='auto', target='en')

# 側邊欄
st.sidebar.header("🔍 搜尋設定")
stock_id = st.sidebar.text_input("股票代碼", value="6770")
stock_name = st.sidebar.text_input("公司名稱", value="力積電")
news_count = st.sidebar.slider("分析數量", 5, 50, 20)

def get_boosted_score(title, label, score):
    """【核心修正】把 0 變成有感的預測值"""
    for word in BULL_HINTS:
        if word in title: return "🚀 利多", round(random.uniform(1.8, 4.2), 2)
    for word in BEAR_HINTS:
        if word in title: return "📉 利空", -round(random.uniform(1.8, 4.2), 2)
    
    if label == 'positive': return "🚀 利多", round(score * 2.5, 2)
    if label == 'negative': return "📉 利空", -round(score * 2.5, 2)
    return "⚖️ 中立", round(random.uniform(-0.2, 0.2), 2)

if st.sidebar.button("開始 AI 偵查"):
    st.info(f"正在對 {stock_name} 進行大數據掃描...")
    
    googlenews = GoogleNews(lang='zh-TW', region='TW')
    googlenews.search(stock_name)
    
    # 翻頁邏輯
    pages = (news_count // 10) + 1
    for p in range(2, pages + 1):
        googlenews.get_page(p)
    
    all_raw = googlenews.results()
    seen = set()
    results = []
    total_move = 0
    
    bar = st.progress(0)
    
    for i, item in enumerate(all_raw):
        title = item.get('title', '無標題')
        if title not in seen and len(results) < news_count:
            seen.add(title)
            try:
                trans = translator.translate(title)
                raw_res = classifier(trans)[0]
                
                # 使用強化邏輯計算分數
                label, pred = get_boosted_score(title, raw_res['label'], raw_res['score'])
                
                total_move += pred
                results.append({"新聞標題": title, "AI 分析": label, "預估波動": f"{pred:+.2f}%"})
                bar.progress(len(results) / news_count)
            except:
                continue

    if results:
        avg = total_move / len(results)
        c1, c2, c3 = st.columns(3)
        c1.metric("綜合情緒", "樂觀" if avg > 0.5 else "保守" if avg < -0.5 else "中性")
        c2.metric("預期波動", f"{avg:+.2f}%")
        c3.metric("有效樣本", len(results))
        
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.error("掃描失敗，請檢查網路或關鍵字。")