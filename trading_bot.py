import os
import json
import time
import threading
from trading_module import TradingAssistant

ALERTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "noke_alerts.json")

class TradingBot:
    """Background monitor for stock and crypto prices."""

    _monitor_thread = None
    _monitoring = False
    _speak_fn = None

    @staticmethod
    def _load_alerts() -> list:
        if os.path.exists(ALERTS_FILE):
            try:
                with open(ALERTS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    @staticmethod
    def _save_alerts(alerts: list):
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)

    @staticmethod
    def add_alert(symbol: str, target_price: float, condition: str) -> str:
        """
        Add a new price alert.
        Condition must be 'above' or 'below'.
        """
        symbol = symbol.upper().strip()
        condition = condition.lower().strip()
        if condition not in ["above", "below"]:
            return "Condition must be 'above' or 'below', Sir."

        alerts = TradingBot._load_alerts()
        # Remove existing alert for the same symbol/condition
        alerts = [a for a in alerts if not (a['symbol'] == symbol and a['condition'] == condition)]
        
        alerts.append({
            "symbol": symbol,
            "target": target_price,
            "condition": condition
        })
        TradingBot._save_alerts(alerts)
        return f"Alert set, Sir. I will notify you if {symbol} goes {condition} {target_price}."

    @staticmethod
    def clear_alerts(symbol: str = None) -> str:
        if symbol:
            symbol = symbol.upper().strip()
            alerts = TradingBot._load_alerts()
            original_len = len(alerts)
            alerts = [a for a in alerts if a['symbol'] != symbol]
            TradingBot._save_alerts(alerts)
            if len(alerts) < original_len:
                return f"Cleared all alerts for {symbol}, Sir."
            return f"No active alerts found for {symbol}, Sir."
        else:
            TradingBot._save_alerts([])
            return "All trading alerts cleared, Sir."

    @staticmethod
    def list_alerts() -> str:
        alerts = TradingBot._load_alerts()
        if not alerts:
            return "You have no active trading alerts, Sir."
        
        lines = [f"{a['symbol']} {a['condition']} {a['target']}" for a in alerts]
        return f"You have {len(alerts)} active alerts: {', '.join(lines)}."

    @staticmethod
    def _fetch_price(symbol: str) -> float:
        # Determine if it's crypto or stock based on symbol length/common names
        crypto_names = {"BTC", "ETH", "SOL", "DOGE", "BITCOIN", "ETHEREUM", "SOLANA", "DOGECOIN"}
        if symbol in crypto_names:
            resp = TradingAssistant.get_crypto_price(symbol.lower())
        else:
            resp = TradingAssistant.get_stock_price(symbol)
        
        # Extremely simple parse to extract first float/int from response
        import re
        matches = re.findall(r"\$?\s*([\d,]+\.?\d*)", resp.replace(",", ""))
        if matches:
            return float(matches[0])
        return None

    @staticmethod
    def start_monitoring(speak_fn):
        TradingBot._speak_fn = speak_fn
        TradingBot._monitoring = True

        def monitor_loop():
            while TradingBot._monitoring:
                alerts = TradingBot._load_alerts()
                alerts_triggered = []

                for alert in alerts:
                    try:
                        current_price = TradingBot._fetch_price(alert['symbol'])
                        if current_price is None:
                            continue
                        
                        target = float(alert['target'])
                        if alert['condition'] == 'above' and current_price >= target:
                            TradingBot._speak_fn(f"Trading Alert, Sir! {alert['symbol']} has crossed above {target}. Current price is {current_price}.")
                            alerts_triggered.append(alert)
                        elif alert['condition'] == 'below' and current_price <= target:
                            TradingBot._speak_fn(f"Trading Alert, Sir! {alert['symbol']} has dropped below {target}. Current price is {current_price}.")
                            alerts_triggered.append(alert)
                    except Exception as e:
                        print(f"[TradingBot Error] {e}")

                if alerts_triggered:
                    # Remove triggered alerts so they don't spam
                    remaining_alerts = [a for a in alerts if a not in alerts_triggered]
                    TradingBot._save_alerts(remaining_alerts)

                time.sleep(300) # Check every 5 minutes

        TradingBot._monitor_thread = threading.Thread(target=monitor_loop, daemon=True, name="TradingBot")
        TradingBot._monitor_thread.start()

    @staticmethod
    def stop_monitoring():
        TradingBot._monitoring = False
