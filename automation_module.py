import os
import json
import pywhatkit
import time
from datetime import datetime

CONTACTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "noke_contacts.json")

class AutomationEngine:
    """Handles 3rd-party automations like WhatsApp messaging."""

    @staticmethod
    def _load_contacts() -> dict:
        if os.path.exists(CONTACTS_FILE):
            try:
                with open(CONTACTS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    @staticmethod
    def _save_contacts(contacts: dict):
        with open(CONTACTS_FILE, "w") as f:
            json.dump(contacts, f, indent=2)

    @staticmethod
    def add_contact(name: str, phone_number: str) -> str:
        """Add a contact. Phone number must include country code (e.g., +91)."""
        name = name.lower().strip()
        phone_number = phone_number.strip()
        if not phone_number.startswith("+"):
            return "Phone number must start with a country code, Sir. E.g., +91 for India."
        
        contacts = AutomationEngine._load_contacts()
        contacts[name] = phone_number
        AutomationEngine._save_contacts(contacts)
        return f"Contact {name.capitalize()} added successfully, Sir."

    @staticmethod
    def list_contacts() -> str:
        contacts = AutomationEngine._load_contacts()
        if not contacts:
            return "No contacts saved yet, Sir."
        names = [name.capitalize() for name in contacts.keys()]
        return f"You have {len(names)} contacts saved, Sir: {', '.join(names)}."

    @staticmethod
    def send_whatsapp(name: str, message: str) -> str:
        """Sends a WhatsApp message instantly via WhatsApp Web."""
        name = name.lower().strip()
        contacts = AutomationEngine._load_contacts()
        
        if name not in contacts:
            return f"I do not have a number for {name.capitalize()}, Sir. Please add the contact first."
        
        phone_number = contacts[name]
        
        try:
            # Threading so NOKE doesn't freeze while the browser opens
            import threading
            def _send():
                try:
                    pywhatkit.sendwhatmsg_instantly(
                        phone_no=phone_number,
                        message=message,
                        wait_time=15,
                        tab_close=True,
                        close_time=3
                    )
                except Exception as e:
                    print(f"\n[WhatsApp Error]: {e}")
            
            threading.Thread(target=_send, daemon=True).start()
            return f"Initiating WhatsApp transmission to {name.capitalize()}, Sir. Please do not touch the mouse for 15 seconds."
        except Exception as e:
            return f"Failed to start WhatsApp thread, Sir. Error: {e}"
