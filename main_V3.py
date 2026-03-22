"""
main_V3.py  —  Yash's Web Search AI Agent
──────────────────────────────────────────
• YOUTUBE  →  Writes query to .streamlit_query, auto-starts app.py (Streamlit),
              opens browser at http://localhost:8501  — NO manual 'streamlit run' needed
• GOOGLE   →  Terminal results with snippet preview + open in browser
"""

import os
import re
import sys
import time
import signal
import subprocess
import webbrowser
from dotenv import load_dotenv

# InquirerPy
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

# Google Custom Search API
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyC6NQI4Vt4TVZHquAaj0LvpvR0fjs5qi-M")
GOOGLE_CX_ID   = os.getenv("GOOGLE_CX_ID",   "b11c8dec6844f4432")

QUERY_FILE      = ".streamlit_query"    # handoff file for Streamlit
STREAMLIT_PORT  = 8501
STREAMLIT_URL   = f"http://localhost:{STREAMLIT_PORT}"
APP_FILE        = "app.py"              # must be in same folder as this script

# ─────────────────────────────────────────────
#  CONTENT LIBRARY
# ─────────────────────────────────────────────
CONTENT = {
    "F1": {
        "years":  list(range(2025, 1999, -1)),
        "gps": [
            "ABU DHABI GRAND PRIX", "MONACO GRAND PRIX",
            "BRITISH GRAND PRIX",   "ITALIAN GRAND PRIX",
            "BAHRAIN GRAND PRIX",   "SINGAPORE GRAND PRIX",
            "JAPANESE GRAND PRIX",  "UNITED STATES GRAND PRIX",
            "SAO PAULO GRAND PRIX", "BELGIAN GRAND PRIX",
        ],
        "stages": ["RACE", "QUALIFYING", "SPRINT QUALIFYING", "SPRINT RACE", "HIGHLIGHTS"],
    },
    "ANIME": {
        "titles": [
            "NARUTO", "ONE PIECE", "DEMON SLAYER", "ATTACK ON TITAN",
            "JUJUTSU KAISEN", "VINLAND SAGA", "BLUE LOCK",
            "DRAGON BALL Z", "FULLMETAL ALCHEMIST BROTHERHOOD", "DEATH NOTE",
        ],
        "sections": ["INTRO / OP", "FULL EPISODE", "BEST CLIPS", "TRAILER", "OST / SOUNDTRACK"],
    },
    "MOVIES": {
        "titles": [
            "INTERSTELLAR", "AVENGERS ENDGAME", "YOUR NAME",
            "INCEPTION", "THE DARK KNIGHT", "OPPENHEIMER",
            "SPIRITED AWAY", "DUNE PART TWO", "PARASITE",
        ],
        "types": ["OFFICIAL TRAILER", "FULL MOVIE", "REVIEW", "BEHIND THE SCENES", "CLIP"],
    },
    "WEB-SERIES": {
        "titles": [
            "INVINCIBLE", "THE BOYS", "STRANGER THINGS",
            "BREAKING BAD", "GAME OF THRONES", "SEVERANCE",
            "HOUSE OF THE DRAGON", "ARCANE",
        ],
        "types": ["SEASON TRAILER", "BEST MOMENTS", "REVIEW", "RECAP", "EPISODE CLIP"],
    },
    "GAMING": {
        "titles": [
            "GTA 5", "GTA 6", "ELDEN RING", "WARZONE",
            "MINECRAFT", "VALORANT", "RED DEAD REDEMPTION 2",
            "CYBERPUNK 2077", "THE LAST OF US",
        ],
        "types": ["GAMEPLAY", "WALKTHROUGH", "TIPS & TRICKS", "TRAILER", "SPEEDRUN"],
    },
    "ANIMATIONS": {
        "studios": [
            "MAPPA", "UFOTABLE", "PIXAR", "STUDIO GHIBLI",
            "WIT STUDIO", "KYOTO ANIMATION", "A-1 PICTURES",
        ],
        "types": ["BEST SCENES", "TRAILER", "BEHIND THE SCENES", "AMV"],
    },
    "CARTOONS": {
        "titles": [
            "BEN 10", "OGGY AND THE COCKROACHES", "SPIDER-MAN",
            "TOM AND JERRY", "GRAVITY FALLS", "RICK AND MORTY",
            "AVATAR THE LAST AIRBENDER", "THE SIMPSONS",
        ],
        "types": ["FULL EPISODE", "BEST MOMENTS", "TRAILER"],
    },
    "STUDY": {
        "topics": [
            "PYTHON", "FASTAPI", "SUPABASE", "MACHINE LEARNING",
            "DEEP LEARNING", "REACT", "NEXT.JS", "DSA IN PYTHON",
            "SYSTEM DESIGN", "DOCKER", "KUBERNETES", "GIT & GITHUB",
        ],
        "types": ["FULL TUTORIAL", "CRASH COURSE", "PROJECT BUILD", "EXPLAINED IN 10 MINS"],
    },
    "MUSIC": {
        "genres": [
            "LOFI HIP HOP", "PHONK", "EDM", "BOLLYWOOD HITS",
            "ANIME OST", "CODING PLAYLIST", "JAZZ",
        ],
        "types": ["PLAYLIST", "MIX", "TOP SONGS 2024", "LIVE PERFORMANCE"],
    },
    "CUSTOM": {},
}

