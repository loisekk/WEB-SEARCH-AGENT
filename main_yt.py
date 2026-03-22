import os
import re
from InquirerPy import inquirer
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ================= CONFIG =================
YOUTUBE_API_KEY = "AIzaSyCHHHpPjptqoIhwSsjsdprf2t7VQy-nGtU"
# =========================================


# ---------- Helpers ----------
def clean_query(text: str) -> str:
    return re.sub(r"[^\x00-\x7F]+", "", text)


def youtube_search(query, max_results=5):
    try:
        yt = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        request = yt.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results
        )

        response = request.execute()

        print("\n📺 YouTube Results:\n")
        for i, item in enumerate(response["items"], start=1):
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            url = f"https://www.youtube.com/watch?v={video_id}"

            print(f"{i}. {title}")
            print(f"   🔗 {url}\n")

    except HttpError as e:
        print(f"❌ YouTube API Error: {e}")


# ---------- Platform & Category ----------
def choose_category():
    categories = [
        "F1",
        "ANIME",
        "MOVIES",
        "WEB-SERIES",
        "GAMING-VIDEOS",
        "ANIMATIONS",
        "CARTOONS",
        "STUDY-STUFF"
    ]

    return inquirer.select(
        message="🎯 Select YouTube Category:",
        choices=categories
    ).execute()


# ---------- F1 ----------
def f1_flow():
    years = list(range(2000, 2027))

    grand_prix = [
        "ABU DHABI GRAND PRIX 🏎️",
        "SAO PAULO GRAND PRIX 🏁",
        "MONACO GRAND PRIX 🏎️",
        "BRITISH GRAND PRIX 🇬🇧",
        "LAS VEGAS GRAND PRIX 🎰",
        "MIAMI GRAND PRIX 🌴",
        "ITALIAN GRAND PRIX 🇮🇹",
        "BELGIAN GRAND PRIX 🇧🇪",
        "SINGAPORE GRAND PRIX 🇸🇬"
    ]

    stages = ["SPRINT QUALIFYING", "SPRINT", "QUALIFYING", "RACE"]

    year = inquirer.select("📅 Choose F1 Year:", years).execute()
    gp = inquirer.select(f"🏁 Choose GP ({year}):", grand_prix).execute()
    stage = inquirer.select(f"🚦 Choose Stage ({year} {gp}):", stages).execute()

    return f"F1 {year} {gp} {stage}"


# ---------- Generic Flow ----------
def simple_flow(title, items, suffix):
    choice = inquirer.select(f"Select {title}:", items).execute()
    return f"{choice} {suffix}"


# ---------- Main Agent ----------
def web_search_agent():
    print("\n🤖 YouTube Web Search Agent Initialized\n")

    category = choose_category()

    if category == "F1":
        query = f1_flow()

    elif category == "ANIME":
        query = simple_flow(
            "Anime",
            [
                "DRAGON BALL", "NARUTO", "ONE PIECE","BLEACH",
        "DEMON SLAYER", "JUJUTSU KAISEN", "SOLO LEVELING" , "ATTACK ON TITAN", 
        "MY HERO ACADEMIA" ,"CHAINSAW MAN", "HUNTER X HUNTER" ,"ONE PUNCH MAN" ,"CLASS ROOM OF THE ELITE", "DAN - DA - DAN", "SPY X FAMILY",
        "GINTAMA","DEATH NOTE" , "BLUE LOCK" , "SAKAMOTO DAYS" , "WIND BREACKER","DR. STONE" ,"SEVEN DEADLY SINS", "TOKOYO REVENGERS","TOKOYO GOUL","RE ZERO",
        "KAGUYA SAMA","GACHIA GUTA" ,"MUSHOKO TENSAI" ,"HAJIME NO IPPO" , "HAIKYU" ,"DAYS WITH MY STEP ONII-SAN",
        "MOOB PHYCHO 100" ,"YOUR NAME" ,"FIVE CENTIMETER PER SECOND" ,"WEATHERING WITH YOU","SPRITED AWAY","BLUE BOX",
        "KAIJU NO. 8","VINLAND SAGA" ,"BLACK CLOVER" ,"FREEREN" ,"ASSASSINATION CLASSROOM",
        "I WANT TO EAT YOUR PANCREASE" ,"SLIENT VOICE","FIRE FLISE" ,"GRAND BLUE" ,"HORIMIA" ,"THE DANGERS IN MY HEART"
            ],
            "best clips"
        )

    elif category == "MOVIES":
        query = simple_flow(
            "Movie",
            ["IRON MAN", "AVENGERS", "INTERSTELLAR", "END GAME", "CARS"],
            "best scenes"
        )

    elif category == "WEB-SERIES":
        query = simple_flow(
            "Web Series",
            ["BREAKING BAD", "DARK", "MONEY HEIST", "LOKI", "THE BOYS"],
            "best moments"
        )

    elif category == "GAMING-VIDEOS":
        query = simple_flow(
            "Game",
            [
                "GTA 5", "ELDEN RING", "GOD OF WAR",
                "RED DEAD REDEMPTION 2", "MINECRAFT"
            ],
            "gameplay"
        )

    elif category == "ANIMATIONS":
        query = "Best animation short films"

    elif category == "CARTOONS":
        query = "Best cartoon episodes clips"

    elif category == "STUDY-STUFF":
        query = simple_flow(
            "Study Topic",
            [
                "PYTHON", "JAVA", "C++", "JAVASCRIPT",
                "AI", "MACHINE LEARNING", "DATA STRUCTURES"
            ],
            "tutorial"
        )

    else:
        print("❌ Invalid category")
        return

    print("\n🔎 Search Query:")
    print(query)

    youtube_search(clean_query(query))


# ---------- Run ----------
if __name__ == "__main__":
    web_search_agent()
