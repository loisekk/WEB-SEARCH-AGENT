from InquirerPy import inquirer
from googleapiclient.discovery import build

YOUTUBE_API_KEY = "AIzaSyCHHHpPjptqoIhwSsjsdprf2t7VQy-nGtU"
GOOGLE_API_KEY = "AIzaSyC6NQI4Vt4TVZHquAaj0LvpvR0fjs5qi-M"

def choose_to_entertain():
    platforms = ["youtube", "bing", "google", "reddit", "instragram"]
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

    platform = inquirer.select(
        message="🌐 Select platform:",
        choices=platforms
    ).execute()

    category = inquirer.select(
        message=f"🎯 Select category for {platform}:",
        choices=categories
    ).execute()

    return platform, category



def f1_flow():
    years = list(range(2000, 2026))

    grand_prix = [
        "ABU DHABI GRAND PRIX 🏎️", "SAO PAULO GRAND PRIX 🏎️",
        "MONACO GRAND PRIX 🏎️", "BRITISH GRAND PRIX 🏎️",
        "LAS VEGAS GRAND PRIX 🏎️", "MIAMI GRAND PRIX 🏎️",
        "AUSTRALIAN GRAND PRIX 🏎️", "ITALIAN GRAND PRIX 🏎️",
        "BELGIAN GRAND PRIX 🏎️", "SINGAPORE GRAND PRIX 🏎️",
        "CHINESE GRAND PRIX 🏎️", "SAUDI ARABIAN GRAND PRIX 🏎️",
        "EMILIA GRAND PRIX 🏎️", "DUTCH GRAND PRIX 🏎️",
        "HUNGARIAN GRAND PRIX 🏎️", "BAHRAIN GRAND PRIX 🏎️",
        "AZERBAIJAN GRAND PRIX 🏎️", "UNITED STATES GRAND PRIX 🏎️",
        "QATAR GRAND PRIX 🏎️"
    ]

    stages = ["SPRINT QUALIFYING", "SPRINT", "QUALIFYING", "RACE"]

    year = inquirer.select("📅 Choose F1 year:", years).execute()
    gp = inquirer.select(f"🏁 Choose GP ({year}):", grand_prix).execute()
    stage = inquirer.select(f"🚦 Choose stage for {gp} {year}:", stages).execute()

    return {"year": year, "grand_prix": gp, "stage": stage}



def anime_flow():
    anime_titles = [
        "DRAGON BALL", "NARUTO", "ONE PIECE","BLEACH",
        "DEMON SLAYER", "JUJUTSU KAISEN", "SOLO LEVELING" , "ATTACK ON TITAN", 
        "MY HERO ACADEMIA" ,"CHAINSAW MAN", "HUNTER X HUNTER" ,"ONE PUNCH MAN" ,"CLASS ROOM OF THE ELITE", "DAN - DA - DAN", "SPY X FAMILY",
        "GINTAMA","DEATH NOTE" , "BLUE LOCK" , "SAKAMOTO DAYS" , "WIND BREACKER","DR. STONE" ,"SEVEN DEADLY SINS", "TOKOYO REVENGERS","TOKOYO GOUL","RE ZERO",
        "KAGUYA SAMA","GACHIA GUTA" ,"MUSHOKO TENSAI" ,"HAJIME NO IPPO" , "HAIKYU" ,"DAYS WITH MY STEP ONII-SAN",
        "MOOB PHYCHO 100" ,"YOUR NAME" ,"FIVE CENTIMETER PER SECOND" ,"WEATHERING WITH YOU","SPRITED AWAY","BLUE BOX",
        "KAIJU NO. 8","VINLAND SAGA" ,"BLACK CLOVER" ,"FREEREN" ,"ASSASSINATION CLASSROOM",
        "I WANT TO EAT YOUR PANCREASE" ,"SLIENT VOICE","FIRE FLISE" ,"GRAND BLUE" ,"HORIMIA" ,"THE DANGERS IN MY HEART"
    ]
    sections = ["INTRO", "SEASON", "CLIPS" ,"TRAILOR" ,"MOVIES"]

    anime = inquirer.select("🍥 Choose Anime:", anime_titles).execute()
    section = inquirer.select(f"📺 What from {anime}?", sections).execute()

    return {"anime": anime, "section": section}



def movie_flow():
    movies = [
        "IRON MAN", "CARS", "AVENGERS",
        "END GAME", "INTERSTELLAR", "DEMON SLAYER"
    ]
    sections = ["ACTIONS", "CLIPS"]

    movie = inquirer.select("🎬 Choose Movie:", movies).execute()
    section = inquirer.select(f"🎞 What from {movie}?", sections).execute()

    return {"movie": movie, "section": section}



