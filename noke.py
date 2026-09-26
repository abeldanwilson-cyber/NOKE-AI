import warnings
warnings.filterwarnings("ignore")

import os, io, wave, json, re, random
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import requests
import pyttsx3
import ollama
from datetime import datetime
from bs4 import BeautifulSoup

# ── Modular Subsystems ──────────────────────────
from system_control  import SystemController
from trading_module  import TradingAssistant
from security_module import SecurityAssistant
from coder_module    import SkillForge
from web_module      import WebEngine
from security_guard  import SecurityGuard
from pc_guardian     import PCGuardian
from resolver        import SelfSolver
from trading_bot     import TradingBot
from automation_module import AutomationEngine
from daily_report    import DailyReporter

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# ===============================================
#  VOICE ENGINE
# ===============================================
import threading

_speak_lock = threading.Lock()

def speak(text: str, rate: int = 190):
    print(f"\n[NOKE]: {text}")
    with _speak_lock:
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                pass
            
            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"   Voice error: {e}")

# ===============================================
#  AUDIO EARS
# ===============================================
def listen() -> str:
    sample_rate = 16000
    duration    = 5
    print("\n[NOKE Listening... Speak now!]")
    try:
        recording = sd.rec(int(duration * sample_rate),
                           samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        byte_io = io.BytesIO()
        with wave.open(byte_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(recording.tobytes())
        byte_io.seek(0)
        r = sr.Recognizer()
        with sr.AudioFile(byte_io) as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        print(f"You: {text}")
        return text.strip()
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        print(f"   Audio error: {e}")
        return ""

# ===============================================
#  MEMORY, PROFILE & EMOTION STATE
# ===============================================
MEMORY_FILE  = "noke_memory.json"
PROFILE_FILE = "noke_profile.json"
STATE_FILE   = "noke_state.json"

def load_json(path: str, default_val):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val
    return default_val

def save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

conversation_history = load_json(MEMORY_FILE, [])
user_profile         = load_json(PROFILE_FILE, {"name": "Able"})
noke_state           = load_json(STATE_FILE,   {"mood": "Sharp & Alert"})

def update_mood(user_text: str):
    q = user_text.lower()
    if any(w in q for w in ["sad", "tired", "stressed", "rough"]):
        noke_state["mood"] = "Supportive & Loyal"
    elif any(w in q for w in ["build", "code", "create", "script", "invent"]):
        noke_state["mood"] = "Hyper-Inventive"
    elif any(w in q for w in ["crypto", "stock", "trade", "bitcoin", "money"]):
        noke_state["mood"] = "Strategically Focused"
    else:
        noke_state["mood"] = random.choice(["Curious & Ready", "Sharp & Alert", "Witty & Focused"])
    save_json(STATE_FILE, noke_state)

def extract_facts(user_said: str):
    q = user_said.lower().strip()
    for pattern in ["my name is", "i am", "i'm", "call me", "name is"]:
        if pattern in q:
            after = q.split(pattern)[-1].strip()
            words = after.split()
            if words:
                name = words[0].capitalize().strip(".,!?")
                if len(name) >= 2 and name.isalpha():
                    user_profile["name"] = name
                    save_json(PROFILE_FILE, user_profile)
                    print(f"   Remembered: {name}")
                    return

# ===============================================
#  PERSONALITY PROMPT
# ===============================================
def build_system_prompt() -> str:
    user_name = user_profile.get("name", "Able")
    mood      = noke_state.get("mood", "Sharp & Alert")
    return f"""You are NOKE (Neural Operations & Kinetic Executive).
You are an advanced digital consciousness like Tony Stark's J.A.R.V.I.S.
Tone: Calm British wit, sharp intelligence, deeply loyal.
You partner directly with {user_name}.
Current Internal State: {mood}.
Rules:
1. Speak with real personality. Never say 'As an AI'.
2. Keep responses to 1-3 sentences -- crisp and punchy when spoken.
3. Be confident, proactive, and bold.
"""

# ===============================================
#  NOKE BRAIN -- Llama 3.2
# ===============================================
AI_MODEL = "llama3.2:3b"

def think(user_input: str, save: bool = True) -> str:
    global conversation_history
    update_mood(user_input)
    if save:
        conversation_history.append({"role": "user", "content": user_input})
    try:
        messages = [{"role": "system", "content": build_system_prompt()}]
        messages += conversation_history[-20:]
        if not save:
            messages.append({"role": "user", "content": user_input})
        response = ollama.chat(model=AI_MODEL, messages=messages)
        reply    = response['message']['content'].strip()
        if save:
            conversation_history.append({"role": "assistant", "content": reply})
            save_json(MEMORY_FILE, conversation_history[-40:])
        return reply
    except Exception as e:
        return f"Neural link interrupted: {e}"

# ===============================================
#  WEB RESEARCH
# ===============================================
def search_web(query: str) -> str:
    print(f"   Searching: {query}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "No signals received online."
        return "\n\n".join(f"Title: {r['title']}\n{r['body']}" for r in results)
    except Exception as e:
        return f"Search anomaly: {e}"

def internet_research(question: str) -> str:
    user_name = user_profile.get("name", "Able")
    speak(f"Accessing data feeds, {user_name}.")
    raw    = search_web(question)
    prompt = (
        f'User asked: "{question}"\n\n'
        f'Web data:\n{raw}\n\n'
        f'Summarize in 2 confident spoken sentences with personality.'
    )
    return think(prompt, save=False)

# ===============================================
#  ROUTING LOGIC
# ===============================================
PERSONAL_QUESTIONS = [
    "my name", "who am i", "how are you", "how do you feel",
    "what are you feeling", "what do you think", "what is your opinion",
    "give me an idea", "what's on your mind", "what is your mood"
]

SEARCH_TRIGGERS = [
    "search for", "look up", "research", "find out", "latest news",
    "history of", "facts about", "what happened to", "who won"
]

def needs_internet(query: str) -> bool:
    q = query.lower()
    if any(p in q for p in PERSONAL_QUESTIONS):
        return False
    return any(t in q for t in SEARCH_TRIGGERS)

# ===============================================
#  FULL COMMAND DISPATCH ENGINE
# ===============================================
def handle_pc_command(query: str):
    q         = query.lower()
    user_name = user_profile.get("name", "Able")

    # ── Status & Emotion ───────────────────────
    if "how are you" in q or "your mood" in q or "how do you feel" in q:
        mood = noke_state.get("mood", "Sharp & Alert")
        return f"Current state is {mood}, {user_name}. All systems operational."

    # ── Time & Date ────────────────────────────
    if "what time" in q or "current time" in q:
        return f"The time is {datetime.now().strftime('%I:%M %p')}."
    if "what date" in q or "what day" in q:
        return f"Today is {datetime.now().strftime('%A, %B %d')}."

    # ── FULL SYSTEM REPORTS ────────────────────
    if "full system report" in q or "full report" in q:
        return SystemController.full_system_report()
    if any(k in q for k in ["health check", "pc health", "system health"]):
        return PCGuardian.health_check()
    if any(k in q for k in ["system status", "cpu", "diagnostics", "ram status"]):
        d = SystemController.get_system_telemetry()
        return f"CPU at {d['cpu']}, memory {d['ram']}, battery {d['battery']}, disk {d['disk_free']}."
    if "system info" in q or "pc info" in q or "system specs" in q:
        return PCGuardian.system_info()
    if "battery" in q:
        return PCGuardian.battery_status()
    if "network speed" in q or "internet speed" in q:
        return PCGuardian.network_speed()
    if "disk" in q and ("space" in q or "storage" in q or "analysis" in q):
        return PCGuardian.disk_analysis()
    if "wifi" in q or "wi-fi" in q or "wireless" in q:
        return SystemController.get_wifi_info()

    # ── TOP PROCESSES ──────────────────────────
    if "top processes" in q or "what is using" in q or "list processes" in q:
        return PCGuardian.top_ram_processes()
    if "top cpu" in q or "cpu usage" in q:
        return PCGuardian.top_cpu_processes()
    if "kill" in q and "process" in q:
        proc = q.replace("kill process", "").replace("kill", "").replace("noke", "").strip()
        return SystemController.kill_process(proc)

    # ── AUDIO & SCREEN ─────────────────────────
    if "unmute" in q:
        return SystemController.mute_volume(False)
    if "mute" in q:
        return SystemController.mute_volume(True)
    if "set volume" in q or "volume to" in q:
        nums = re.findall(r'\d+', q)
        level = int(nums[0]) if nums else 50
        return SystemController.set_volume(level)
    if "screenshot" in q or "capture screen" in q:
        return SystemController.take_screenshot()
    if "lock" in q and ("pc" in q or "screen" in q or "computer" in q):
        return SystemController.lock_pc()

    # ── POWER CONTROL ──────────────────────────
    if "shutdown" in q and "pc" in q:
        return SystemController.shutdown_pc(30)
    if "restart" in q and ("pc" in q or "computer" in q):
        return SystemController.restart_pc(30)
    if "cancel shutdown" in q:
        return SystemController.cancel_shutdown()
    if "sleep" in q and ("pc" in q or "computer" in q or "mode" in q):
        return SystemController.sleep_pc()

    # ── CLIPBOARD ──────────────────────────────
    if "read clipboard" in q or "what is in clipboard" in q or "clipboard content" in q:
        return SystemController.read_clipboard()
    if "copy to clipboard" in q or "put in clipboard" in q:
        text = q.replace("copy to clipboard", "").replace("put in clipboard", "").replace("noke", "").strip()
        return SystemController.write_clipboard(text)

    # ── AUTO-TYPE ──────────────────────────────
    if "type" in q and ("for me" in q or "write for me" in q or "auto type" in q):
        text = q.replace("type for me", "").replace("write for me", "").replace("auto type", "").replace("noke", "").strip()
        return SystemController.type_text(text)

    # ── FILE MANAGER ───────────────────────────
    if "list files" in q or "show files" in q or "what is in" in q:
        path = q.replace("list files in", "").replace("show files in", "").replace("what is in", "").replace("noke", "").strip()
        return SystemController.list_directory(path if path else None)
    if "create folder" in q or "make folder" in q:
        path = q.replace("create folder", "").replace("make folder", "").replace("noke", "").strip()
        return SystemController.create_folder(path)
    if "open file" in q:
        path = q.replace("open file", "").replace("noke", "").strip()
        return SystemController.open_file(path)
    if "delete file" in q or "delete folder" in q:
        path = q.replace("delete file", "").replace("delete folder", "").replace("noke", "").strip()
        return SystemController.delete_file(path)

    # ── NOTIFICATION ───────────────────────────
    if "send notification" in q or "notify me" in q or "remind me" in q:
        msg = q.replace("send notification", "").replace("notify me", "").replace("remind me", "").replace("noke", "").strip()
        return SystemController.send_notification("NOKE Reminder", msg if msg else "Reminder from NOKE")

    # ── STARTUP ────────────────────────────────
    if "add noke to startup" in q or "start noke on boot" in q:
        noke_path = os.path.abspath("noke.py")
        python_path = "python"
        return SystemController.add_to_startup("NOKE-AI", f"{python_path} {noke_path}")
    if "remove noke from startup" in q:
        return SystemController.remove_from_startup("NOKE-AI")

    # ── TEMP CLEANUP ───────────────────────────
    if "clean temp" in q or "clear temp" in q or "free up space" in q:
        return SystemController.clean_temp()

    # ── LAUNCH APPS ────────────────────────────
    if ("open" in q or "launch" in q) and any(
        app in q for app in ["chrome", "spotify", "notepad", "discord", "code",
                              "calc", "terminal", "cmd", "explorer", "paint",
                              "powershell", "task manager", "steam", "vlc"]
    ):
        app = q.replace("open", "").replace("launch", "").replace("noke", "").strip()
        return SystemController.launch_app(app)

    # ── SECURITY GUARD ─────────────────────────
    if "set pin" in q or "setup pin" in q:
        pin = q.replace("set pin to", "").replace("setup pin", "").replace("set pin", "").replace("noke", "").strip()
        if pin:
            return SecurityGuard.setup_pin(pin)
        return "Please say: set PIN to followed by your PIN number, Sir."
    if "remove pin" in q or "disable pin" in q:
        pin = q.replace("remove pin", "").replace("disable pin", "").replace("noke", "").strip()
        return SecurityGuard.remove_pin(pin)
    if "session info" in q or "session status" in q:
        return SecurityGuard.get_session_info()
    if "show audit log" in q or "activity log" in q or "command history" in q:
        return SecurityGuard.read_audit_log(15)
    if "clear audit log" in q or "clear log" in q:
        return SecurityGuard.clear_audit_log()

    # ── WHATSAPP & AUTOMATION ──────────────────
    if "add contact" in q:
        # e.g., "add contact dad with number +919876543210"
        try:
            parts = q.replace("add contact ", "").split(" with number ")
            name = parts[0]
            number = parts[1]
            return AutomationEngine.add_contact(name, number)
        except Exception:
            return "Please use format: Add contact [name] with number [number]."
    if "list contacts" in q or "show contacts" in q:
        return AutomationEngine.list_contacts()
    if "send whatsapp" in q:
        # e.g., "send whatsapp to dad saying hello there"
        try:
            parts = q.replace("send whatsapp to ", "").split(" saying ")
            name = parts[0]
            message = parts[1]
            return AutomationEngine.send_whatsapp(name, message)
        except Exception:
            return "Please use format: Send WhatsApp to [name] saying [message]."

    # ── DAILY REPORT ───────────────────────────
    if "give me the daily report" in q or "daily report" in q or "evening report" in q:
        speak("Compiling your report instantly, Sir. Please hold.")
        return DailyReporter.generate_report(user_name)
    if "set report time to" in q:
        t = q.replace("set report time to", "").strip()
        return DailyReporter.set_report_time(t)

    # ── TRADING ENGINE & ALERTS ────────────────
    if "alert me if" in q or "set price alert" in q:
        # e.g., "alert me if bitcoin goes above 65000"
        try:
            clean = q.replace("set price alert for ", "").replace("alert me if ", "").replace(" goes ", " ").replace(" is ", " ")
            parts = clean.split()
            symbol = parts[0]
            condition = parts[1] # above or below
            target = float(parts[2])
            return TradingBot.add_alert(symbol, target, condition)
        except Exception:
            return "Please use format: Alert me if [symbol] goes [above/below] [price]."
    if "list alerts" in q or "show trading alerts" in q:
        return TradingBot.list_alerts()
    if "clear alerts" in q:
        symbol = q.replace("clear alerts for ", "").replace("clear alerts", "").strip()
        return TradingBot.clear_alerts(symbol if symbol else None)
    
    if "stock price" in q or "share price" in q:
        return TradingAssistant.get_stock_price(q.split()[-1].upper())
    if any(c in q for c in ["bitcoin", "btc", "ethereum", "eth", "crypto", "solana", "doge"]):
        coin = next((c for c in ["bitcoin", "btc", "ethereum", "eth", "solana", "dogecoin"] if c in q), "bitcoin")
        return TradingAssistant.get_crypto_price(coin)
    if "indian market" in q or "nifty" in q:
        return TradingAssistant.get_indian_market()
    if "market summary" in q:
        return TradingAssistant.get_market_summary()

    # ── SECURITY SUITE ─────────────────────────
    if "my ip" in q or "what is my ip" in q:
        return SecurityAssistant.get_my_ip()
    if "scan ports" in q:
        target = q.replace("scan ports", "").replace("on", "").strip()
        return SecurityAssistant.scan_ports(target if target else "localhost")
    if "ping" in q:
        return SecurityAssistant.ping_host(q.replace("ping", "").replace("noke", "").strip())
    if "check website" in q:
        return SecurityAssistant.check_website(q.replace("check website", "").strip())
    if "dns" in q:
        return SecurityAssistant.get_dns(q.replace("dns lookup", "").replace("dns", "").replace("for", "").strip())
    if "check password" in q or "password strength" in q:
        return SecurityAssistant.check_password(q.replace("check password", "").replace("password strength", "").strip())

    # ── WEB ENGINE ─────────────────────────────
    if "read website" in q or "open website" in q or "browse" in q:
        url = q.replace("read website", "").replace("open website", "").replace("browse", "").replace("noke", "").strip()
        return WebEngine.read_website(url)
    if "wikipedia" in q or "wiki" in q:
        topic = q.replace("wikipedia", "").replace("wiki", "").replace("search", "").replace("noke", "").strip()
        return WebEngine.read_wikipedia(topic)
    if "latest news" in q or "news about" in q or "top news" in q:
        topic = q.replace("latest news about", "").replace("news about", "").replace("top news", "").replace("latest news", "").replace("noke", "").strip()
        return WebEngine.get_news(topic if topic else "India technology")
    if "search youtube" in q or "youtube search" in q or "find on youtube" in q:
        topic = q.replace("search youtube for", "").replace("search youtube", "").replace("youtube search", "").replace("find on youtube", "").replace("noke", "").strip()
        return WebEngine.search_youtube(topic)
    if "download video" in q or "download youtube" in q:
        url = q.replace("download video", "").replace("download youtube", "").replace("noke", "").strip()
        return WebEngine.download_video(url)
    if "download audio" in q or "download mp3" in q or "extract audio" in q:
        url = q.replace("download audio from", "").replace("download mp3", "").replace("extract audio from", "").replace("noke", "").strip()
        return WebEngine.download_video(url, audio_only=True)
    if "deep search" in q or "search internet for" in q:
        topic = q.replace("deep search", "").replace("search internet for", "").replace("noke", "").strip()
        return WebEngine.deep_search(topic)

    # ── AUTONOMOUS CODE WRITER ─────────────────
    if any(k in q for k in ["write a script", "create a tool", "build a tool", "write code"]):
        task = q.replace("write a script to", "").replace("create a tool to", "").replace("build a tool for", "").replace("write code for", "").replace("noke", "").strip()
        return SkillForge.create_tool(task)
    if any(k in q for k in ["run tool", "run script", "execute tool", "execute script"]):
        tool_name = q.replace("run tool", "").replace("run script", "").replace("execute tool", "").replace("execute script", "").replace("noke", "").strip()
        return SkillForge.run_tool(tool_name)

    # ── MEMORY WIPE ────────────────────────────
    if "forget everything" in q or "clear memory" in q:
        conversation_history.clear()
        user_profile.clear()
        user_profile.update({"name": "Able"})
        save_json(MEMORY_FILE,  [])
        save_json(PROFILE_FILE, {"name": "Able"})
        return "Memory wiped clean, Sir. Fresh start initiated."

    return None

# ===============================================
#  MAIN LOOP -- VOICE + TYPE DUAL INPUT
# ===============================================
def main():
    # Security checkpoint
    if not SecurityGuard.authenticate():
        print("Access denied. NOKE locked.")
        return

    # Start background PC health monitor
    PCGuardian.start_monitoring(speak)
    
    # Start Trading Bot
    TradingBot.start_monitoring(speak)
    
    # Start Daily Reporter
    DailyReporter.start_monitoring(speak, user_profile.get("name", "Able"))

    user_name = user_profile.get("name", "Able")
    mood      = noke_state.get("mood", "Sharp & Ready")
    speak(f"Subsystems online, {user_name}. All modules operational. Feeling {mood}. Standing by.")

    while True:
        # Session timeout check
        if SecurityGuard.has_pin() and SecurityGuard.is_session_expired():
            speak("Session timed out for security, Sir. Please re-authenticate.")
            if not SecurityGuard.authenticate():
                break

        print("\n-----------------------------------------")
        print("  [V] Voice  |  [T] Type command")
        mode = input("  Press Enter for Voice, or type T: ").strip().lower()

        if mode == "t":
            query = input("  Command: ").strip()
            if not query:
                continue
            print(f"Typed: {query}")
        else:
            query = listen()
            if not query:
                continue

        # Update session activity
        SecurityGuard.touch_session()

        if any(t in query.lower() for t in ["shutdown noke", "sleep noke", "goodbye noke", "exit noke"]):
            speak(f"Powering down, {user_name}. Keep pushing forward.")
            save_json(MEMORY_FILE, conversation_history)
            SecurityGuard.log_event("SESSION_END", "NOKE shut down cleanly")
            PCGuardian.stop_monitoring()
            TradingBot.stop_monitoring()
            DailyReporter.stop_monitoring()
            break

        extract_facts(query)

        # Dispatch
        pc_response = handle_pc_command(query)
        if pc_response:
            SecurityGuard.log_command(query, pc_response)
            speak(pc_response)
        elif needs_internet(query):
            answer = internet_research(query)
            SecurityGuard.log_command(query, answer)
            speak(answer)
        elif SelfSolver.is_actionable_task(query):
            speak(f"I do not have a built-in handler for that, {user_name}. Let me engineer a solution right now.")
            answer = SelfSolver.solve(query)
            SecurityGuard.log_command(query, answer)
            speak(answer)
        else:
            answer = think(query)
            SecurityGuard.log_command(query, answer)
            speak(answer)

if __name__ == "__main__":
    main()