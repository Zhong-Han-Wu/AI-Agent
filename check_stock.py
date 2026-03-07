import yfinance as yf
target = "2308.TW"
def fetch_stock_info(symbol):
    stock=yf.Ticker(symbol)
    price=stock.history(period="1d")['Close'].iloc[-1]
    print(f"--- 雲端運行成功 ---")
    print(f"台達電 (2308) 當前股價預估: {price:.2f} TWD")
    print(f"提示：這段運算完全是在 GitHub 伺服器執行的，沒用到你筆電的 CPU！")
if __name__ == "__main__":
    fetch_stock_info(target)