def web_series_flow():
    web_series = [
        "INVINCIBLE", "THE BOYS", "STRANGER THINGS",
        "ALICE IN BORDERLAND", "GAME OF THRONE", "MONEY HEIST",
        "BREAKING BAD", "BLOOD HOUND", "WEAK HERO", "MOON NIGHT",
        "LOKI", "THE WITCHER", "PEAKY BLINDER"
    ]
    sections = ["SEASON", "CLIPS", "INTRO", "HIGHEST RATED SCENE"]

    series = inquirer.select("📺 Choose Web Series:", web_series).execute()
    section = inquirer.select(f"🎞 What from {series}?", sections).execute()

    return {"web_series": series, "section": section}



def gaming_flow():
    gaming = [
        "DELTA FORCE", "ELDEN RING", "DARK SOUL",
        "BATTLE FIELD 6", "RESIDENT EVIL", "DEMON SLAYER",
        "BLACK OPPS 6", "HORROR TYPE", "MINECRAFT", "GOD OF WAR",
        "RED DEAD REDEMPTION 2", "ASSASSIN'S CREED", "GTA 5",
        "WARZONE"
    ]
    sections = [
        "ACTION SCENES", "CLIPS", "WATCH LIVE STREAM",
        "SEE FULL STORY", "CAMPAIGN", "CUT SCENE"
    ]

    game = inquirer.select("🎮 Choose Game:", gaming).execute()
    section = inquirer.select(f"🕹 What from {game}?", sections).execute()

    return {"game": game, "section": section}



def animations_flow():
    animations = [
        "UFOTABLE", "MAPPA", "FAN MADE", "PIXAR STUDIOS", "SONY",
        "GHIBLI ANIMATONS", "ILLUMINATION", "TOEI ANIMATIONS",
        "DREAM WORK", "WIT STUDIOS"
    ]
    sections = ["ACTION SCENES", "CLIPS", "WATCH LIVE STREAM", "ANIME", "2D ANI", "CUT SCENE"]

    animation = inquirer.select("🎨 Choose Animation:", animations).execute()
    section = inquirer.select(f"🎞 What from {animation}?", sections).execute()

    return {"animation": animation, "section": section}



def cartoons_flow():
    cartoons = [
        "OGGY AND THE CROCKROACHES", "PAKADAM PAKADAI",
        "PENGUINS AND THE MADAGASCAR", "GON", "DOREMON",
        "SPIDER MAN", "CHOTA BHEEM", "BEN 10", "COW AND CHICKEN",
        "ADVENTURE TIME", "WE BARE BEARS", "PAW PETROLS",
        "MICKEY MOUSE", "BANDBUDH AND BUDHBAK", "MOTU PATLU",
        "LITTLE KRISHNA", "BAHUBBALI THE LOST LEGEND",
        "BUNTY BILLA AUR BABBAN", "KEYMON ACHE", "SUPER BHEEM"
    ]
    sections = [
        "ACTION SCENES", "CLIPS", "WATCH LIVE STREAM",
        "2D ANI", "3D ANI", "CUT SCENE", "HIGHEST RATED SCENE"
    ]

    cartoon = inquirer.select("🐭 Choose Cartoon:", cartoons).execute()
    section = inquirer.select(f"😂 What from {cartoon}?", sections).execute()

    return {"cartoon": cartoon, "section": section}


def study_flow():
    study = [
        "CODING STUFF", "WEB DEV PART", "PYTHON MODULES", "JAVA", "C++",
        "JAVASCRIPT", "HTML_CSS", "DJANGO", "FRONTEND", "BACKEND",
        "SUPABASE", "GIT", "GITHUB", "LINKDIN", "RGPV NOTES",
        "SCRTCH PROJECTS", "MCP SERVERS", "OPEN ROUTER", "CODE DEX",
        "DEVFOLIO", "HAKATHOAN", "TECH STUFF", "PC STUFF",
        "ARTIFICIAL INTELLIGENCE", "LIBERARYS OF PYTHON",
        "DEEP LEARNING", "AGENTIC AI", "MODELS",
        "MACHINE LEARNING", "PROJECTS", "REPOSITORIES",
        "GO", "RUST", "RUBY", "C", "SQL", "LEET CODE STUFFS",
        "HACKER-RANK", "FAST API"
    ]
    levels = ["BEGINNERS", "INTERMEDIATE", "PROFESSIONAL", "EXPERIENCED"]

    topic = inquirer.select("📘 Choose Study Topic:", study).execute()
    level = inquirer.select(f"🎓 Level for {topic}:", levels).execute()

    return {"study_topic": topic, "level": level}



def build_query(agent_state):
    return " ".join(str(v) for v in agent_state.values())



