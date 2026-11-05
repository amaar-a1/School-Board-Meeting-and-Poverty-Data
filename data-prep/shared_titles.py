"""The monthly refresh's title lists (see refresh_youtube.py)."""
import json, os

def shared_titles():
    """Titles from the monthly refresh (refresh_youtube.py), newer than the build's own lists."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", "youtube_titles.json")
    return json.load(open(p, encoding="utf-8"))["titles"] if os.path.exists(p) else {}
