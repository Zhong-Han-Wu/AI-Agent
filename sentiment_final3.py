import pandas as pd
import yfinance as yf
from GoogleNews import GoogleNews
from deep_translator import GoogleTranslator
from transformers import pipeline
import datetime
import os

# 1. 初始化 AI (雲端運算)
print("🚀 正在啟動 V7 終極回測版 AI 引擎...")
classifier = pipeline('sentiment-analysis', model="ProsusAI/finbert")
translator = GoogleTranslator(source='auto', target='en')

def verify_performance(stock_id, predicted_move):
    """週一對答案邏輯：抓取真實漲跌幅並計算誤差"""
    print(f"\n🔍 --- 正在進行真實數據比對 ({stock_id}) ---")
    ticker_id = f"{stock_id}.TW"
    
    # 獲取今日(或最近一個交易日)的股價
    stock = yf.Ticker(ticker_id)
    hist = stock.history(period="1d")
    
    if hist.empty:
        print("⚠️ 無法獲取今日收盤數據，可能尚未收盤或 API 延遲。")
        return
    
    # 計算實際漲跌幅: (收盤價 - 開盤價) / 開盤價
    open_p = hist['Open'].iloc[0]
    close_p = hist['Close'].iloc[0]
    actual_move = ((close_p - open_p) / open_p) * 100
    
    error = abs(actual_move - predicted_move)
    
    print(f"📈 實際開盤價：{open_p:.2f} | 實際收盤價：{close_p:.2f}")
    print(f"📊 實際漲跌幅：{actual_move:+.2f}%")
    print(f"🤖 AI 預測值：{predicted_move:+.2f}%")
    print(f"📏 預測誤差值：{error:.2f}%")
    
    status = "🎯 精準命中" if error < 0.5 else "✅ 方向正確" if (actual_move * predicted_move) > 0 else "❌ 預測失準"
    print(f"🏆 最終評價：{status}")
    return actual_move, error, status

# (中間的 run_invest_agent 與 V6 邏輯相同，僅在最後加入 verify 呼叫)
def run_final_agent(stock_id, stock_name):
    # ... [此處省略前述 V6 搜尋與預測邏輯] ...
    # 假設最後算出 avg_move = 1.72
    avg_move = 1.72 # 此處為 V6 的計算結果
    
    # 執行對答案 (如果是週一收盤後跑，就會有真實數據)
    verify_performance(stock_id, avg_move)

if __name__ == "__main__":
    # 使用力積電代碼進行驗證
    run_final_agent("6770", "力積電")