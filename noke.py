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

# Modular Subsystems
from system_control import SystemController
from trading_module  import TradingAssistant
from security_module import SecurityAssistant
from coder_module    import SkillForge
from web_module      import WebEngine

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# ===============================================
#  VOICE ENGINE
# ===============================================
def speak(text: str, rate: int = 165):
    print(f"\n[NOKE]: {text}")
    try:
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
#  ALL COMMANDS
# ===============================================
def handle_pc_command(query: str):
    q         = query.lower()
    user_name = user_profile.get("name", "Able")

    # Emotion & Status
    if "how are you" in q or "your mood" in q or "how do you feel" in q:
        mood = noke_state.get("mood", "Sharp & Alert")
        return f"Current state is {mood}, {user_name}. All systems operational."

    # Time & Date
    if "what time" in q or "current time" in q:
        return f"The time is {datetime.now().strftime('%I:%M %p')}."
    if "what date" in q or "what day" in q:
        return f"Today is {datetime.now().strftime('%A, %B %d')}."

    # System Diagnostics
    if any(k in q for k in ["system status", "cpu", "diagnostics", "ram status"]):
        d = SystemController.get_system_telemetry()
        return f"CPU at {d['cpu']}, memory {d['ram']}, battery {d['battery']}."

    # Audio & Screen
    if "unmute" in q:
        return SystemController.mute_volume(False)
    if "mute" in q:
        return SystemController.mute_volume(True)
    if "screenshot" in q or "capture screen" in q:
        return SystemController.take_screenshot()
    if "lock" in q and ("pc" in q or "screen" in q or "computer" in q):
        return SystemController.lock_pc()

    # Launch Apps
    if ("open" in q or "launch" in q) and any(
        app in q for app in ["chrome", "spotify", "notepad", "discord", "code", "calc", "terminal"]
    ):
        app = q.replace("open", "").replace("launch", "").replace("noke", "").strip()
        return SystemController.launch_app(app)

    # TRADING ENGINE
    if "stock price" in q or "share price" in q:
        return TradingAssistant.get_stock_price(q.split()[-1].upper())
    if any(c in q for c in ["bitcoin", "btc", "ethereum", "eth", "crypto", "solana", "doge"]):
        coin = next((c for c in ["bitcoin", "btc", "ethereum", "eth", "solana", "dogecoin"] if c in q), "bitcoin")
        return TradingAssistant.get_crypto_price(coin)
    if "indian market" in q or "nifty" in q:
        return TradingAssistant.get_indian_market()
    if "market summary" in q:
        return TradingAssistant.get_market_summary()

    # SECURITY SUITE
    if "my ip" in q or "what is my ip" in q:
        return SecurityAssistant.get_my_ip()
    if "scan ports" in q:
        target = q.replace("scan ports", "").replace("on", "").strip()
        return SecurityAssistant.scan_ports(target if target else "localhost")
    if "ping" in q:
        return SecurityAssistant.ping_host(q.replace("ping", "").replace("noke", "").strip())
    if "check website" in q:
        target = q.replace("check website", "").strip()
        return SecurityAssistant.check_website(target)
    if "dns" in q:
        target = q.replace("dns lookup", "").replace("dns", "").replace("for", "").strip()
        return SecurityAssistant.get_dns(target)
    if "check password" in q or "password strength" in q:
        pwd = q.replace("check password", "").replace("password strength", "").strip()
        return SecurityAssistant.check_password(pwd)

    # WEB ENGINE
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

    # AUTONOMOUS CODE WRITER
    if any(k in q for k in ["write a script", "create a tool", "build a tool", "write code"]):
        task = q.replace("write a script to", "").replace("create a tool to", "").replace("build a tool for", "").replace("write code for", "").replace("noke", "").strip()
        return SkillForge.create_tool(task)
    if any(k in q for k in ["run tool", "run script", "execute tool", "execute script"]):
        tool_name = q.replace("run tool", "").replace("run script", "").replace("execute tool", "").replace("execute script", "").replace("noke", "").strip()
        return SkillForge.run_tool(tool_name)

    # Memory Wipe
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
    user_name = user_profile.get("name", "Able")
    mood      = noke_state.get("mood", "Sharp & Ready")
    speak(f"Subsystems online, {user_name}. Feeling {mood}. Standing by.")

    while True:
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

        if any(t in query.lower() for t in ["shutdown noke", "sleep noke", "goodbye noke", "exit noke"]):
            speak(f"Powering down, {user_name}. Keep pushing forward.")
            save_json(MEMORY_FILE, conversation_history)
            break

        extract_facts(query)

        pc_response = handle_pc_command(query)
        if pc_response:
            speak(pc_response)
        elif needs_internet(query):
            answer = internet_research(query)
            speak(answer)
        else:
            answer = think(query)
            speak(answer)

if __name__ == "__main__":
    main()