PLATFORM_CHOICES = [
    Choice(value="YOUTUBE",  name="📺  YouTube  — Watch inside Streamlitp web viewer"),
    Choice(value="GOOGLE",   name="🔍  Google   — Search results in terminal"),
    Choice(value="reddit",   name ="📟 Reddit   -- Search result in web page ")
]

CATEGORY_CHOICES = [
    Separator("── Entertainment ──────────────────"),
    Choice(value="ANIME",       name="🍥  Anime"),
    Choice(value="MOVIES",      name="🎬  Movies"),
    Choice(value="WEB-SERIES",  name="📺  Web Series"),
    Choice(value="CARTOONS",    name="🐭  Cartoons"),
    Choice(value="ANIMATIONS",  name="🎨  Animations"),
    Separator("── Sports & Gaming ────────────────"),
    Choice(value="F1",          name="🏎️  Formula 1"),
    Choice(value="GAMING",      name="🎮  Gaming"),
    Separator("── Knowledge & Music ───────────────"),
    Choice(value="STUDY",       name="📘  Study / Tutorials"),
    Choice(value="MUSIC",       name="🎵  Music"),
    Separator("── Other ──────────────────────────"),
    Choice(value="CUSTOM",      name="✏️  Custom Search Query"),
]


# ─────────────────────────────────────────────
#  STREAMLIT MANAGER
# ─────────────────────────────────────────────

_streamlit_proc: subprocess.Popen | None = None   # global handle


def _streamlit_running() -> bool:
    """Check if our Streamlit process is alive."""
    return _streamlit_proc is not None and _streamlit_proc.poll() is None


def _start_streamlit():
    """Launch app.py as a background Streamlit process."""
    global _streamlit_proc

    if _streamlit_running():
        return   # already up

    # Resolve app.py path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path   = os.path.join(script_dir, APP_FILE)

    if not os.path.exists(app_path):
        print(f"\n  ❌  Cannot find {APP_FILE} — make sure it's in the same folder as this script.")
        return

    print(f"\n  🚀 Starting Streamlit viewer (app.py) …")

    # Launch streamlit as a subprocess, suppress its console output
    _streamlit_proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port",        str(STREAMLIT_PORT),
            "--server.headless",    "true",     # don't auto-open browser (we do it ourselves)
            "--browser.gatherUsageStats", "false",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        # Windows needs this to avoid a new console window popping up
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )

    # Wait up to 8 seconds for Streamlit to be ready
    print("  ⏳ Waiting for Streamlit to be ready", end="", flush=True)
    for _ in range(16):
        time.sleep(0.5)
        print(".", end="", flush=True)
        # Simple TCP probe
        import socket
        try:
            with socket.create_connection(("localhost", STREAMLIT_PORT), timeout=1):
                break
        except OSError:
            continue
    print(" ✅")


def _send_query_to_streamlit(query: str):
    """Write query to the handoff file so Streamlit picks it up."""
    with open(QUERY_FILE, "w") as f:
        f.write(query)


