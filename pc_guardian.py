import os
import psutil
import platform
import subprocess
import threading
import time
from datetime import datetime

class PCGuardian:
    """NOKE's PC health monitor — battery alerts, RAM alerts, CPU alerts, disk warnings."""

    _monitor_thread = None
    _monitoring     = False
    _speak_fn       = None  # Will be set by noke.py to the speak() function

    # ===============================================
    #  HEALTH SNAPSHOT
    # ===============================================
    @staticmethod
    def health_check() -> str:
        cpu     = psutil.cpu_percent(interval=0.5)
        ram     = psutil.virtual_memory()
        disk    = psutil.disk_usage('C:\\')
        battery = psutil.sensors_battery()
        net     = psutil.net_io_counters()

        warnings = []
        if cpu > 85:
            warnings.append(f"CPU critically high at {cpu}%")
        if ram.percent > 85:
            warnings.append(f"RAM critically high at {ram.percent}%")
        if disk.percent > 90:
            warnings.append(f"Disk C: nearly full at {disk.percent}%")
        if battery and battery.percent < 15 and not battery.power_plugged:
            warnings.append(f"Battery critically low at {battery.percent:.0f}%")

        status = "All systems nominal." if not warnings else "WARNINGS: " + ". ".join(warnings)

        report = (
            f"PC Health Report, Sir. "
            f"CPU: {cpu}%. "
            f"RAM: {ram.percent}% used ({ram.available // (1024**3)} GB free). "
            f"Disk C: {disk.percent}% used ({disk.free // (1024**3)} GB free). "
            f"Battery: {battery.percent:.0f}% {'charging' if battery and battery.power_plugged else 'on battery'}. "
            f"{status}"
        )
        return report

    # ===============================================
    #  BATTERY MONITOR
    # ===============================================
    @staticmethod
    def battery_status() -> str:
        battery = psutil.sensors_battery()
        if not battery:
            return "No battery detected. Running on mains power, Sir."
        pct     = battery.percent
        plugged = battery.power_plugged
        secs    = battery.secsleft

        if plugged:
            return f"Battery at {pct:.0f}% and charging, Sir."
        elif secs > 0:
            mins = secs // 60
            hrs  = mins // 60
            rem_mins = mins % 60
            time_str = f"{hrs}h {rem_mins}m" if hrs > 0 else f"{mins}m"
            return f"Battery at {pct:.0f}%. Estimated {time_str} remaining on battery, Sir."
        return f"Battery at {pct:.0f}%, Sir."

    # ===============================================
    #  TOP RESOURCE CONSUMERS
    # ===============================================
    @staticmethod
    def top_cpu_processes(n: int = 5) -> str:
        procs = sorted(
            psutil.process_iter(['name', 'cpu_percent']),
            key=lambda p: p.info['cpu_percent'] or 0, reverse=True
        )[:n]
        lines = [f"{p.info['name']} ({p.info['cpu_percent']:.1f}% CPU)" for p in procs]
        return f"Top {n} CPU consumers, Sir: {'. '.join(lines)}."

    @staticmethod
    def top_ram_processes(n: int = 5) -> str:
        procs = sorted(
            psutil.process_iter(['name', 'memory_percent']),
            key=lambda p: p.info['memory_percent'] or 0, reverse=True
        )[:n]
        lines = [f"{p.info['name']} ({p.info['memory_percent']:.1f}% RAM)" for p in procs]
        return f"Top {n} RAM consumers, Sir: {'. '.join(lines)}."

    # ===============================================
    #  NETWORK SPEED
    # ===============================================
    @staticmethod
    def network_speed() -> str:
        net1 = psutil.net_io_counters()
        time.sleep(1)
        net2 = psutil.net_io_counters()
        sent_kbps = (net2.bytes_sent - net1.bytes_sent) / 1024
        recv_kbps = (net2.bytes_recv - net1.bytes_recv) / 1024
        return (
            f"Network speed, Sir: "
            f"Downloading at {recv_kbps:.1f} KB/s. "
            f"Uploading at {sent_kbps:.1f} KB/s."
        )

    # ===============================================
    #  DISK ANALYSIS
    # ===============================================
    @staticmethod
    def disk_analysis() -> str:
        partitions = psutil.disk_partitions()
        results    = []
        for p in partitions:
            try:
                usage = psutil.disk_usage(p.mountpoint)
                results.append(
                    f"{p.device}: {usage.percent}% used "
                    f"({usage.free // (1024**3)} GB free of {usage.total // (1024**3)} GB)"
                )
            except Exception:
                pass
        return f"Disk analysis, Sir: {'. '.join(results)}."

    # ===============================================
    #  SYSTEM INFO
    # ===============================================
    @staticmethod
    def system_info() -> str:
        info = platform.uname()
        ram  = psutil.virtual_memory()
        cpu_count = psutil.cpu_count(logical=True)
        return (
            f"System specification, Sir. "
            f"OS: {info.system} {info.version[:20]}. "
            f"Processor: {info.processor[:40] or 'Unknown'}. "
            f"CPU cores: {cpu_count}. "
            f"Total RAM: {ram.total // (1024**3)} GB. "
            f"Machine name: {info.node}."
        )

    # ===============================================
    #  BACKGROUND HEALTH MONITOR
    # ===============================================
    @staticmethod
    def start_monitoring(speak_fn):
        """Start background thread that alerts NOKE about critical PC issues."""
        PCGuardian._speak_fn  = speak_fn
        PCGuardian._monitoring = True

        def monitor_loop():
            battery_warned = False
            ram_warned     = False
            cpu_warned     = False

            while PCGuardian._monitoring:
                try:
                    # Battery alert
                    battery = psutil.sensors_battery()
                    if battery and not battery.power_plugged:
                        if battery.percent <= 10 and not battery_warned:
                            PCGuardian._speak_fn(
                                f"Sir, urgent warning. Battery is critically low at "
                                f"{battery.percent:.0f}%. Please plug in immediately."
                            )
                            battery_warned = True
                        elif battery.percent > 15:
                            battery_warned = False

                    # RAM alert
                    ram = psutil.virtual_memory()
                    if ram.percent > 90 and not ram_warned:
                        PCGuardian._speak_fn(
                            f"Sir, RAM usage is critically high at {ram.percent}%. "
                            f"I recommend closing some applications."
                        )
                        ram_warned = True
                    elif ram.percent < 80:
                        ram_warned = False

                    # CPU alert
                    cpu = psutil.cpu_percent(interval=1)
                    if cpu > 95 and not cpu_warned:
                        PCGuardian._speak_fn(
                            f"Sir, CPU load is at {cpu}%. "
                            f"Something is consuming heavy processing power."
                        )
                        cpu_warned = True
                    elif cpu < 80:
                        cpu_warned = False

                except Exception:
                    pass

                time.sleep(60)  # Check every 60 seconds

        PCGuardian._monitor_thread = threading.Thread(
            target=monitor_loop, daemon=True, name="NOKEGuardian"
        )
        PCGuardian._monitor_thread.start()

    @staticmethod
    def stop_monitoring():
        PCGuardian._monitoring = False
