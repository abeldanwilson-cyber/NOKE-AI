import time
import threading
from datetime import datetime
from trading_module import TradingAssistant
from web_module import WebEngine
from pc_guardian import PCGuardian
import ollama

class DailyReporter:
    """Generates an AI-summarized daily briefing."""

    _monitor_thread = None
    _monitoring = False
    _speak_fn = None
    _report_time = "21:00" # Default 9:00 PM

    @staticmethod
    def set_report_time(time_str: str):
        """Format: HH:MM in 24-hour time."""
        DailyReporter._report_time = time_str.strip()
        return f"Daily report scheduled for {time_str}, Sir."

    @staticmethod
    def generate_report(user_name: str) -> str:
        print("\n   [Daily Reporter] Gathering data streams...")
        
        # 1. Market Data
        try:
            market_data = TradingAssistant.get_market_summary()
            nifty = TradingAssistant.get_indian_market()
            crypto = TradingAssistant.get_top_crypto()
        except Exception:
            market_data = "Market data unavailable."
            nifty = ""
            crypto = ""

        # 2. News Data
        try:
            news_data = WebEngine.get_news("Technology")
        except Exception:
            news_data = "News unavailable."

        # 3. System Data
        try:
            pc_health = PCGuardian.health_check()
        except Exception:
            pc_health = "PC Health data unavailable."

        print("   [Daily Reporter] Engineering AI summary...")

        prompt = f"""You are NOKE, an advanced AI assistant (like JARVIS).
Generate a daily evening briefing for your boss, {user_name}.
Keep it concise, punchy, and confident (about 3-4 sentences).
Speak naturally, do not use bullet points, markdown, or lists.

DATA TO SUMMARIZE:
Market: {market_data}, {nifty}, {crypto}
News: {news_data[:500]}
System: {pc_health}
"""
        try:
            response = ollama.chat(
                model="llama3.2:3b",
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content'].strip()
        except Exception as e:
            return f"Good evening, {user_name}. I gathered the daily data but my neural link to summarize it failed. All basic systems remain online."

    @staticmethod
    def start_monitoring(speak_fn, user_name: str):
        DailyReporter._speak_fn = speak_fn
        DailyReporter._monitoring = True

        def monitor_loop():
            last_run_day = None
            while DailyReporter._monitoring:
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                current_day = now.strftime("%Y-%m-%d")

                if current_time == DailyReporter._report_time and current_day != last_run_day:
                    DailyReporter._speak_fn("Compiling your daily report, Sir. Please hold.")
                    report = DailyReporter.generate_report(user_name)
                    DailyReporter._speak_fn(report)
                    last_run_day = current_day
                
                time.sleep(30) # Check every 30 seconds

        DailyReporter._monitor_thread = threading.Thread(target=monitor_loop, daemon=True, name="DailyReporter")
        DailyReporter._monitor_thread.start()

    @staticmethod
    def stop_monitoring():
        DailyReporter._monitoring = False