def _open_streamlit_browser():
    """Open the Streamlit page in the default browser."""
    webbrowser.open(STREAMLIT_URL)
    print(f"  🌐 Opened: {STREAMLIT_URL}")


def launch_streamlit_for_query(query: str):
    """Full flow: start Streamlit (if needed) → send query → open browser."""
    _send_query_to_streamlit(query)
    _start_streamlit()
    _open_streamlit_browser()
    print(f"\n  📺 Watching: \033[1;32m{query}\033[0m")
    print("  💡 Streamlit is running in the background.")
    print("  💡 Keep this terminal open. Press Ctrl+C here to quit the agent.\n")


def _shutdown_streamlit():
    """Kill Streamlit process on agent exit."""
    global _streamlit_proc
    if _streamlit_running():
        print("\n  🛑 Shutting down Streamlit …")
        if sys.platform == "win32":
            _streamlit_proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            _streamlit_proc.terminate()
        try:
            _streamlit_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _streamlit_proc.kill()
        _streamlit_proc = None
    # Clean up temp query file
    if os.path.exists(QUERY_FILE):
        os.remove(QUERY_FILE)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def banner():
    print("\n" + "═" * 64)
    print("  🤖  WEB SEARCH AI AGENT  v3.0".center(64))
    print("  Built by Yash Brahmankar".center(64))
    print("═" * 64 + "\n")


def clean_query(text: str) -> str:
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def confirm_and_run(query: str, platform: str):
    final = clean_query(query)
    print(f"\n  📌 Final Query : \033[1;36m{final}\033[0m")
    proceed = inquirer.confirm(message="  Launch search?", default=True).execute()
    if not proceed:
        print("  ↩  Cancelled.\n")
        return

    if platform == "YOUTUBE":
        launch_streamlit_for_query(final)
    else:
        google_search_terminal(final)


# ─────────────────────────────────────────────
#  GOOGLE SEARCH (TERMINAL)
# ─────────────────────────────────────────────

def google_search_terminal(query: str = ""):
    if not query:
        query = inquirer.text(message="  Enter search query:").execute().strip()
    if not query:
        print("  ❌  Empty query.\n")
        return

    if not GOOGLE_API_KEY or not GOOGLE_CX_ID:
        print("\n  ❌  GOOGLE_API_KEY or GOOGLE_CX_ID missing in .env\n")
        return

    num = inquirer.select(
        message="  Results to show:",
        choices=[
            Choice(value=3,  name="3  — Quick look"),
            Choice(value=5,  name="5  — Standard"),
            Choice(value=10, name="10 — Deep dive"),
        ],
        default=5,
    ).execute()

    print(f"\n  🔍 Fetching top {num} results for: \033[1;36m{query}\033[0m\n")

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res     = service.cse().list(q=query, cx=GOOGLE_CX_ID, num=num).execute()
        items   = res.get("items", [])

        if not items:
            print("  ⚠️  No results found.\n")
            return

        print("─" * 64)
        for idx, item in enumerate(items, 1):
            title   = item.get("title", "No Title")
            link    = item.get("link", "")
            snippet = item.get("snippet", "").replace("\n", " ")
            print(f"  \033[1;33m[{idx}]\033[0m \033[1m{title}\033[0m")
            print(f"       🔗 {link}")
            print(f"       📝 {snippet[:120]}{'…' if len(snippet) > 120 else ''}")
            print("─" * 64)

        open_one = inquirer.confirm(
            message="  Open a result in your browser?", default=False
        ).execute()
        if open_one:
            idx_choice = inquirer.select(
                message="  Which result?",
                choices=[
                    Choice(value=i, name=f"[{i}] {items[i-1]['title'][:60]}")
                    for i in range(1, len(items) + 1)
                ],
            ).execute()
            webbrowser.open(items[idx_choice - 1]["link"])
            print("  🌐 Opened in browser.\n")

    except HttpError as e:
        print(f"  ❌  Google API Error: {e}\n")
    except Exception as e:
        print(f"  ❌  Unexpected error: {e}\n")


# ─────────────────────────────────────────────
#  CATEGORY FLOWS
# ─────────────────────────────────────────────

