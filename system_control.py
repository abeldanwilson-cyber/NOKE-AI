import os
import subprocess
import webbrowser
import psutil
import pyautogui
import ctypes
from datetime import datetime

class SystemController:
    @staticmethod
    def get_system_telemetry() -> dict:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        power = f"{battery.percent}%" if battery else "Plugged In"
        return {
            "cpu": f"{cpu}%",
            "ram": f"{ram.percent}%",
            "battery": power
        }

    @staticmethod
    def launch_app(app_name: str) -> str:
        app = app_name.lower().strip()
        shortcuts = {
            "chrome": "chrome",
            "browser": "chrome",
            "spotify": "spotify",
            "notepad": "notepad",
            "calculator": "calc",
            "code": "code"
        }
        if app in shortcuts:
            try:
                subprocess.Popen(shortcuts[app], shell=True)
                return f"Launching {app_name}, Sir."
            except Exception:
                pass
        webbrowser.open(f"https://www.google.com/search?q={app_name}")
        return f"Searching for {app_name}, Sir."

    @staticmethod
    def take_screenshot() -> str:
        pyautogui.screenshot().save("noke_view.png")
        return "Visual scan saved as noke_view.png, Sir."

    @staticmethod
    def lock_pc() -> str:
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked. Security active, Sir."