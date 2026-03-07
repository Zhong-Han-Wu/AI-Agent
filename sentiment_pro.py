import pandas as pd
from GoogleNews import GoogleNews
from deep_translator import GoogleTranslator
from transformers import pipeline

# 1. 初始化
print("正在啟動 V3 專業偵查引擎 (具備模糊字眼偵測能力)...")
classifier = pipeline('sentiment-analysis', model="ProsusAI/finbert")
translator = GoogleTranslator(source='auto', target='en')

# 2. 強化版台股情緒字典 (更細碎、更敏感)
BULL_HINTS = ['漲', '單', '入列', '正面', '缺貨', '新高', '優於預期', '追單', '進場', '佈局']
BEAR_HINTS = ['跌', '熄火', '壓力', '重挫', '賣壓', '裁員', '虧損', '下修', '保守', '觀望']

def super_boost(title, original_label, original_score):
    """V3 強制表態邏輯：只要有關鍵字，就打破中立陷阱"""
    # 優先掃描利多
    for word in BULL_HINTS:
        if word in title:
            return "🚀 利多 (偵測到標題亮點)", 0.98
    # 掃描利空
    for word in BEAR_HINTS:
        if word in title:
            return "📉 利空 (偵測到負面警訊)", 0.98
    
    # 若都沒有，維持 AI 原判
    emoji = "🚀 利多" if original_label == 'positive' else "📉 利空" if original_label == 'negative' else "⚖️ 中立"
    return emoji, original_score

def run_v3_agent(stock_name):
    print(f"\n--- 正在深度連線：{stock_name} ---")
    googlenews = GoogleNews(lang='zh-TW', region='TW')
    googlenews.search(stock_name)
    news_items = googlenews.results()[:5]
    
    if not news_items:
        print("⚠️ 抓不到新聞。")
        return

    results = []
    
    for i, item in enumerate(news_items):
        title = item.get('title', '無標題')
        try:
            # 翻譯與初步推理
            translated = translator.translate(title)
            inference = classifier(translated)[0]
            
            # --- 核心優化：V3 強制表態 ---
            label, score = super_boost(title, inference['label'], inference['score'])
            
            print(f"📰 新聞 {i+1}：{title}")
            print(f"🧠 V3 推理結果：{label}")
            print("-" * 50)
            
            results.append({"標題": title, "分析": label, "分數": score})
        except:
            continue

    if results:
        # 計算統計 (排除中立後的方向)
        pos = sum(1 for r in results if "利多" in r["分析"])
        neg = sum(1 for r in results if "利空" in r["分析"])
        
        print("\n💡 --- 最終投資指南 ---")
        if pos > neg:
            print("🌟 建議：情緒指標偏向樂觀，市場正釋放正面訊號。")
        elif neg > pos:
            print("⚠️ 建議：情緒指標轉弱，建議保持高度戒備。")
        else:
            print("⚖️ 建議：訊號不明顯，適合維持中性策略。")
            
        pd.DataFrame(results).to_excel(f"{stock_name}_V3報告.xlsx", index=False)
        print(f"\n💾 V3 報告已存檔至 Excel。")

if __name__ == "__main__":
    run_v3_agent("6770") # 再次挑戰力積電