# NOKE — Neural Operations & Kinetic Executive

> A personal AI assistant inspired by Tony Stark's J.A.R.V.I.S.
> Built with Python, Ollama (Llama 3.2), and local voice processing.

---

## Features

- Voice activated — speak naturally, NOKE listens and responds
- Type or speak — dual input mode supported
- Local AI brain — runs 100% offline using Ollama + Llama 3.2
- Human-like personality — emotions, opinions, British wit
- Permanent memory — remembers your name, preferences, conversations
- Internet research — live web search and Wikipedia access
- Trading tools — real-time stock prices, crypto prices, Indian market (NIFTY, SENSEX)
- Cybersecurity tools — port scanner, IP lookup, DNS, ping, password checker
- PC control — open apps, screenshot, lock screen, mute, system status
- Video downloader — download YouTube videos and audio via voice command
- Autonomous code writer — NOKE writes and runs its own Python scripts

---

## Project Structure

```
NOKE/
|-- noke.py              Main brain and voice loop
|-- system_control.py    PC control module
|-- trading_module.py    Stock and crypto trading tools
|-- security_module.py   Cybersecurity and network tools
|-- coder_module.py      Autonomous script writer
|-- web_module.py        Internet, Wikipedia, YouTube, news
|-- ideas.py             Creative idea engine
|-- README.md            This file
|-- .gitignore           Excluded personal files
```

---

## Requirements

- Python 3.10 or higher (tested on Python 3.14)
- Ollama installed — https://ollama.com
- Llama 3.2 model downloaded

```bash
ollama pull llama3.2:3b
```

---

## Install Dependencies

```bash
python -m pip install sounddevice SpeechRecognition numpy pyttsx3 ollama requests beautifulsoup4 psutil pyautogui pycaw ddgs yt-dlp yfinance
```

---

## How to Run

1. Make sure Ollama is running in the background
2. Open Command Prompt in the NOKE folder
3. Run:

```bash
python noke.py
```

4. Choose Voice (press Enter) or Type (press T) to give commands

---

## Example Commands

| Say or Type | What NOKE Does |
|---|---|
| What time is it | Tells the current time |
| Bitcoin price | Live crypto price |
| Stock price AAPL | Live Apple stock price |
| Indian market | NIFTY and SENSEX update |
| Latest news about AI | Searches and reads live news |
| Wikipedia quantum computing | Reads full Wikipedia article |
| Download video youtube.com/... | Downloads the video |
| Scan ports localhost | Scans your own PC ports |
| What is my IP | Shows your public IP and location |
| Write a script to calculate pi | NOKE writes and saves a Python script |
| System status | CPU, RAM and battery report |
| Open Chrome | Launches Chrome |
| Screenshot | Takes a screenshot |
| Shutdown NOKE | Saves memory and exits |

---

## Built By

Able — with AI assistance from Antigravity (Google DeepMind)

---

## Notes

- Your personal memory files (noke_memory.json, noke_profile.json) are excluded from this repo
- Never share your memory files — they contain your personal conversations
- This project is for personal and educational use
