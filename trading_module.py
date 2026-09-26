import requests
import yfinance as yf

class TradingAssistant:

    @staticmethod
    def get_stock_price(symbol: str) -> str:
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.fast_info
            price = info.last_price
            change_pct = ((price - info.previous_close) / info.previous_close) * 100
            direction = "up" if change_pct > 0 else "down"
            return (f"{symbol.upper()} is trading at ${price:.2f}, Sir. "
                    f"It is {direction} {abs(change_pct):.2f}% from yesterday.")
        except Exception as e:
            return f"Could not fetch {symbol} data, Sir."

    @staticmethod
    def get_crypto_price(coin: str) -> str:
        coin_map = {
            "bitcoin": "bitcoin",  "btc":      "bitcoin",
            "ethereum": "ethereum","eth":      "ethereum",
            "solana":  "solana",   "sol":      "solana",
            "dogecoin":"dogecoin", "doge":     "dogecoin",
            "bnb":     "binancecoin","xrp":    "ripple",
            "cardano": "cardano",  "ada":      "cardano"
        }
        coin_id = coin_map.get(coin.lower(), coin.lower())
        try:
            url = (f"https://api.coingecko.com/api/v3/simple/price"
                   f"?ids={coin_id}&vs_currencies=usd&include_24hr_change=true")
            data = requests.get(url, timeout=5).json()
            if coin_id in data:
                price  = data[coin_id]['usd']
                change = data[coin_id].get('usd_24h_change') or 0
                direction = "up" if change > 0 else "down"
                return (f"{coin.upper()} is at ${price:,.2f}, Sir. "
                        f"{direction} {abs(change):.2f}% in the last 24 hours.")
            return f"Could not find {coin} price data, Sir."
        except Exception:
            return f"Crypto data unavailable right now, Sir."

    @staticmethod
    def get_market_summary() -> str:
        indices = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Dow Jones": "^DJI"}
        summary = "Global market summary, Sir. "
        try:
            for name, symbol in indices.items():
                info = yf.Ticker(symbol).fast_info
                pct  = ((info.last_price - info.previous_close) / info.previous_close) * 100
                direction = "up" if pct > 0 else "down"
                summary += f"{name} is {direction} {abs(pct):.1f}%. "
            return summary
        except Exception:
            return "Global market data unavailable, Sir."

    @staticmethod
    def get_indian_market() -> str:
        indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN"}
        summary = "Indian market update, Sir. "
        try:
            for name, symbol in indices.items():
                info = yf.Ticker(symbol).fast_info
                pct  = ((info.last_price - info.previous_close) / info.previous_close) * 100
                direction = "up" if pct > 0 else "down"
                summary += f"{name} is {direction} {abs(pct):.1f}% at {info.last_price:,.0f}. "
            return summary
        except Exception:
            return "Indian market data unavailable, Sir."

    @staticmethod
    def get_top_crypto() -> str:
        try:
            url = ("https://api.coingecko.com/api/v3/coins/markets"
                   "?vs_currency=usd&order=market_cap_desc&per_page=5&page=1")
            coins = requests.get(url, timeout=5).json()
            result = "Top 5 cryptocurrencies by market cap, Sir. "
            for c in coins:
                change = c.get('price_change_percentage_24h') or 0
                direction = "up" if change > 0 else "down"
                result += (f"{c['name']} at ${c['current_price']:,.2f}, "
                           f"{direction} {abs(change):.1f}%. ")
            return result
        except Exception:
            return "Crypto rankings unavailable, Sir."