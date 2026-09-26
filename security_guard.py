import os
import json
import hashlib
import getpass
import time
from datetime import datetime

NOKE_DIR     = os.path.dirname(os.path.abspath(__file__))
PIN_FILE     = os.path.join(NOKE_DIR, "noke_pin.json")
AUDIT_FILE   = os.path.join(NOKE_DIR, "noke_audit.log")
SESSION_TIMEOUT_MINUTES = 60  # Auto-lock after this many minutes of inactivity

class SecurityGuard:
    """NOKE's personal security system — PIN protection, session management, audit logging."""

    _session_start = None
    _last_activity = None
    _authenticated = False

    # ===============================================
    #  PIN MANAGEMENT
    # ===============================================
    @staticmethod
    def _hash_pin(pin: str) -> str:
        return hashlib.sha256(pin.encode()).hexdigest()

    @staticmethod
    def has_pin() -> bool:
        return os.path.exists(PIN_FILE)

    @staticmethod
    def setup_pin(pin: str) -> str:
        if len(pin) < 4:
            return "PIN must be at least 4 digits, Sir."
        data = {"pin_hash": SecurityGuard._hash_pin(pin), "created": datetime.now().isoformat()}
        with open(PIN_FILE, "w") as f:
            json.dump(data, f)
        SecurityGuard.log_event("PIN_SETUP", "Security PIN configured")
        return "Security PIN set successfully, Sir. NOKE is now PIN-protected."

    @staticmethod
    def verify_pin(pin: str) -> bool:
        if not SecurityGuard.has_pin():
            return True  # No PIN set — open access
        try:
            with open(PIN_FILE, "r") as f:
                data = json.load(f)
            return data.get("pin_hash") == SecurityGuard._hash_pin(pin)
        except Exception:
            return False

    @staticmethod
    def change_pin(old_pin: str, new_pin: str) -> str:
        if not SecurityGuard.verify_pin(old_pin):
            SecurityGuard.log_event("PIN_CHANGE_FAILED", "Wrong old PIN entered")
            return "Incorrect current PIN, Sir. Change denied."
        return SecurityGuard.setup_pin(new_pin)

    @staticmethod
    def remove_pin(pin: str) -> str:
        if not SecurityGuard.verify_pin(pin):
            return "Incorrect PIN, Sir. Cannot remove protection."
        if os.path.exists(PIN_FILE):
            os.remove(PIN_FILE)
        SecurityGuard.log_event("PIN_REMOVED", "PIN protection disabled")
        return "PIN protection removed, Sir. NOKE is now open access."

    # ===============================================
    #  SESSION MANAGEMENT
    # ===============================================
    @staticmethod
    def start_session():
        SecurityGuard._session_start = time.time()
        SecurityGuard._last_activity = time.time()
        SecurityGuard._authenticated = True
        SecurityGuard.log_event("SESSION_START", "NOKE session initiated")

    @staticmethod
    def touch_session():
        SecurityGuard._last_activity = time.time()

    @staticmethod
    def is_session_expired() -> bool:
        if SecurityGuard._last_activity is None:
            return False
        elapsed_minutes = (time.time() - SecurityGuard._last_activity) / 60
        return elapsed_minutes > SESSION_TIMEOUT_MINUTES

    @staticmethod
    def lock_session():
        SecurityGuard._authenticated = False
        SecurityGuard.log_event("SESSION_LOCKED", "Session locked due to inactivity")

    @staticmethod
    def get_session_info() -> str:
        if SecurityGuard._session_start is None:
            return "No active session, Sir."
        duration = int((time.time() - SecurityGuard._session_start) / 60)
        idle     = int((time.time() - SecurityGuard._last_activity) / 60)
        return (
            f"Session active for {duration} minutes, Sir. "
            f"Last activity: {idle} minutes ago. "
            f"Auto-lock in: {max(0, SESSION_TIMEOUT_MINUTES - idle)} minutes."
        )

    # ===============================================
    #  AUDIT LOG
    # ===============================================
    @staticmethod
    def log_event(event_type: str, detail: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry     = f"[{timestamp}] [{event_type}] {detail}\n"
        try:
            with open(AUDIT_FILE, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

    @staticmethod
    def log_command(user_input: str, response_preview: str = ""):
        preview = response_preview[:80] if response_preview else ""
        SecurityGuard.log_event("COMMAND", f"Input: {user_input[:80]} | Response: {preview}")

    @staticmethod
    def read_audit_log(last_n: int = 10) -> str:
        if not os.path.exists(AUDIT_FILE):
            return "No audit log exists yet, Sir."
        try:
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            recent = lines[-last_n:]
            if not recent:
                return "Audit log is empty, Sir."
            return "Recent activity log, Sir:\n" + "".join(recent)
        except Exception as e:
            return f"Could not read audit log, Sir: {e}"

    @staticmethod
    def clear_audit_log() -> str:
        try:
            open(AUDIT_FILE, "w").close()
            return "Audit log cleared, Sir."
        except Exception as e:
            return f"Could not clear log, Sir: {e}"

    # ===============================================
    #  STARTUP AUTHENTICATION
    # ===============================================
    @staticmethod
    def authenticate() -> bool:
        """Called at NOKE startup. Returns True if user is authenticated."""
        if not SecurityGuard.has_pin():
            SecurityGuard.start_session()
            return True

        print("\n" + "=" * 45)
        print("  NOKE SECURITY CHECKPOINT")
        print("  Enter your PIN to unlock NOKE")
        print("=" * 45)

        for attempt in range(3):
            try:
                pin = getpass.getpass(f"  PIN ({3 - attempt} attempts remaining): ")
                if SecurityGuard.verify_pin(pin):
                    print("  Access granted. Welcome back, Sir.")
                    print("=" * 45)
                    SecurityGuard.start_session()
                    SecurityGuard.log_event("AUTH_SUCCESS", "PIN verified successfully")
                    return True
                else:
                    print("  Incorrect PIN. Try again.")
                    SecurityGuard.log_event("AUTH_FAIL", f"Wrong PIN attempt {attempt + 1}")
            except Exception:
                return False

        print("  3 failed attempts. NOKE locked.")
        SecurityGuard.log_event("AUTH_LOCKOUT", "3 failed PIN attempts - lockout")
        return False
