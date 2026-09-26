# NOKE — Neural Operations & Kinetic Executive

> A personal AI assistant inspired by Tony Stark's J.A.R.V.I.S.
> Runs 100% offline on your PC. No subscription. No cloud. Your data stays with you.

---

## What NOKE Can Do

- Talk to you like a real person — with personality, opinions, and emotions
- Remember your name, conversations, and preferences permanently
- Control your PC — open apps, screenshot, lock screen, shutdown, restart
- Manage your files — list, create, delete, copy, move files and folders
- Monitor your PC health — battery, RAM, CPU alerts in real time
- Kill processes, clean temp files, set volume, read clipboard
- Give live stock prices, crypto prices, Indian market (NIFTY, SENSEX)
- Scan ports, check IPs, DNS lookup, ping, password strength checker
- Search the internet and summarize results instantly
- Read full Wikipedia articles, fetch live news
- Download YouTube videos and audio (MP3)
- Write and run its own Python code to solve unknown tasks automatically
- Protect itself with PIN security and session management
- Log every command it executes in an audit trail

---

## Requirements

| Requirement | Version |
|---|---|
| Windows | Windows 10 or 11 |
| Python | 3.10 or higher |
| Ollama | Latest version |
| Internet | Required for search and crypto features |

---

## Step 1 — Install Python

1. Go to **https://www.python.org/downloads**
2. Download Python 3.10 or newer
3. During install, tick **"Add Python to PATH"** — very important!
4. Click Install

Verify it worked — open Command Prompt and type:
```
python --version
```
You should see something like `Python 3.11.0`

---

## Step 2 — Install Ollama (the AI brain engine)

1. Go to **https://ollama.com**
2. Click Download for Windows
3. Run the installer
4. After install, Ollama runs automatically in the background

Verify it worked:
```
ollama --version
```

---

## Step 3 — Download the AI Brain Model

Open Command Prompt and run:
```
ollama pull llama3.2:3b
```

This downloads a 2 GB AI model to your PC. It only needs to be done once.
Wait for it to finish completely.

---

## Step 4 — Download NOKE

**Option A — Download ZIP (easiest):**
1. Click the green **Code** button on this page
2. Click **Download ZIP**
3. Extract the ZIP to your Desktop
4. You should now have a folder called `NOKE-AI`

**Option B — Git clone:**
```
git clone https://github.com/abeldanwilson-cyber/NOKE-AI.git
```

---

## Step 5 — Install All Required Libraries

Open Command Prompt **inside the NOKE-AI folder**:

```
cd Desktop\NOKE-AI
```

Then run this single command to install everything:

```
python -m pip install sounddevice SpeechRecognition numpy pyttsx3 ollama requests beautifulsoup4 psutil pyautogui pycaw ddgs yt-dlp yfinance pyperclip
```

Wait for all packages to finish installing.

---

## Step 6 — Run NOKE

Make sure you are inside the NOKE-AI folder, then run:

```
python noke.py
```

You will see:
```
-----------------------------------------
  [V] Voice  |  [T] Type command
  Press Enter for Voice, or type T:
```

- Press **Enter** to use your voice
- Press **T** then Enter to type a command

---

## Example Commands

### PC Control
```
what time is it
open chrome
screenshot
lock pc
shutdown pc
mute
set volume to 80
clean temp files
list files in Desktop
kill process chrome
```

### Health & Status
```
pc health check
battery status
system info
top processes
network speed
disk space
wifi info
```

### Trading & Finance
```
bitcoin price
ethereum price
stock price AAPL
indian market
market summary
```

### Internet & Research
```
wikipedia artificial intelligence
latest news about India
search youtube for Python tutorial
download video https://youtube.com/watch?v=XXXXX
download audio https://youtube.com/watch?v=XXXXX
```

### Security Tools
```
what is my ip
scan ports localhost
ping google.com
check website github.com
check password MyPassword123
```

### Self-Solving (NOKE writes its own code!)
```
download this youtube video https://youtube.com/...
convert 100 dollars to rupees
compress all images in downloads folder
rename all files to lowercase
```

### Personality & Memory
```
how are you feeling
what is your opinion on AI
give me a tech idea
what is my name
```

### Shutdown
```
exit noke
goodbye noke
shutdown noke
```

---

## File Structure

```
NOKE-AI/
|-- noke.py              Main brain and voice loop
|-- system_control.py    Full PC control (files, processes, power, clipboard)
|-- trading_module.py    Stock and crypto trading tools
|-- security_module.py   Cybersecurity and network tools
|-- coder_module.py      Autonomous Python script writer
|-- web_module.py        Internet, Wikipedia, YouTube, news downloader
|-- resolver.py          Self-solving engine (research + code + run)
|-- security_guard.py    PIN protection, session lock, audit logging
|-- pc_guardian.py       Real-time health monitor with voice alerts
|-- README.md            This file
|-- .gitignore           Excluded personal/private files
```

Files created automatically at runtime (not in this repo):
```
noke_memory.json         Your conversation history
noke_profile.json        Your personal profile (name etc.)
noke_state.json          NOKE's current mood state
noke_audit.log           Command audit trail
skills/                  Scripts NOKE writes for itself
noke_downloads/          Downloaded videos and audio
```

---

## Optional — Add PIN Security

To protect NOKE with a PIN so only you can use it, say or type:

```
set pin to 1234
```

From now on, NOKE will ask for your PIN every time it starts.

To remove the PIN:
```
remove pin 1234
```

---

## Troubleshooting

**NOKE says "Neural link interrupted"**
- Make sure Ollama is running. Open a new terminal and run: `ollama serve`

**Voice not working**
- Use Type mode instead: press T when NOKE asks for input
- Make sure your microphone is plugged in and set as default in Windows sound settings

**"Module not found" error**
- Run the pip install command again from Step 5

**Ollama model not found**
- Run: `ollama pull llama3.2:3b`

**yt-dlp not found when downloading videos**
- Run: `python -m pip install yt-dlp`

---

## Built By

Able — with AI assistance from Google Antigravity (Gemini)

---

## Notes

- NOKE runs entirely on your local PC — no data is sent to any server
- Your memory files are private and excluded from this repository
- This project is for personal and educational use
- The cybersecurity tools are for use on your own systems only
