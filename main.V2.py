import os
import re
from time import sleep
from dotenv import load_dotenv
from InquirerPy import inquirer

# Selenium for YouTube automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Google Custom Search API
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX_ID = os.getenv("GOOGLE_CX_ID")


# ================= CLEAN QUERY =================
def clean_query(text):
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


# ================= YOUTUBE AUTOMATION =================
def open_youtube_and_play(search_query):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://www.youtube.com")

        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "search_query"))
        )
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.ENTER)

        first_video = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '(//ytd-video-renderer//a[@id="video-title"])[1]')
            )
        )

        print("\n▶ Playing:", first_video.text)
        first_video.click()

        sleep(60)

    except Exception as e:
        print("❌ YouTube Automation Error:", e)


# ================= GOOGLE SEARCH (TERMINAL RESULTS) =================
def google_search_terminal():
    print("\n" + "=" * 60)
    print("🔍 GOOGLE SEARCH".center(60))
    print("=" * 60)

    query = input("│  Enter Search Query: ").strip()

    if not query:
        print("❌ Empty query.")
        return

    if not GOOGLE_API_KEY or not GOOGLE_CX_ID:
        print("❌ Missing GOOGLE_API_KEY or GOOGLE_CX_ID")
        return

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)

        res = service.cse().list(
            q=query,
            cx=GOOGLE_CX_ID,
            num=5
        ).execute()

        print("\n📄 GOOGLE RESULTS:\n")

        for item in res.get("items", []):
            print("▶", item["title"])
            print(item["link"])
            print("-" * 60)

    except HttpError as e:
        print(f"❌ Google API Error: {e}")


# ================= CATEGORY FLOWS =================
def choose_platform():
    return inquirer.select(
        message="🌐 Select Platform:",
        choices=["YOUTUBE (Automated)", "GOOGLE (Terminal Search)"]
    ).execute()


def choose_category():
    return inquirer.select(
        message="🎯 Select Category:",
        choices=[
            "F1", "ANIME", "MOVIES", "WEB-SERIES",
            "GAMING-VIDEOS", "ANIMATIONS",
            "CARTOONS", "STUDY-STUFF"
        ]
    ).execute()


def f1_flow():
    years = list(range(2000, 2026))
    gps = [
        "ABU DHABI GRAND PRIX", "MONACO GRAND PRIX",
        "BRITISH GRAND PRIX", "ITALIAN GRAND PRIX"
    ]
    stages = ["SPRINT QUALIFYING", "QUALIFYING", "RACE"]

    year = inquirer.select("📅 Choose Year:", years).execute()
    gp = inquirer.select("🏁 Choose Grand Prix:", gps).execute()
    stage = inquirer.select("🚦 Choose Stage:", stages).execute()

    return f"F1 {year} {gp} {stage}"


def anime_flow():
    anime = inquirer.select(
        "🍥 Choose Anime:",
        ["NARUTO", "ONE PIECE", "DEMON SLAYER", "ATTACK ON TITAN"]
    ).execute()

    section = inquirer.select(
        "📺 Choose Section:",
        ["INTRO", "SEASON", "CLIPS", "TRAILER"]
    ).execute()

    return f"{anime} {section}"


def movie_flow():
    movie = inquirer.select(
        "🎬 Choose Movie:",
        ["INTERSTELLAR", "AVENGERS", "YOUR NAME"]
    ).execute()

    return f"{movie} trailer"


def web_series_flow():
    series = inquirer.select(
        "📺 Choose Series:",
        ["INVINCIBLE", "THE BOYS", "STRANGER THINGS"]
    ).execute()

    return f"{series} season"


def gaming_flow():
    game = inquirer.select(
        "🎮 Choose Game:",
        ["GTA 5", "ELDEN RING", "WARZONE"]
    ).execute()

    return f"{game} gameplay"


def animations_flow():
    return inquirer.select(
        "🎨 Choose Animation Studio:",
        ["MAPPA", "UFOTABLE", "PIXAR"]
    ).execute()


def cartoons_flow():
    return inquirer.select(
        "🐭 Choose Cartoon:",
        ["BEN 10", "OGGY", "SPIDER MAN"]
    ).execute()


def study_flow():
    topic = inquirer.select(
        "📘 Choose Topic:",
        ["PYTHON", "FAST API", "SUPABASE"]
    ).execute()

    return f"{topic} tutorial"


# ================= MAIN AGENT =================
def web_search_agent():
    print("\n🤖 Web Search AI Agent Started\n")

    platform = choose_platform()

    if platform.startswith("GOOGLE"):
        google_search_terminal()
        return

    # YouTube Automation Flow
    category = choose_category()

    if category == "F1":
        query = f1_flow()
    elif category == "ANIME":
        query = anime_flow()
    elif category == "MOVIES":
        query = movie_flow()
    elif category == "WEB-SERIES":
        query = web_series_flow()
    elif category == "GAMING-VIDEOS":
        query = gaming_flow()
    elif category == "ANIMATIONS":
        query = animations_flow()
    elif category == "CARTOONS":
        query = cartoons_flow()
    elif category == "STUDY-STUFF":
        query = study_flow()
    else:
        return

    final_query = clean_query(query)

    print("\n🔎 Searching on YouTube:", final_query)
    open_youtube_and_play(final_query)


# ================= RUN =================
if __name__ == "__main__":
    web_search_agent()

