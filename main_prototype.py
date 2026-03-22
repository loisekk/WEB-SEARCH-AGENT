import random
import matplotlib.pyplot as plt
from InquirerPy import inquirer

# ---------------- Platform + Category Selection ----------------

def choose_to_entertain():
    platforms = ["youtube", "bing", "google", "reddit", "steam"]
    categories = [
        "F1", "ANIME", "MOVIES",
        "WEB-SERIES", "GAMING-VIDEOS",
        "ANIMATIONS", "CARTOONS"
    ]

    platform = inquirer.select(
        message="🌐 Which platform do you want to search?",
        choices=platforms
    ).execute()

    category = inquirer.select(
        message=f"🎯 What do you want to search on {platform}?",
        choices=categories
    ).execute()

    print(f"\n🌐 Platform Selected: {platform}")
    print(f"🎯 Category Selected: {category}\n")

    return platform, category


# ---------------- F1 Search Flow (Year → Country → Stage) ----------------
def f1_flow():
    years = list(range(2000, 2026))

    # ✅ Expanded F1 Grand Prix List (includes your previous ones)
    grand_prix = [
        "ABU DHABI GP", "AUSTRALIAN GP", "BAHRAIN GP",
        "SAUDI ARABIAN GP", "CHINESE GP", "JAPANESE GP",
        "MONACO GP", "CANADIAN GP", "SPANISH GP",
        "AUSTRIAN GP", "BRITISH GP", "HUNGARIAN GP",
        "BELGIAN GP", "DUTCH GP", "ITALIAN GP",
        "SINGAPORE GP", "UNITED STATES GP",
        "MEXICAN GP", "SAO PAULO GP",
        "LAS VEGAS GP", "MIAMI GP", "QATAR GP"
    ]

    stages = ["SPRINT QUALIFYING", "SPRINT", "QUALIFYING", "RACE"]

    year = inquirer.select(
        message="🗓 Which F1 season do you want to watch?",
        choices=years
    ).execute()

    gp = inquirer.select(
        message=f"🏁 Select Grand Prix ({year})",
        choices=grand_prix
    ).execute()

    stage = inquirer.select(
        message=f"🚦 Select stage for {gp} {year}",
        choices=stages
    ).execute()

    print("\n🏎 F1 SELECTION CONFIRMED")
    print(f"🗓 Year       : {year}")
    print(f"🏁 Grand Prix: {gp}")
    print(f"🚦 Stage     : {stage}\n")

    return year, gp, stage


# ---------------- Anime Flow ----------------
def anime_flow():
    anime_section = [
        "DRAGON BALL", "NARUTO", "ONE PIECE",
        "DEMON SLAYER", "JUJUTSU KAISEN", "SOLO LEVELING"
    ]
    stages = ["INTRO", "SEASON", "CLIPS"]

    anime = inquirer.select(
        message="🍥 Which anime?",
        choices=anime_section
    ).execute()

    stage = inquirer.select(
        message=f"📺 What do you want from {anime}?",
        choices=stages
    ).execute()

    print(f"\n🎌 Anime Selected: {anime}")
    print(f"📺 Content Type: {stage}\n")

    return anime, stage


# ---------------- Movie Flow ----------------
def movie_flow():
    movies = [
        "IRON MAN", "CARS",
        "AVENGERS", "ENDGAME",
        "INTERSTELLAR"
    ]
    stages = ["ACTION SCENES", "CLIPS"]

    movie = inquirer.select(
        message="🎬 Which movie?",
        choices=movies
    ).execute()

    stage = inquirer.select(
        message=f"🎞 What do you want from {movie}?",
        choices=stages
    ).execute()

    print(f"\n🎬 Movie Selected: {movie}")
    print(f"🎞 Content Type: {stage}\n")

    return movie, stage


# ---------------- Web Search Agent Core ----------------
def web_search_agent():
    print("🤖 Web Search Agent Initialized\n")

    platform, category = choose_to_entertain()

    agent_state = {
        "platform": platform,
        "category": category
    }

    if platform == "youtube" and category == "F1":
        year, gp, stage = f1_flow()
        agent_state.update({
            "year": year,
            "grand_prix": gp,
            "stage": stage
        })

    elif platform == "youtube" and category == "ANIME":
        anime, stage = anime_flow()
        agent_state.update({
            "anime": anime,
            "stage": stage
        })

    elif platform == "youtube" and category == "MOVIES":
        movie, stage = movie_flow()
        agent_state.update({
            "movie": movie,
            "stage": stage
        })

    else:
        print("🔧 This search flow will be added soon.")

    print("🔎 Final Agent State (Ready for API):")
    print(agent_state)

    return agent_state


# ---------------- Run ----------------
if __name__ == "__main__":
    web_search_agent()