def youtube_search(query):
    yt = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    req = yt.search().list(q=query, part="snippet", maxResults=5, type="video")
    res = req.execute()

    print("\n📺 YouTube Results:\n")
    for item in res["items"]:
        print("▶", item["snippet"]["title"])
        print("https://www.youtube.com/watch?v=" + item["id"]["videoId"], "\n")

# def youtube_search(query):
#     try:
#         yt = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
#         req = yt.search().list(
#             q=query,
#             part="snippet",
#             maxResults=5,
#             type="video"
#         )
#         res = req.execute()

#         print("\n📺 YouTube Results:\n")
#         for item in res.get("items", []):
#             print("▶", item["snippet"]["title"])
#             print("https://www.youtube.com/watch?v=" + item["id"]["videoId"], "\n")

#     except Exception as e:
#         print("❌ YouTube API Error:", e)


def youtube_search(query):
    try:
        yt = build("youtube" , "v3" , developerKey=YOUTUBE_API_KEY)
        req = yt.search().list(
            q = query,
            part ="snippet",
            maxresults = 5,
            type = "video"
        )
        res = req.execute()

        print("\n youtube results:\n")
        for item in res.get("item", []):
            print("v", item["snippet"]["tittle"])
            print("https://www.youtube.com/watch?v=" + item["id"]["videoId"] , "\n")

    except Exception as e:
        print("youtube api key is wrong")

def web_search_agent():
    print("\n🤖 Web Search AI Agent Initialized\n")

    platform, category = choose_to_entertain()
    agent_state = {"platform": platform, "category": category}

    if platform == "youtube":
        if category == "F1":
            agent_state.update(f1_flow())
        elif category == "ANIME":
            agent_state.update(anime_flow())
        elif category == "MOVIES":
            agent_state.update(movie_flow())
        elif category == "WEB-SERIES":
            agent_state.update(web_series_flow())
        elif category == "GAMING-VIDEOS":
            agent_state.update(gaming_flow())
        elif category == "ANIMATIONS":
            agent_state.update(animations_flow())
        elif category == "CARTOONS":
            agent_state.update(cartoons_flow())
        elif category == "STUDY-STUFF":
            agent_state.update(study_flow())
            
    if platform == "bing":
        if category == "F1":
            agent_state.update(f1_flow())
        elif category == "ANIME":
            agent_state.update(anime_flow())
        elif category == "MOVIES":
            agent_state.update(movie_flow())
        elif category == "WEB-SERIES":
            agent_state.update(web_series_flow())
        elif category == "GAMING-VIDEOS":
            agent_state.update(gaming_flow())
        elif category == "ANIMATIONS":
            agent_state.update(animations_flow())
        elif category == "CARTOONS":
            agent_state.update(cartoons_flow())
        elif category == "STUDY-STUFF":
            agent_state.update(study_flow())

    if platform == "google":
        if category == "F1":
            agent_state.update(f1_flow())
        elif category == "ANIME":
            agent_state.update(anime_flow())
        elif category == "MOVIES":
            agent_state.update(movie_flow())
        elif category == "WEB-SERIES":
            agent_state.update(web_series_flow())
        elif category == "GAMING-VIDEOS":
            agent_state.update(gaming_flow())
        elif category == "ANIMATIONS":
            agent_state.update(animations_flow())
        elif category == "CARTOONS":
            agent_state.update(cartoons_flow())
        elif category == "STUDY-STUFF":
            agent_state.update(study_flow())

    if platform == "reddit":
        if category == "F1":
            agent_state.update(f1_flow())
        elif category == "ANIME":
            agent_state.update(anime_flow())
        elif category == "MOVIES":
            agent_state.update(movie_flow())
        elif category == "WEB-SERIES":
            agent_state.update(web_series_flow())
        elif category == "GAMING-VIDEOS":
            agent_state.update(gaming_flow())
        elif category == "ANIMATIONS":
            agent_state.update(animations_flow())
        elif category == "CARTOONS":
            agent_state.update(cartoons_flow())
        elif category == "STUDY-STUFF":
            agent_state.update(study_flow())

    if platform == "instagram":
        if category == "F1":
            agent_state.update(f1_flow())
        elif category == "ANIME":
            agent_state.update(anime_flow())
        elif category == "MOVIES":
            agent_state.update(movie_flow())
        elif category == "WEB-SERIES":
            agent_state.update(web_series_flow())
        elif category == "GAMING-VIDEOS":
            agent_state.update(gaming_flow())
        elif category == "ANIMATIONS":
            agent_state.update(animations_flow())
        elif category == "CARTOONS":
            agent_state.update(cartoons_flow())
        elif category == "STUDY-STUFF":
            agent_state.update(study_flow())

    query = build_query(agent_state)
    print("\n🔎 Generated Search Query:\n", query)

    if platform == "youtube":
        youtube_search(query)
  


if __name__ == "__main__":
    web_search_agent()
