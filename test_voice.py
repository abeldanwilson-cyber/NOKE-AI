# test_voice.py — NOKE Voice Diagnostic
import os, subprocess, winsound

print("\n" + "="*45)
print("   NOKE VOICE DIAGNOSTIC")
print("="*45)

# TEST 1: Basic audio (beep)
print("\n[TEST 1] Playing a beep sound...")
winsound.Beep(800, 800)
r1 = input("Did you HEAR the beep? (yes/no): ").strip().lower()

# TEST 2: VBScript SAPI
print("\n[TEST 2] VBScript voice...")
with open("_t.txt", "w") as f:
    f.write("Hello Sir. NOKE voice test two. Can you hear me?")
vbs = ('Set f=CreateObject("Scripting.FileSystemObject")'
       '.OpenTextFile("_t.txt",1)\n'
       'Set v=CreateObject("SAPI.SpVoice")\n'
       'v.Speak f.ReadAll,0\n'
       'f.Close')
with open("_t.vbs", "w") as f:
    f.write(vbs)
os.system("cscript //nologo _t.vbs")
r2 = input("Did you HEAR speech? (yes/no): ").strip().lower()

# TEST 3: PowerShell SAPI
print("\n[TEST 3] PowerShell voice...")
subprocess.run([
    'powershell', '-Command',
    'Add-Type -AssemblyName System.Speech;'
    '$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;'
    '$s.Volume=100;'
    '$s.Rate=0;'
    '$s.Speak("Hello Sir. NOKE voice test three. Can you hear me?")'
])
r3 = input("Did you HEAR speech? (yes/no): ").strip().lower()

# TEST 4: pyttsx3
print("\n[TEST 4] pyttsx3 voice...")
try:
    import pyttsx3
    e = pyttsx3.init()
    e.setProperty('volume', 1.0)
    e.say("Hello Sir. NOKE voice test four. Can you hear me?")
    e.runAndWait()
    r4 = input("Did you HEAR speech? (yes/no): ").strip().lower()
except Exception as ex:
    print(f"   pyttsx3 error: {ex}")
    r4 = "no"

print("\n" + "="*45)
print("   RESULTS")
print("="*45)
print(f"  Beep:        {r1}")
print(f"  VBScript:    {r2}")
print(f"  PowerShell:  {r3}")
print(f"  pyttsx3:     {r4}")
print("\nShare these results and I will fix NOKE's voice!")