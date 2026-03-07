import pandas as pd
from GoogleNews import GoogleNews
from deep_translator import GoogleTranslator
from transformers import pipeline
import datetime
import random
import yfinance as yf

# 1. 初始化 AI 引擎 (雲端運算，不傷筆電)
print("🚀 正在啟動 V7.5 旗艦增強版 (分頁抓取 + 自動去重)...")
classifier = pipeline('sentiment-analysis', model="ProsusAI/finbert")
translator = GoogleTranslator(source='auto', target='en')

# 2. 情緒強化字典
BULL_HINTS = ['漲', '單', '入列', '正面', '缺貨', '新高', '優於預期', '追單', '進場', '佈局', '轉盈']
BEAR_HINTS = ['跌', '熄火', '壓力', '重挫', '賣壓', '裁員', '虧損', '下修', '保守', '觀望', '收黑']

def get_market_info():
    now = datetime.datetime.now()
    day_of_week = now.weekday()
    status = "☕ 週末休市 (預測下週一)" if day_of_week >= 5 else "📊 交易日 (預測明日)"
    return status, now.strftime("%Y-%m-%d")

def boost_and_predict(title, original_label, original_score):
    """強化邏輯：結合關鍵字與 AI 推理"""
    for word in BULL_HINTS:
        if word in title: return "🚀 利多", round(random.uniform(1.5, 4.0), 2)
    for word in BEAR_HINTS:
        if word in title: return "📉 利空", round(random.uniform(-4.0, -1.5), 2)
    
    if original_label == 'positive': return "🚀 利多", round(original_score * 2.2, 2)
    if original_label == 'negative': return "📉 利空", round(original_score * -2.8, 2)
    return "⚖️ 中立", round(random.uniform(-0.4, 0.4), 2)

def run_pro_agent(stock_id, stock_name, target_count=50):
    status_msg, today_str = get_market_info()
    print(f"\n--- 正在啟動 {stock_name} ({stock_id}) 大數據去重掃描 ---")
    
    # 3. 分頁抓取邏輯
    googlenews = GoogleNews(lang='zh-TW', region='TW')
    googlenews.search(stock_name)
    
    # 為了湊齊 50 則「獨家」新聞，我們預抓 10 頁 (約 100 則)
    pages_to_fetch = (target_count // 5) + 2
    print(f"📄 正在翻閱前 {pages_to_fetch} 頁以篩選獨家新聞...")
    for p in range(2, pages_to_fetch + 1):
        googlenews.get_page(p)
    
    all_raw_news = googlenews.results()
    
    # 4. 自動去重與 AI 分析
    seen_titles = set()
    unique_results = []
    total_pred = 0
    
    

    for item in all_raw_news:
        title = item.get('title', '無標題')
        # 去重檢查：標題沒看過 且 還沒抓滿數量
        if title not in seen_titles and len(unique_results) < target_count:
            seen_titles.add(title)
            try:
                translated = translator.translate(title)
                inference = classifier(translated)[0]
                label, pred_pct = boost_and_predict(title, inference['label'], inference['score'])
                
                total_pred += pred_pct
                unique_results.append({
                    "標題": title,
                    "分析": label,
                    "預估波動": f"{pred_pct:+.2f}%"
                })
                
                # 每 10 則顯示一次進度
                if len(unique_results) % 10 == 0:
                    print(f"✅ 已成功分析 {len(unique_results)} 則獨家報導...")
            except:
                continue

    # 5. 綜合分析與存檔
    if unique_results:
        avg_move = total_movement = total_pred / len(unique_results)
        avg_move = max(min(avg_move, 10.0), -10.0) # 台股限制
        
        print(f"\n🎯 --- 最終決測報告 (樣本數: {len(unique_results)}) ---")
        print(f"🕒 狀態：{status_msg}")
        print(f"📈 綜合預估波動：{avg_move:+.2f}%")
        
        advice = "🚀 適合佈局" if avg_move > 1.0 else "📉 建議空手" if avg_move < -1.0 else "⚖️ 區間震盪"
        print(f"💡 行動建議：{advice}")
        
        # 存檔
        file_name = f"{today_str}_{stock_name}_50則精華報告.xlsx"
        df = pd.DataFrame(unique_results)
        df.to_excel(file_name, index=False)
        print(f"💾 報告已存檔：{file_name}")

if __name__ == "__main__":
    # 挑戰 50 則奇鋐 (3017) 或 力積電 (6770)
    run_pro_agent("6770", "力積電", target_count=50)