def f1_flow() -> str:
    d = CONTENT["F1"]
    year  = inquirer.select("  📅 Year:",       choices=d["years"]).execute()
    gp    = inquirer.select("  🏁 Grand Prix:", choices=d["gps"]).execute()
    stage = inquirer.select("  🚦 Stage:",      choices=d["stages"]).execute()
    return f"F1 {year} {gp} {stage}"

def anime_flow() -> str:
    d     = CONTENT["ANIME"]
    title = inquirer.select("  🍥 Anime:",   choices=d["titles"]).execute()
    sec   = inquirer.select("  📺 Section:", choices=d["sections"]).execute()
    return f"{title} {sec}"

def movie_flow() -> str:
    d     = CONTENT["MOVIES"]
    title = inquirer.select("  🎬 Movie:", choices=d["titles"]).execute()
    typ   = inquirer.select("  📹 Type:",  choices=d["types"]).execute()
    return f"{title} {typ}"

def web_series_flow() -> str:
    d     = CONTENT["WEB-SERIES"]
    title = inquirer.select("  📺 Series:", choices=d["titles"]).execute()
    typ   = inquirer.select("  📹 Type:",   choices=d["types"]).execute()
    return f"{title} {typ}"

def gaming_flow() -> str:
    d     = CONTENT["GAMING"]
    title = inquirer.select("  🎮 Game:", choices=d["titles"]).execute()
    typ   = inquirer.select("  📹 Type:", choices=d["types"]).execute()
    return f"{title} {typ}"

def animations_flow() -> str:
    d      = CONTENT["ANIMATIONS"]
    studio = inquirer.select("  🎨 Studio:", choices=d["studios"]).execute()
    typ    = inquirer.select("  📹 Type:",   choices=d["types"]).execute()
    return f"{studio} ANIMATION {typ}"

def cartoons_flow() -> str:
    d     = CONTENT["CARTOONS"]
    title = inquirer.select("  🐭 Cartoon:", choices=d["titles"]).execute()
    typ   = inquirer.select("  📹 Type:",    choices=d["types"]).execute()
    return f"{title} {typ}"

def study_flow() -> str:
    d     = CONTENT["STUDY"]
    topic = inquirer.select("  📘 Topic:", choices=d["topics"]).execute()
    typ   = inquirer.select("  📹 Type:",  choices=d["types"]).execute()
    return f"{topic} {typ}"

def music_flow() -> str:
    d     = CONTENT["MUSIC"]
    genre = inquirer.select("  🎵 Genre:", choices=d["genres"]).execute()
    typ   = inquirer.select("  📹 Type:",  choices=d["types"]).execute()
    return f"{genre} {typ}"

def custom_flow() -> str:
    return inquirer.text(message="  ✏️  Enter your search query:").execute().strip()


FLOW_MAP = {
    "F1":          f1_flow,
    "ANIME":       anime_flow,
    "MOVIES":      movie_flow,
    "WEB-SERIES":  web_series_flow,
    "GAMING":      gaming_flow,
    "ANIMATIONS":  animations_flow,
    "CARTOONS":    cartoons_flow,
    "STUDY":       study_flow,
    "MUSIC":       music_flow,
    "CUSTOM":      custom_flow,
}


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────

def web_search_agent():
    banner()

    try:
        while True:
            platform = inquirer.select(
                message="  🌐 Select Platform:",
                choices=PLATFORM_CHOICES,
            ).execute()

            if platform == "GOOGLE":
                google_search_terminal()
            else:
                category = inquirer.select(
                    message="  🎯 Select Category:",
                    choices=CATEGORY_CHOICES,
                ).execute()

                flow_fn = FLOW_MAP.get(category)
                if not flow_fn:
                    print("  ⚠️  Unknown category.\n")
                    continue

                query = flow_fn()
                if query:
                    confirm_and_run(query, platform)

            again = inquirer.confirm(
                message="  🔁 Search again?", default=True
            ).execute()
            if not again:
                break

    except KeyboardInterrupt:
        pass

    finally:
        _shutdown_streamlit()
        print("\n  👋 Goodbye! — Yash's Web Search Agent v3.0\n")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    web_search_agent()
