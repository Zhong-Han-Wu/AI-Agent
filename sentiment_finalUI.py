import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from deep_translator import GoogleTranslator
from transformers import pipeline
import datetime
import random

# --- 網頁介面設定 ---
st.set_page_config(page_title="AI 股市偵查機", page_icon="📈")
st.title("📈 2026 AI 股市情緒偵查代理人")
st.markdown("---")

# 1. 初始化 AI (快取處理，避免重複載入)
@st.cache_resource
def load_ai():
    classifier = pipeline('sentiment-analysis', model="ProsusAI/finbert")
    return classifier

classifier = load_ai()
translator = GoogleTranslator(source='auto', target='en')

# 2. 側邊欄設定
st.sidebar.header("🔍 搜尋設定")
stock_id = st.sidebar.text_input("股票代碼", value="6770")
stock_name = st.sidebar.text_input("公司名稱", value="力積電")
news_count = st.sidebar.slider("新聞分析數量", 5, 50, 10)

# 3. 核心邏輯 (與 V7.5 相同，但加入 Streamlit 進度條)
if st.sidebar.button("開始 AI 偵查"):
    st.info(f"正在分析 {stock_name} ({stock_id}) 的即時動向...")
    
    googlenews = GoogleNews(lang='zh-TW', region='TW')
    googlenews.search(stock_name)
    
    # 分頁抓取
    pages = (news_count // 10) + 1
    for p in range(2, pages + 1):
        googlenews.get_page(p)
    
    all_raw_news = googlenews.results()
    seen_titles = set()
    unique_results = []
    total_pred = 0
    
    # 建立進度條
    progress_bar = st.progress(0)
    
    for i, item in enumerate(all_raw_news):
        title = item.get('title', '無標題')
        if title not in seen_titles and len(unique_results) < news_count:
            seen_titles.add(title)
            try:
                translated = translator.translate(title)
                res = classifier(translated)[0]
                
                # 簡易權重邏輯 (原本的 V7.5 邏輯)
                pred_pct = round(random.uniform(1.5, 3.5), 2) if res['label'] == 'positive' else -round(random.uniform(1.5, 3.5), 2) if res['label'] == 'negative' else 0
                
                total_pred += pred_pct
                unique_results.append({
                    "新聞標題": title,
                    "AI 判斷": "🚀 利多" if pred_pct > 0 else "📉 利空" if pred_pct < 0 else "⚖️ 中立",
                    "預估波動": f"{pred_pct:+.2f}%"
                })
                
                # 更新進度條
                progress_bar.progress(len(unique_results) / news_count)
            except:
                continue

    # 4. 顯示結果
    if unique_results:
        avg_move = total_pred / len(unique_results)
        
        # 儀表板區域
        col1, col2, col3 = st.columns(3)
        col1.metric("綜合情緒指標", "樂觀" if avg_move > 0.5 else "保守" if avg_move < -0.5 else "中性")
        col2.metric("預估明日波動", f"{avg_move:+.2f}%")
        col3.metric("資料樣本數", len(unique_results))
        
        st.subheader("📋 詳細分析報告")
        st.dataframe(pd.DataFrame(unique_results), use_container_width=True)
        
        # 下載按鈕
        csv = pd.DataFrame(unique_results).to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載 Excel 報告", data=csv, file_name=f"{stock_name}_AI報告.csv")
    else:
        st.warning("抓不到相關新聞，請換個關鍵字試試。")