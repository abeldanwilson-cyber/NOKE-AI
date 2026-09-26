import os
import subprocess
import webbrowser
import psutil
import pyautogui
import ctypes
import shutil
import platform
import winreg
import pyperclip
import time
from datetime import datetime

class SystemController:

    # ===============================================
    #  SYSTEM TELEMETRY
    # ===============================================
    @staticmethod
    def get_system_telemetry() -> dict:
        cpu     = psutil.cpu_percent(interval=0.5)
        ram     = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        power   = f"{battery.percent:.0f}%" if battery else "Plugged In"
        disk    = psutil.disk_usage('C:\\')
        return {
            "cpu":      f"{cpu}%",
            "ram":      f"{ram.percent}%",
            "battery":  power,
            "disk_free": f"{disk.free // (1024**3)} GB free"
        }

    @staticmethod
    def full_system_report() -> str:
        d = SystemController.get_system_telemetry()
        return (
            f"Full system report, Sir. "
            f"CPU load: {d['cpu']}. "
            f"Memory usage: {d['ram']}. "
            f"Battery: {d['battery']}. "
            f"Disk space remaining: {d['disk_free']}."
        )

    # ===============================================
    #  APP LAUNCHER
    # ===============================================
    @staticmethod
    def launch_app(app_name: str) -> str:
        app = app_name.lower().strip()
        shortcuts = {
            "chrome":      "chrome",
            "browser":     "chrome",
            "spotify":     "spotify",
            "notepad":     "notepad",
            "calculator":  "calc",
            "calc":        "calc",
            "code":        "code",
            "vscode":      "code",
            "discord":     "discord",
            "terminal":    "cmd",
            "cmd":         "cmd",
            "powershell":  "powershell",
            "explorer":    "explorer",
            "files":       "explorer",
            "task manager":"taskmgr",
            "paint":       "mspaint",
            "word":        "winword",
            "excel":       "excel",
            "vlc":         "vlc",
            "steam":       "steam",
        }
        try:
            target = shortcuts.get(app, app)
            subprocess.Popen(target, shell=True)
            return f"Launching {app_name}, Sir."
        except Exception:
            webbrowser.open(f"https://www.google.com/search?q={app_name}")
            return f"Could not find {app_name} locally. Searching online, Sir."

    # ===============================================
    #  PROCESS MANAGER
    # ===============================================
    @staticmethod
    def list_processes(top: int = 8) -> str:
        procs = sorted(psutil.process_iter(['name','cpu_percent','memory_percent']),
                       key=lambda p: p.info['memory_percent'] or 0, reverse=True)[:top]
        lines = [f"{p.info['name']} (RAM: {p.info['memory_percent']:.1f}%)" for p in procs]
        return f"Top {top} processes by memory, Sir: {'. '.join(lines)}."

    @staticmethod
    def kill_process(name: str) -> str:
        killed = []
        for proc in psutil.process_iter(['name']):
            if name.lower() in (proc.info['name'] or '').lower():
                try:
                    proc.kill()
                    killed.append(proc.info['name'])
                except Exception:
                    pass
        if killed:
            return f"Terminated {', '.join(set(killed))}, Sir."
        return f"No running process named {name} found, Sir."

    # ===============================================
    #  SCREEN & VISUAL
    # ===============================================
    @staticmethod
    def take_screenshot(path: str = "noke_view.png") -> str:
        pyautogui.screenshot().save(path)
        return f"Visual scan saved as {path}, Sir."

    @staticmethod
    def lock_pc() -> str:
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked. Security active, Sir."

    @staticmethod
    def set_wallpaper(image_path: str) -> str:
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            return f"Desktop wallpaper updated, Sir."
        except Exception as e:
            return f"Wallpaper change failed, Sir: {e}"

    # ===============================================
    #  VOLUME CONTROL
    # ===============================================
    @staticmethod
    def mute_volume(mute: bool = True) -> str:
        key = chr(0xAD)  # VK_VOLUME_MUTE
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        return "Audio muted, Sir." if mute else "Audio restored, Sir."

    @staticmethod
    def set_volume(level: int) -> str:
        # level: 0-100
        level = max(0, min(100, level))
        script = f"""
$wshShell = New-Object -ComObject WScript.Shell
$volume = [int]({level} / 2)
For ($i = 0; $i -lt 50; $i++) {{
    $wshShell.SendKeys([char]174)
}}
For ($i = 0; $i -lt $volume; $i++) {{
    $wshShell.SendKeys([char]175)
}}
"""
        try:
            subprocess.run(["powershell", "-Command", script], capture_output=True)
            return f"Volume set to approximately {level}%, Sir."
        except Exception as e:
            return f"Volume adjustment failed, Sir: {e}"

    # ===============================================
    #  CLIPBOARD
    # ===============================================
    @staticmethod
    def read_clipboard() -> str:
        try:
            text = pyperclip.paste()
            if not text.strip():
                return "Clipboard is empty, Sir."
            preview = text[:200]
            return f"Clipboard contains, Sir: {preview}{'...' if len(text) > 200 else ''}"
        except Exception as e:
            return f"Could not read clipboard, Sir: {e}"

    @staticmethod
    def write_clipboard(text: str) -> str:
        try:
            pyperclip.copy(text)
            return f"Copied to clipboard, Sir."
        except Exception as e:
            return f"Clipboard write failed, Sir: {e}"

    # ===============================================
    #  AUTO-TYPE
    # ===============================================
    @staticmethod
    def type_text(text: str) -> str:
        try:
            time.sleep(1.5)
            pyautogui.typewrite(text, interval=0.04)
            return f"Text typed into active window, Sir."
        except Exception as e:
            return f"Auto-type failed, Sir: {e}"

    @staticmethod
    def press_key(key: str) -> str:
        try:
            pyautogui.press(key)
            return f"Key {key} pressed, Sir."
        except Exception as e:
            return f"Key press failed, Sir: {e}"

    # ===============================================
    #  FILE MANAGER
    # ===============================================
    @staticmethod
    def list_directory(path: str = None) -> str:
        path = path or os.path.expanduser("~/Desktop")
        try:
            items = os.listdir(path)
            folders = [i for i in items if os.path.isdir(os.path.join(path, i))]
            files   = [i for i in items if os.path.isfile(os.path.join(path, i))]
            return (f"Directory {path} contains {len(folders)} folders and "
                    f"{len(files)} files, Sir. "
                    f"Folders: {', '.join(folders[:5]) if folders else 'none'}. "
                    f"Files: {', '.join(files[:5]) if files else 'none'}.")
        except Exception as e:
            return f"Could not read directory, Sir: {e}"

    @staticmethod
    def create_folder(path: str) -> str:
        try:
            os.makedirs(path, exist_ok=True)
            return f"Folder created at {path}, Sir."
        except Exception as e:
            return f"Folder creation failed, Sir: {e}"

    @staticmethod
    def delete_file(path: str) -> str:
        try:
            if os.path.isfile(path):
                os.remove(path)
                return f"File {os.path.basename(path)} deleted, Sir."
            elif os.path.isdir(path):
                shutil.rmtree(path)
                return f"Folder {os.path.basename(path)} and its contents deleted, Sir."
            return f"Path {path} not found, Sir."
        except Exception as e:
            return f"Deletion failed, Sir: {e}"

    @staticmethod
    def copy_file(src: str, dst: str) -> str:
        try:
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                return f"File copied to {dst}, Sir."
            shutil.copytree(src, dst)
            return f"Folder copied to {dst}, Sir."
        except Exception as e:
            return f"Copy failed, Sir: {e}"

    @staticmethod
    def move_file(src: str, dst: str) -> str:
        try:
            shutil.move(src, dst)
            return f"Moved to {dst}, Sir."
        except Exception as e:
            return f"Move failed, Sir: {e}"

    @staticmethod
    def open_file(path: str) -> str:
        try:
            os.startfile(path)
            return f"Opening {os.path.basename(path)}, Sir."
        except Exception as e:
            return f"Could not open file, Sir: {e}"

    # ===============================================
    #  WINDOWS NOTIFICATIONS
    # ===============================================
    @staticmethod
    def send_notification(title: str, message: str) -> str:
        try:
            script = (
                f'Add-Type -AssemblyName System.Windows.Forms; '
                f'$n = New-Object System.Windows.Forms.NotifyIcon; '
                f'$n.Icon = [System.Drawing.SystemIcons]::Information; '
                f'$n.Visible = $true; '
                f'$n.ShowBalloonTip(4000, "{title}", "{message}", '
                f'[System.Windows.Forms.ToolTipIcon]::None); '
                f'Start-Sleep 5; $n.Visible = $false'
            )
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", script])
            return f"Notification sent, Sir."
        except Exception as e:
            return f"Notification failed, Sir: {e}"

    # ===============================================
    #  STARTUP MANAGER
    # ===============================================
    @staticmethod
    def add_to_startup(name: str, exe_path: str) -> str:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            return f"{name} added to Windows startup, Sir."
        except Exception as e:
            return f"Startup registration failed, Sir: {e}"

    @staticmethod
    def remove_from_startup(name: str) -> str:
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            return f"{name} removed from Windows startup, Sir."
        except Exception as e:
            return f"Startup removal failed, Sir: {e}"

    # ===============================================
    #  POWER CONTROL
    # ===============================================
    @staticmethod
    def shutdown_pc(delay: int = 30) -> str:
        subprocess.run(["shutdown", "/s", "/t", str(delay)])
        return f"System shutdown scheduled in {delay} seconds, Sir."

    @staticmethod
    def restart_pc(delay: int = 30) -> str:
        subprocess.run(["shutdown", "/r", "/t", str(delay)])
        return f"System restart scheduled in {delay} seconds, Sir."

    @staticmethod
    def cancel_shutdown() -> str:
        subprocess.run(["shutdown", "/a"])
        return "Shutdown cancelled, Sir. System remains operational."

    @staticmethod
    def sleep_pc() -> str:
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
        return "Initiating sleep mode, Sir."

    # ===============================================
    #  NETWORK INFO
    # ===============================================
    @staticmethod
    def get_wifi_info() -> str:
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True, text=True
            )
            lines = result.stdout.splitlines()
            ssid    = next((l.split(":")[1].strip() for l in lines if "SSID" in l and "BSSID" not in l), "Unknown")
            signal  = next((l.split(":")[1].strip() for l in lines if "Signal" in l), "Unknown")
            return f"Connected to Wi-Fi network: {ssid}. Signal strength: {signal}, Sir."
        except Exception as e:
            return f"Wi-Fi info unavailable, Sir: {e}"

    # ===============================================
    #  CLEAN TEMP FILES
    # ===============================================
    @staticmethod
    def clean_temp() -> str:
        temp_path = os.environ.get("TEMP", "")
        freed     = 0
        deleted   = 0
        if not temp_path:
            return "Temp directory not found, Sir."
        for item in os.listdir(temp_path):
            item_path = os.path.join(temp_path, item)
            try:
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    os.remove(item_path)
                    freed   += size
                    deleted += 1
                elif os.path.isdir(item_path):
                    size = sum(
                        os.path.getsize(os.path.join(dp, f))
                        for dp, _, fn in os.walk(item_path) for f in fn
                    )
                    shutil.rmtree(item_path)
                    freed   += size
                    deleted += 1
            except Exception:
                pass
        mb = freed / (1024 * 1024)
        return f"Temp cleanup complete, Sir. Removed {deleted} items, freed {mb:.1f} MB."