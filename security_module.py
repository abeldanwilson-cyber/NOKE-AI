import socket
import subprocess
import platform
import requests
import hashlib

class SecurityAssistant:

    @staticmethod
    def get_my_ip() -> str:
        """Get your public IP and location."""
        try:
            ip  = requests.get("https://api.ipify.org?format=json", timeout=5).json()["ip"]
            loc = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5).json()
            return (f"Your public IP is {ip}, Sir. "
                    f"Location detected as {loc.get('city','Unknown')}, "
                    f"{loc.get('country_name','Unknown')}.")
        except Exception:
            return "Could not retrieve IP information, Sir."

    @staticmethod
    def network_info() -> str:
        """Get local network details."""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return (f"Local network report, Sir. "
                    f"Device hostname: {hostname}. "
                    f"Local IP address: {local_ip}.")
        except Exception:
            return "Local network info unavailable, Sir."

    @staticmethod
    def scan_ports(host: str) -> str:
        """Scan common ports — use ONLY on your own systems."""
        common_ports = [21,22,23,25,53,80,443,3306,5432,8080,8443,27017]
        open_ports   = []
        try:
            ip = socket.gethostbyname(host)
        except Exception:
            return f"Cannot resolve host {host}, Sir."
        for port in common_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
                s.close()
            except Exception:
                pass
        if open_ports:
            return (f"Port scan complete, Sir. "
                    f"Open ports on {host}: {', '.join(map(str, open_ports))}.")
        return f"No common open ports found on {host}, Sir."

    @staticmethod
    def check_website(url: str) -> str:
        """Check if a website is online."""
        if not url.startswith("http"):
            url = "https://" + url
        try:
            r = requests.get(url, timeout=6)
            ms = int(r.elapsed.total_seconds() * 1000)
            return (f"{url} is ONLINE, Sir. "
                    f"Status {r.status_code}. Response time: {ms}ms.")
        except requests.exceptions.ConnectionError:
            return f"{url} is OFFLINE or unreachable, Sir."
        except Exception as e:
            return f"Website check failed, Sir. {e}"

    @staticmethod
    def ping_host(host: str) -> str:
        """Ping a host."""
        try:
            param  = "-n" if platform.system().lower() == "windows" else "-c"
            result = subprocess.run(
                ["ping", param, "3", host],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return f"Ping to {host} successful, Sir. Host is reachable and responding."
            return f"Ping to {host} failed, Sir. Host may be offline or blocking pings."
        except Exception as e:
            return f"Ping operation failed, Sir. {e}"

    @staticmethod
    def get_dns(domain: str) -> str:
        """DNS lookup for a domain."""
        try:
            ip = socket.gethostbyname(domain)
            return f"DNS lookup complete, Sir. {domain} resolves to IP address {ip}."
        except Exception:
            return f"DNS lookup failed for {domain}, Sir."

    @staticmethod
    def check_password(password: str) -> str:
        """Analyze password strength."""
        score = 0
        tips  = []
        if len(password) >= 12:   score += 2
        elif len(password) >= 8:  score += 1
        else: tips.append("use at least 12 characters")
        if any(c.isupper() for c in password): score += 1
        else: tips.append("add uppercase letters")
        if any(c.islower() for c in password): score += 1
        else: tips.append("add lowercase letters")
        if any(c.isdigit() for c in password): score += 1
        else: tips.append("add numbers")
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 2
        else: tips.append("add special characters like ! @ # $")
        levels = {0:"Very Weak",1:"Weak",2:"Weak",3:"Fair",4:"Strong",5:"Strong",6:"Very Strong",7:"Unbreakable"}
        strength = levels.get(score, "Strong")
        result   = f"Password strength assessment: {strength}, Sir."
        if tips:
            result += f" To improve: {', '.join(tips)}."
        return result

    @staticmethod
    def hash_text(text: str, algorithm: str = "sha256") -> str:
        """Generate a hash of any text."""
        try:
            h = hashlib.new(algorithm, text.encode()).hexdigest()
            return f"{algorithm.upper()} hash generated, Sir: {h}"
        except Exception:
            return f"Hashing failed, Sir. Unsupported algorithm: {algorithm}"