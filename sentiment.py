import pandas as pd
from GoogleNews import GoogleNews
from deep_translator import GoogleTranslator
from transformers import pipeline

# 1. 初始化 AI 大腦與翻譯官
print("正在啟動雲端 AI 引擎 (FinBERT) 與翻譯模組...")
# 這些權重會在雲端下載，不佔用你的實體硬體空間
classifier = pipeline('sentiment-analysis', model="ProsusAI/finbert")
translator = GoogleTranslator(source='auto', target='en')

def start_ai_agent(stock_name):
    # --- 第一階段：透過 GoogleNews 搜尋即時新聞 ---
    print(f"\n--- 正在連線 Google 新聞搜尋：{stock_name} ---")
    googlenews = GoogleNews(lang='zh-TW', region='TW')
    googlenews.search(stock_name)
    
    # 獲取前 5 則最新結果
    news_items = googlenews.results()[:5]
    
    if not news_items:
        print("⚠️ 無法獲取即時新聞。可能是雲端 IP 受限，我們載入備用範例進行測試。")
        news_items = [
            {'title': f"{stock_name} 拿下 NVIDIA 大訂單，營收預期大幅成長"},
            {'title': f"市場擔憂科技股估值過高，{stock_name} 面臨賣壓"}
        ]
    else:
        print(f"✅ 成功找到 {len(news_items)} 則新聞！開始深度推理...")

    results_data = []

    # --- 第二階段：翻譯與 AI 情緒推理 ---
    for i, item in enumerate(news_items):
        original_title = item.get('title', '無標題')
        
        try:
            # 翻譯成英文以利財經模型判斷
            translated_title = translator.translate(original_title)
            
            # AI 推理 (FinBERT)
            inference = classifier(translated_title)[0]
            label = inference['label']
            score = inference['score']
            
            # 視覺化標籤
            emoji = "🚀 利多 (Positive)" if label == 'positive' else "📉 利空 (Negative)" if label == 'negative' else "⚖️ 中立 (Neutral)"
            
            print(f"📰 新聞 {i+1}：{original_title}")
            print(f"🤖 AI 推理：{emoji} (信心：{score:.2%})")
            print("-" * 50)
            
            results_data.append({
                "搜尋標的": stock_name,
                "中文標題": original_title,
                "英文翻譯": translated_title,
                "AI 判斷": emoji,
                "信心指數": f"{score:.2%}"
            })
        except Exception as e:
            continue

    # --- 第三階段：資管專業資料存檔 (Excel) ---
    if results_data:
        df = pd.DataFrame(results_data)
        file_name = f"{stock_name}_AI分析報告.xlsx"
        df.to_excel(file_name, index=False)
        print(f"💾 任務完成！報告已存檔至：{file_name}")

if __name__ == "__main__":
    # 你可以輸入「2308」、「台達電」或「力積電」
    target_stock = "台達電" 
    start_ai_agent(target_stock)