import os
import re
import requests
import subprocess
from bs4 import BeautifulSoup

# Optional imports with fallback
try:
    import wikipediaapi
    WIKI_AVAILABLE = True
except ImportError:
    WIKI_AVAILABLE = False

DOWNLOADS_DIR = "noke_downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

class WebEngine:

    # ═══════════════════════════════════════
    #  FULL WEBSITE READER
    # ═══════════════════════════════════════
    @staticmethod
    def read_website(url: str) -> str:
        """Reads and extracts clean readable text from any public URL."""
        if not url.startswith("http"):
            url = "https://" + url
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"}
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            # Remove junk tags
            for tag in soup(["script","style","nav","footer","header","aside"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            text = re.sub(r'\s+', ' ', text).strip()
            summary = text[:600]
            return f"Content extracted from {url}: {summary}..."
        except Exception as e:
            return f"Could not read that website, Sir: {e}"

    # ═══════════════════════════════════════
    #  WIKIPEDIA DEEP READER
    # ═══════════════════════════════════════
    @staticmethod
    def read_wikipedia(topic: str) -> str:
        """Fetches the full Wikipedia article for any topic."""
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ','_')}"
            headers = {"User-Agent": "NOKE-AI/1.0"}
            r = requests.get(url, headers=headers, timeout=8)
            data = r.json()
            if "extract" in data:
                extract = data["extract"][:500]
                return f"Wikipedia on {topic}: {extract}"
            return f"No Wikipedia article found for {topic}, Sir."
        except Exception as e:
            return f"Wikipedia access failed: {e}"

    # ═══════════════════════════════════════
    #  LIVE NEWS READER
    # ═══════════════════════════════════════
    @staticmethod
    def get_news(topic: str = "technology") -> str:
        """Fetches latest news headlines for any topic."""
        try:
            url = f"https://news.google.com/rss/search?q={topic.replace(' ','+')}&hl=en-IN&gl=IN&ceid=IN:en"
            r = requests.get(url, timeout=8)
            soup = BeautifulSoup(r.text, "xml")
            items = soup.find_all("item")[:5]
            if not items:
                return f"No news found for {topic}, Sir."
            headlines = [item.find("title").text for item in items if item.find("title")]
            result = f"Latest news on {topic}, Sir: "
            result += ". Next: ".join(headlines[:3])
            return result
        except Exception as e:
            return f"News feed unavailable: {e}"

    # ═══════════════════════════════════════
    #  YOUTUBE VIDEO DOWNLOADER
    # ═══════════════════════════════════════
    @staticmethod
    def download_video(url: str, audio_only: bool = False) -> str:
        """Downloads video or audio from YouTube or any supported site."""
        try:
            print(f"\n📥 [NOKE Download]: Starting {'audio' if audio_only else 'video'} download...")
            output_template = os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s")

            cmd = ["python", "-m", "yt_dlp", "--no-warnings", "-o", output_template]

            if audio_only:
                cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
            else:
                cmd += ["-f", "bestvideo[height<=1080]+bestaudio/best"]

            cmd.append(url)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                action = "Audio extracted" if audio_only else "Video downloaded"
                return (f"{action} successfully, Sir. "
                        f"Saved to the noke_downloads folder on your desktop.")
            else:
                err = result.stderr.strip()[:150]
                return f"Download encountered an issue: {err}"

        except FileNotFoundError:
            return "yt-dlp is not installed. Run: python -m pip install yt-dlp"
        except subprocess.TimeoutExpired:
            return "Download timed out. Try a shorter video or check your connection."
        except Exception as e:
            return f"Download failed: {e}"

    # ═══════════════════════════════════════
    #  YOUTUBE SEARCH (No download)
    # ═══════════════════════════════════════
    @staticmethod
    def search_youtube(query: str) -> str:
        """Searches YouTube and returns top video titles and links."""
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ','+')}"
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(search_url, headers=headers, timeout=8)
            # Extract video IDs from page source
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
            titles    = re.findall(r'"title":{"runs":\[{"text":"([^"]+)"', r.text)
            if not video_ids or not titles:
                return f"YouTube search for {query} returned no results, Sir."
            result = f"Top YouTube results for {query}, Sir: "
            for i in range(min(3, len(titles))):
                vid_id = video_ids[i] if i < len(video_ids) else ""
                result += f"{i+1}. {titles[i]} — youtube.com/watch?v={vid_id}. "
            return result
        except Exception as e:
            return f"YouTube search failed: {e}"

    # ═══════════════════════════════════════
    #  GENERAL DEEP SEARCH
    # ═══════════════════════════════════════
    @staticmethod
    def deep_search(query: str) -> str:
        """Searches + reads the top result fully for maximum detail."""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(
                f"https://html.duckduckgo.com/html/?q={query.replace(' ','+')}",
                headers=headers, timeout=8
            )
            soup = BeautifulSoup(r.text, "html.parser")
            results = soup.select(".result__snippet")[:3]
            if not results:
                return f"Deep search for {query} found no snippets, Sir."
            combined = " | ".join([r.get_text(strip=True) for r in results])
            return f"Deep search results for {query}: {combined[:500]}"
        except Exception as e:
            return f"Deep search failed: {e}"