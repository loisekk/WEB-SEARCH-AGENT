"""
app.py — Yash's YouTube Clone
Libraries:
  st.html(unsafe_allow_javascript=True) → injects setQ() into Streamlit parent page
  components.v1.html()                  → renders full HTML page (no React stripping)
  st_player                             → native video player, no embed errors
  st_lottie + @st.cache_data            → cached loading animation
  @st.cache_data on API calls           → 5min cache, no redundant fetches
  search_videos / search_shorts         → YouTube Data API v3
"""
import os, base64, glob, urllib.parse, json
import streamlit as st
import streamlit.components.v1 as components
from streamlit_player import st_player
from streamlit_lottie import st_lottie
import requests
from youtube_api import search_videos, search_shorts


QUERY_FILE = ".streamlit_query"
st.set_page_config(
    page_title="LOISEKK",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════
# CONTENT CATEGORIES
# ═══════════════════════════════════════════════════
CONTENT = {
    "F1":{"icon":"🏎️","gps":["ABU DHABI GRAND PRIX","MONACO GRAND PRIX","BRITISH GRAND PRIX","ITALIAN GRAND PRIX","BAHRAIN GRAND PRIX","SINGAPORE GRAND PRIX","JAPANESE GRAND PRIX","SAO PAULO GRAND PRIX"],"stages":["RACE","QUALIFYING","SPRINT RACE","HIGHLIGHTS"]},
    "ANIME":{"icon":"⛩️","titles":["NARUTO","ONE PIECE","DEMON SLAYER","ATTACK ON TITAN","JUJUTSU KAISEN","VINLAND SAGA","BLUE LOCK","DRAGON BALL Z","DEATH NOTE"],"sections":["INTRO / OP","FULL EPISODE","BEST CLIPS","TRAILER","OST"]},
    "MOVIES":{"icon":"🎬","titles":["INTERSTELLAR","AVENGERS ENDGAME","INCEPTION","THE DARK KNIGHT","OPPENHEIMER","DUNE PART TWO","PARASITE"],"types":["OFFICIAL TRAILER","REVIEW","BEHIND THE SCENES","CLIP"]},
    "WEB-SERIES":{"icon":"📺","titles":["INVINCIBLE","THE BOYS","STRANGER THINGS","BREAKING BAD","GAME OF THRONES","ARCANE"],"types":["SEASON TRAILER","BEST MOMENTS","REVIEW","RECAP"]},
    "GAMING":{"icon":"🎮","titles":["GTA 5","GTA 6","ELDEN RING","WARZONE","MINECRAFT","VALORANT","THE LAST OF US"],"types":["GAMEPLAY","WALKTHROUGH","TRAILER","SPEEDRUN"]},
    "ANIMATIONS":{"icon":"✨","studios":["MAPPA","UFOTABLE","PIXAR","STUDIO GHIBLI","WIT STUDIO","KYOTO ANIMATION"],"types":["BEST SCENES","TRAILER","AMV"]},
    "CARTOONS":{"icon":"🎭","titles":["BEN 10","TOM AND JERRY","GRAVITY FALLS","RICK AND MORTY","AVATAR THE LAST AIRBENDER","THE SIMPSONS"],"types":["FULL EPISODE","BEST MOMENTS"]},
    "STUDY":{"icon":"📚","topics":["PYTHON","FASTAPI","MACHINE LEARNING","REACT","DOCKER","SYSTEM DESIGN","GIT & GITHUB"],"types":["FULL TUTORIAL","CRASH COURSE","PROJECT BUILD"]},
    "MUSIC":{"icon":"🎵","genres":["LOFI HIP HOP","PHONK","EDM","BOLLYWOOD HITS","ANIME OST","JAZZ"],"types":["PLAYLIST","MIX","LIVE PERFORMANCE"]},
}
CHIPS = ["All","Gaming","< 5 min","Music","DC Comics","Delta Force","Mixes","Superheroes","Open-wheel cars","Data Science","Sci-fi films","Anime","Comedy","Recently uploaded","Watched","New to you"]

# ═══════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════
for k,v in [("query",""),("active_short",None),("loaded_query",False),
             ("last_terminal_query",""),("active_video",None),("page",1),
             ("open_cat",""),("volume",80),("speed",1.0)]:
    if k not in st.session_state: st.session_state[k] = v
if not isinstance(st.session_state.get("search_history"), list):
    st.session_state.search_history = []

# ── Load terminal injected query ──
if not st.session_state.loaded_query and os.path.exists(QUERY_FILE):
    with open(QUERY_FILE) as f: injected = f.read().strip()
    if injected:
        st.session_state.query = injected
        st.session_state.last_terminal_query = injected
    st.session_state.loaded_query = True

# ── Handle URL query params ──
p = st.query_params; needs_rerun = False
if "sq" in p and p["sq"] != st.session_state.query:
    nq = p["sq"].strip()
    if nq:
        h = st.session_state.search_history
        if nq not in h: h.insert(0, nq)
        st.session_state.search_history = h[:30]
    st.session_state.query = p["sq"]
    st.session_state.active_short = None
    st.session_state.active_video = None
    st.session_state.page = 1
    needs_rerun = True
if "oc" in p:
    st.session_state.open_cat = p["oc"]; needs_rerun = True
if "av" in p and p["av"] != st.session_state.active_video:
    st.session_state.active_video = p["av"]
    if "sq" in p: st.session_state.query = p["sq"]
    needs_rerun = True
if "as_" in p and p["as_"] != st.session_state.active_short:
    st.session_state.active_short = p["as_"]; needs_rerun = True
if "back" in p:
    st.session_state.active_video = None
    st.session_state.active_short = None
    needs_rerun = True
if "more" in p:
    st.session_state.page = min(st.session_state.page+1, 3); needs_rerun = True
if needs_rerun:
    st.query_params.clear(); st.rerun()

AQ       = st.session_state.query.strip()
FQ       = AQ or "trending videos 2025"
WATCH    = bool(st.session_state.active_video)
PAGE     = st.session_state.page
OPEN_CAT = st.session_state.open_cat

COMP_HEIGHT = 768

# ═══════════════════════════════════════════════════
# LOGO
# ═══════════════════════════════════════════════════
def load_logo():
    for path in ["assets/yt_logo.png","assets/youtube_logo.png","assets/logo.png"]+glob.glob("assets/*.png"):
        if os.path.exists(path):
            with open(path,"rb") as f: d = base64.b64encode(f.read()).decode()
            return "data:image/"+path.rsplit(".",1)[-1]+";base64,"+d
    return None

LOGO = load_logo()
LOGO_HTML = (f'<img src="{LOGO}" style="height:30px;width:auto;object-fit:contain;">') if LOGO else \
    '<span style="font-size:18px;font-weight:900;letter-spacing:2px;background:linear-gradient(90deg,#6c63ff,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent">&#9658;&nbsp;LOISEKK</span>'

# ═══════════════════════════════════════════════════
# LOTTIE (cached)
# ═══════════════════════════════════════════════════
@st.cache_data(ttl=86400)
def load_lottie(url: str):
    try:
        r = requests.get(url, timeout=3)
        return r.json() if r.status_code == 200 else None
    except:
        return None

LOTTIE = load_lottie("https://assets5.lottiefiles.com/packages/lf20_kxsd2ytq.json")

# ═══════════════════════════════════════════════════
# CACHED API CALLS
# ═══════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def fetch_videos(query: str, max_r: int):
    return search_videos(query, max_results=max_r)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_shorts(query: str):
    return search_shorts(query, max_results=12)

max_results = min(20 * PAGE, 50)
videos = []; shorts = []; _err = ""

with st.spinner(""):
    try:
        videos = fetch_videos(FQ, max_results)
    except Exception as e:
        _err = str(e)
    try:
        shorts = fetch_shorts(AQ or "trending shorts 2025") if not WATCH else []
    except:
        pass

# ═══════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════
def nav(k, v): return "?"+k+"="+urllib.parse.quote(str(v), safe="")
def esc(s):    return str(s).replace("<","&lt;").replace('"','&quot;')
def qjs(q):    return "window.parent.setQ('"+str(q).replace("\\","\\\\").replace("'","\\'")+"')"

def avatar(ch, thumb, size=36):
    colors = ["#ff6b6b","#4ecdc4","#45b7d1","#96ceb4","#dda0dd","#ff7675","#74b9ff","#a29bfe","#fd79a8","#55efc4"]
    col = colors[abs(hash(ch))%len(colors)]; ini = ch[0].upper() if ch else "Y"
    if thumb:
        return f'<img src="{thumb}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;display:block;flex-shrink:0;" onerror="this.style.display=\'none\'">'
    return f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:{col};display:flex;align-items:center;justify-content:center;font-size:{size//2-2}px;font-weight:700;color:#fff;flex-shrink:0;">{ini}</div>'

def video_card(v):
    vid = v.get("video_id",""); title = esc(v.get("title","Unknown")); ch = esc(v.get("channel",""))
    thumb = v.get("thumb","") or f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
    av = avatar(v.get("channel",""), v.get("channel_thumb",""))
    hover_js = (
        f"this.querySelector('.hpv').style.display='block';"
        f"this.querySelector('.hpv iframe').src='https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&mute=1&controls=0&rel=0&modestbranding=1&loop=1&playlist={vid}';"
        f"this.querySelector('img').style.opacity='0';"
    )
    leave_js = (
        f"this.querySelector('.hpv').style.display='none';"
        f"this.querySelector('.hpv iframe').src='';"
        f"this.querySelector('img').style.opacity='1';"
    )
    return (f'<a href="{nav("av",vid)}&sq={urllib.parse.quote(AQ,safe="")}" style="text-decoration:none;display:block">'
            f'<div class="vc"><div class="vt" onmouseenter="{hover_js}" onmouseleave="{leave_js}">'
            f'<img src="{thumb}" loading="lazy" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;border-radius:12px;transition:opacity .3s;" onerror="this.src=\'https://img.youtube.com/vi/{vid}/mqdefault.jpg\'">'
            f'<div class="hpv" style="display:none;position:absolute;top:0;left:0;width:100%;height:100%;border-radius:12px;overflow:hidden;z-index:2;">'
            f'<iframe src="" allow="autoplay;encrypted-media" style="width:100%;height:100%;border:none;pointer-events:none;"></iframe>'
            f'</div>'
            f'<div class="pov"><svg viewBox="0 0 24 24" style="fill:#fff;width:22px;height:22px"><path d="M8 5v14l11-7z"/></svg></div>'
            f'</div><div class="vm"><div>{av}</div>'
            f'<div class="vi"><div class="vn">{title}</div><div class="vch">{ch}</div></div>'
            f'</div></div></a>')

def short_card(s):
    vid = s.get("video_id",""); title = esc(s.get("title",""))
    thumb = s.get("thumb","") or f"https://img.youtube.com/vi/{vid}/mqdefault.jpg"
    if st.session_state.active_short == vid:
        return (f'<div class="shc on"><iframe src="https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&rel=0"'
                f' allow="autoplay;encrypted-media" allowfullscreen'
                f' style="width:100%;aspect-ratio:9/16;border:none;border-radius:12px;display:block;"></iframe></div>')
    _idx = next((i for i,s in enumerate(shorts) if s.get("video_id","")==vid), 0)
    return (f'<div class="shc" onclick="openShort({_idx})" style="cursor:pointer">'
            f'<img src="{thumb}" loading="lazy" style="width:100%;aspect-ratio:9/16;object-fit:cover;display:block;"'
            f' onerror="this.src=\'https://img.youtube.com/vi/{vid}/mqdefault.jpg\'">'
            f'<div class="sht">{title}</div></div>')

# ═══════════════════════════════════════════════════
# BUILD HTML BLOCKS
# ═══════════════════════════════════════════════════
chips_html = "".join(
    f'<span class="chip{" on" if i==0 else ""}" onclick="{qjs(c)}">{c}</span>'
    for i, c in enumerate(CHIPS)
)

def build_cat_items():
    html = ""
    for cat, data in CONTENT.items():
        icon = data.get("icon","▶"); is_open = (OPEN_CAT == cat)
        items    = data.get("gps") or data.get("titles") or data.get("topics") or data.get("genres") or data.get("studios") or []
        subtypes = data.get("stages") or data.get("sections") or data.get("types") or []
        first_q  = items[0] if items else cat
        toggle   = nav("oc","") if is_open else nav("oc",cat)+"&sq="+urllib.parse.quote(first_q,safe="")
        bg       = "background:#1a1a1a;" if is_open else ""
        html += (f'<a href="{toggle}" style="text-decoration:none;display:block">'
                 f'<div class="si" style="{bg}"><span class="sbi">{icon}</span>'
                 f'<span style="flex:1">{cat}</span>'
                 f'<span style="font-size:10px;color:#aaa">{"▼" if is_open else "▶"}</span></div></a>')
        if is_open:
            html += '<div style="background:#111;margin:0 4px 4px;border-radius:8px;padding:8px 6px;">'
            if subtypes:
                html += '<div style="display:flex;gap:4px;flex-wrap:wrap;padding:0 4px 8px;">'
                for st_ in subtypes:
                    html += f'<span onclick="{qjs(first_q+" "+st_)}" style="background:#272727;color:#f1f1f1;padding:3px 9px;border-radius:6px;font-size:11px;cursor:pointer;white-space:nowrap;display:inline-block;margin-bottom:2px">{esc(st_)}</span>'
                html += '</div>'
            for item in items[:8]:
                html += (f'<div onclick="{qjs(item)}" style="padding:5px 8px;font-size:12px;color:#ccc;border-radius:6px;cursor:pointer;transition:background .1s"'
                         f' onmouseover="this.style.background=\'#272727\'" onmouseout="this.style.background=\'transparent\'">{esc(item)}</div>')
            if cat == "F1":
                html += '<div style="padding:6px 4px 2px;font-size:11px;color:#aaa">Quick year:</div><div style="display:flex;gap:4px;flex-wrap:wrap;padding:0 4px;">'
                for yr in [2025,2024,2023,2022,2021]:
                    html += f'<span onclick="{qjs(str(yr)+" F1 SEASON HIGHLIGHTS")}" style="background:#272727;color:#f1f1f1;padding:3px 8px;border-radius:6px;font-size:11px;cursor:pointer;display:inline-block;margin-bottom:2px">{yr}</span>'
                html += '</div>'
            html += '</div>'
    return html

cat_items = build_cat_items()

# ── Sidebar SVG helpers ──
def _si(path, label, link="", onclick="", gray=False, active=False):
    col = "#aaa" if gray else "#f1f1f1"; cls = "si on" if active else "si"
    oc = f' onclick="{onclick}"' if onclick else ""
    inner = (f'<div class="{cls}"{oc}>'
             f'<svg style="width:20px;height:20px;fill:{col};flex-shrink:0" viewBox="0 0 24 24"><path d="{path}"/></svg>'
             f'<span style="margin-left:10px;color:{col}">{label}</span></div>')
    return f'<a href="{link}" style="text-decoration:none;display:block">{inner}</a>' if link else inner

def _yt(label):
    return (f'<div class="si"><svg style="width:20px;height:20px;fill:#8B5CF6;flex-shrink:0" viewBox="0 0 24 24">'
            f'<path d="M21.58 7.19c-.23-.86-.91-1.54-1.77-1.77C18.25 5 12 5 12 5s-6.25 0-7.81.42c-.86.23-1.54.91-1.77 1.77C2 8.75 2 12 2 12s0 3.25.42 4.81c.23.86.91 1.54 1.77 1.77C5.75 19 12 19 12 19s6.25 0 7.81-.42c.86-.23 1.54-.91 1.77-1.77C22 15.25 22 12 22 12s0-3.25-.42-4.81zM10 15V9l5.2 3-5.2 3z"/></svg>'
            f'<span style="margin-left:10px">{label}</span></div>')

sb = []
sb.append(f'<div class="sbt"><div class="sbh">&#9776;</div>{LOGO_HTML}</div>')
sb.append(_si("M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z","Home",active=True))
sb.append(_si("M10 14.65v-5.3L15 12l-5 2.65z","Shorts"))
sb.append(_si("M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8 12.5v-9l6 4.5-6 4.5z","Subscriptions"))
sb.append('<div class="sd"></div><div class="ss">My Queries</div>')
sb.append(cat_items)
sb.append('<div class="sd"></div><div class="ss">You &#8250;</div>')
sb.append(_si("M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z","History"))
sb.append(_si("M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z","Playlists"))
sb.append(_si("M22 9V7h-2V5c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-2h2v-2h-2v-2h2v-2h-2V9h2zm-4 10H4V5h14v14zm-2-8H6v-2h10v2zm-4 4H6v-2h6v2z","Watch later"))
sb.append(_si("M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z","Liked videos"))
sb.append(_si("M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8 12.5v-9l6 4.5-6 4.5z","Your videos"))
sb.append(_si("M5 20h14v-2H5v2zM19 9h-4V3H9v6H5l7 7 7-7z","Downloads"))
sb.append(_si("M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z","Show more",gray=True))
sb.append('<div class="sd"></div><div class="ss">Explore</div>')
sb.append(_si("M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z","Trending",onclick=qjs("Trending")))
sb.append(_si("M19 6h-2c0-2.76-2.24-5-5-5S7 3.24 7 6H5c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-7-3c1.66 0 3 1.34 3 3H9c0-1.66 1.34-3 3-3zm0 10c-1.66 0-3-1.34-3-3h2c0 .55.45 1 1 1s1-.45 1-1h2c0 1.66-1.34 3-3 3z","Shopping",onclick=qjs("Shopping")))
sb.append(_si("M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z","Music",onclick=qjs("Music playlist")))
sb.append(_si("M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z","Movies",onclick=qjs("Movies trailer")))
sb.append(_si("M21 6H3c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-10 7H8v3H6v-3H3v-2h3V8h2v3h3v2zm4.5 2c-.83 0-1.5-.67-1.5-1.5S14.67 12 15.5 12s1.5.67 1.5 1.5S16.33 15 15.5 15zm3-3c-.83 0-1.5-.67-1.5-1.5S17.67 9 18.5 9s1.5.67 1.5 1.5S19.33 12 18.5 12z","Gaming",onclick=qjs("Gaming highlights")))
sb.append(_si("M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm-5 14H4v-4h11v4zm0-5H4V9h11v4zm5 5h-4V9h4v9z","News",onclick=qjs("Latest news")))
sb.append(_si("M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z","Show more",gray=True))
sb.append('<div class="sd"></div><div class="ss">More from LOISEKK</div>')
sb.append(_yt("LOISEKK Premium")); sb.append(_yt("LOISEKK Music")); sb.append(_yt("LOISEKK Kids"))
sb.append('<div class="sd"></div>')
sb.append(_si("M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z","Settings"))
sb.append(_si("M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z","Help"))
sb.append(_si("M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z","Send feedback"))
sb.append('<div class="sd"></div>')
sb.append('<div class="sml">About &middot; Press &middot; Copyright<br>Terms &middot; Privacy<br>&copy; 2025 LOISEKK<br><br><span style="color:#3ea6ff;font-size:10px">&#9000; Ctrl+K = Search &nbsp; Esc = Back</span><br><br><span style="color:#f1f1f1;font-size:12px;font-weight:700;letter-spacing:0.5px">LOISEKK</span><br><span style="color:#aaa;font-size:11px">Yash Brahmankar</span></div>')
SIDEBAR = "".join(sb)

# ── Home content ──
v1 = "".join(video_card(v) for v in videos[:4])
v2 = "".join(video_card(v) for v in videos[4:8])
vr = "".join(video_card(v) for v in videos[8:])
sc = "".join(short_card(s) for s in shorts[:6])

if not videos:
    from youtube_api import YOUTUBE_API_KEY as _k
    ks = ("✅ "+str(_k[:8])+"...") if _k else "❌ No API key in .env"
    EMPTY = (f'<div style="padding:60px 20px;text-align:center;color:#aaa">'
             f'<div style="font-size:56px;margin-bottom:16px">🎬</div>'
             f'<div style="font-size:20px;font-weight:600;color:#f1f1f1;margin-bottom:8px">No videos found</div>'
             f'<div style="font-size:14px;margin-bottom:6px">Query: <strong style="color:#fff">{esc(FQ)}</strong></div>'
             +(f'<div style="color:#ff6b6b;font-size:13px;margin-bottom:8px">{esc(_err)}</div>' if _err else "")
             +f'<div style="font-size:12px;color:#555;font-family:monospace">{ks}</div></div>')
else:
    EMPTY = ""

CLOSE_S = (f'<a href="{nav("back","1")}" style="text-decoration:none">'
           f'<div style="text-align:center;padding:8px 0 12px">'
           f'<button style="background:#272727;color:#fff;border:none;padding:8px 24px;border-radius:8px;font-size:14px;cursor:pointer">&#10006; Close</button>'
           f'</div></a>') if st.session_state.active_short else ""

LOAD_MORE = (f'<a href="{nav("more","1")}" style="text-decoration:none">'
             f'<div style="text-align:center;padding:24px">'
             f'<button style="background:#272727;color:#f1f1f1;border:none;padding:10px 32px;border-radius:20px;font-size:14px;cursor:pointer;font-weight:500">Load more &#8595;</button>'
             f'</div></a>') if len(videos) >= max_results else ""

# ── Fullscreen Shorts Overlay ──
_shorts_data = json.dumps([{"vid":s.get("video_id",""),"title":s.get("title",""),"thumb":s.get("thumb","")} for s in shorts[:6]])

SHORTS_OVERLAY = (
    '<div id="shorts-overlay">'
    '<button class="short-close" onclick="closeShorts()">&#10005;</button>'
    '<div class="short-player-wrap"><iframe id="short-iframe" src="" allow="autoplay;encrypted-media;fullscreen" allowfullscreen style="width:100%;height:100vh;border:none;"></iframe></div>'
    '<div class="short-actions">'
    '<div class="sa" onclick="likeShort()"><svg viewBox="0 0 24 24" width="28" height="28"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg><span>Like</span></div>'
    '<div class="sa" onclick="dislikeShort()"><svg viewBox="0 0 24 24" width="28" height="28"><path d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z"/></svg><span>Dislike</span></div>'
    '<div class="sa" onclick="shareShort()"><svg viewBox="0 0 24 24" width="28" height="28"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92c0-1.61-1.31-2.92-2.92-2.92z"/></svg><span>Share</span></div>'
    '</div>'
    '<button class="short-next" onclick="nextShort()">&#8595;</button>'
    '<script>'
    'var _shortsData = ' + _shorts_data + ';'
    'var _shortIdx = 0;'
    'function openShort(idx){'
        '_shortIdx = idx;'
        'var s = _shortsData[idx];'
        'if(!s) return;'
        'document.getElementById("short-iframe").src = "https://www.youtube-nocookie.com/embed/"+s.vid+"?autoplay=1&rel=0";'
        'document.getElementById("shorts-overlay").classList.add("active");'
        'document.body.style.overflow="hidden";'
    '}'
    'function closeShorts(){'
        'document.getElementById("shorts-overlay").classList.remove("active");'
        'document.getElementById("short-iframe").src="";'
        'document.body.style.overflow="";'
    '}'
    'function nextShort(){'
        '_shortIdx = (_shortIdx+1) % _shortsData.length;'
        'openShort(_shortIdx);'
    '}'
    'function likeShort(){}'
    'function dislikeShort(){}'
    'function shareShort(){}'
    'document.addEventListener("keydown",function(e){if(e.key==="Escape")closeShorts();if(e.key==="ArrowDown")nextShort();});'
    '</script>'
    '</div>'
)

HOME_CONTENT = (
    f'<div id="chips">{chips_html}</div>'
    + EMPTY
    + f'<div class="vg">{v1}{v2}</div>'
    + '<div class="hr"></div>'
    + f'<div class="sw"><div class="sl"><span style="color:#8B5CF6;font-size:22px">&#9889;</span> Shorts</div>'
    + f'<div class="sg">{sc or "<div style=color:#aaa;padding:12px>No shorts.</div>"}</div>{CLOSE_S}</div>'
    + '<div class="hr"></div>'
    + f'<div class="vg">{vr}</div>'
    + LOAD_MORE
    + '<div style="height:40px"></div>'
    + SHORTS_OVERLAY
)

# ═══════════════════════════════════════════════════
# WATCH PAGE SUGGESTED VIDEOS
# ── ONLY THIS BLOCK CHANGED ──
# Now fetches from 3 queries: video title + channel + keywords
# Shows up to 45 suggestions instead of 25
# ═══════════════════════════════════════════════════
SUGG = ""
cur_title = cur_ch = cur_av = ""
if WATCH:
    vid_id = st.session_state.active_video
    cur_v = next((v for v in videos if v.get("video_id")==vid_id), videos[0] if videos else {})
    cur_title = cur_v.get("title","Video"); cur_ch = cur_v.get("channel","LOISEKK")
    cur_av = avatar(cur_v.get("channel",""), cur_v.get("channel_thumb",""), 44)

    # ── 3 separate fetches for richer suggestions ──
    _title_q   = cur_title[:50] if cur_title else AQ          # by video title (most relevant)
    _channel_q = (cur_ch[:30] + " videos") if cur_ch else AQ  # by channel (same creator)
    _kw_q      = " ".join((cur_title or AQ).split()[:3]) + " related videos"  # by keywords

    try:
        _r1 = fetch_videos(_title_q,   50)   # 50 by title
    except:
        _r1 = []
    try:
        _r2 = fetch_videos(_channel_q, 30)   # 30 by channel
    except:
        _r2 = []
    try:
        _r3 = fetch_videos(_kw_q,      30)   # 30 by keyword
    except:
        _r3 = []

    # Merge all sources + main search, deduplicate, skip current video
    _seen = {vid_id}
    _all_sugg = []
    for v in (_r1 + _r2 + _r3 + videos):
        sid = v.get("video_id","")
        if sid and sid not in _seen:
            _seen.add(sid)
            _all_sugg.append(v)

    # Build suggestion cards — up to 45
    for v in _all_sugg[:45]:
        sid = v.get("video_id","")
        st2 = esc(v.get("title","")); sc2 = esc(v.get("channel",""))
        th2 = v.get("thumb","") or f"https://img.youtube.com/vi/{sid}/mqdefault.jpg"
        SUGG += (f'<a href="{nav("av",sid)}&sq={urllib.parse.quote(AQ,safe="")}" style="text-decoration:none;display:block">'
                 f'<div class="sug"><div class="suth"><img src="{th2}" loading="lazy" onerror="this.src=\'https://img.youtube.com/vi/{sid}/mqdefault.jpg\'">'
                 f'<div class="suov">&#9658;</div></div>'
                 f'<div class="sui"><div class="suti">{st2}</div>'
                 f'<div class="such">{sc2}</div>'
                 f'</div></div></a>')

PAGE_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0;font-family:'Roboto',sans-serif;color:#f1f1f1;}
html,body{height:100vh;width:100vw;background:#0f0f0f;overflow:hidden;margin:0;padding:0;}
a{color:inherit;text-decoration:none;}
#yw{display:flex;width:100%;height:100%;min-height:100vh;background:#0f0f0f;overflow:hidden;position:fixed;top:0;left:0;right:0;bottom:0;}
#sb{width:240px;min-width:240px;height:100vh;background:#0f0f0f;border-right:1px solid #272727;display:flex;flex-direction:column;overflow-y:scroll;overflow-x:hidden;flex-shrink:0;scrollbar-width:thin;scrollbar-color:#555 #1a1a1a;}
#sb::-webkit-scrollbar{width:6px;background:#1a1a1a;}
#sb::-webkit-scrollbar-thumb{background:#555;border-radius:3px;}
#sb::-webkit-scrollbar-thumb:hover{background:#888;}
.sbt{display:flex;align-items:center;gap:10px;padding:0 14px;height:56px;position:sticky;top:0;background:#0f0f0f;z-index:5;border-bottom:1px solid #1a1a1a;flex-shrink:0;}
.sbh{font-size:18px;cursor:pointer;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.sbh:hover{background:#272727;}
.si{display:flex;align-items:center;padding:0 12px;height:40px;border-radius:10px;cursor:pointer;margin:1px 6px;font-size:14px;white-space:nowrap;overflow:hidden;transition:background .1s;flex-shrink:0;}
.si:hover{background:#272727;}
.si.on{background:#272727;font-weight:500;}
.sbi{font-size:18px;flex-shrink:0;width:24px;text-align:center;margin-right:16px;}
.ss{font-size:14px;font-weight:600;padding:16px 16px 4px;flex-shrink:0;}
.sd{height:1px;background:#272727;margin:8px 0;flex-shrink:0;}
.sml{font-size:11px;color:#717171;padding:8px 16px 32px;line-height:1.9;flex-shrink:0;}
#mn{flex:1;display:flex;flex-direction:column;min-width:0;height:100vh;overflow:hidden;}
#tb{display:flex;align-items:center;height:56px;padding:0 16px;gap:12px;background:#0f0f0f;border-bottom:1px solid #1a1a1a;flex-shrink:0;}
.sp{flex:1;}
#sf{display:flex;align-items:center;width:480px;flex-shrink:0;}
#si{flex:1;height:40px;background:#121212;color:#f1f1f1;border:1px solid #303030;border-right:none;border-radius:40px 0 0 40px;padding:0 20px;font-size:15px;outline:none;transition:border-color .2s,background .2s;}
#si:focus{border-color:#3ea6ff;background:#000;}
#si::placeholder{color:#717171;}
#si::-webkit-search-cancel-button{cursor:pointer;filter:invert(1);}
#sb2{width:52px;height:40px;background:#272727;border:1px solid #303030;border-left:none;border-radius:0 40px 40px 0;color:#f1f1f1;font-size:18px;cursor:pointer;transition:background .15s;}
#sb2:hover{background:#3f3f3f;}
.micbtn{width:40px;height:40px;border-radius:50%;background:transparent;border:none;font-size:20px;cursor:pointer;color:#f1f1f1;display:flex;align-items:center;justify-content:center;}
.micbtn:hover{background:#272727;}
.bkb{display:inline-flex;align-items:center;gap:6px;background:#272727;border:none;border-radius:20px;padding:7px 14px;font-size:13px;cursor:pointer;color:#f1f1f1;}
.bkb:hover{background:#3f3f3f;}
#ct{flex:1;overflow-y:auto;overflow-x:hidden;}
#ct::-webkit-scrollbar{width:6px;}
#ct::-webkit-scrollbar-thumb{background:#3f3f3f;border-radius:3px;}
#chips{display:flex;gap:8px;padding:10px 16px;overflow-x:auto;white-space:nowrap;border-bottom:1px solid #272727;scrollbar-width:none;}
#chips::-webkit-scrollbar{display:none;}
.chip{display:inline-flex;align-items:center;background:#272727;color:#f1f1f1;padding:0 12px;height:32px;border-radius:8px;font-size:14px;font-weight:500;cursor:pointer;flex-shrink:0;transition:background .1s,transform .1s;user-select:none;}
.chip:hover{background:#3f3f3f;transform:scale(1.03);}
.chip.on{background:#f1f1f1!important;color:#0f0f0f!important;}
.vg{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:16px;}
.vc{cursor:pointer;}
.vt{position:relative;width:100%;padding-top:56.25%;border-radius:12px;overflow:hidden;background:#181818;}
.vt img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;border-radius:12px;transition:transform .2s;}
.vc:hover .vt img{transform:scale(1.03);}
.pov{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:48px;height:48px;border-radius:50%;background:rgba(0,0,0,.7);display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity .15s;pointer-events:none;}
.vc:hover .pov{opacity:1;}
.vm{display:flex;gap:10px;padding:10px 0 4px;}
.vi{flex:1;min-width:0;}
.vn{font-size:14px;font-weight:500;color:#f1f1f1;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.4;margin-bottom:3px;}
.vch{font-size:13px;color:#aaa;}
.sw{padding:0 16px 20px;}
.sl{display:flex;align-items:center;gap:8px;padding:14px 0 10px;font-size:18px;font-weight:700;}
.sg{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;}
.shc{cursor:pointer;border-radius:12px;overflow:hidden;background:#181818;transition:transform .15s;position:relative;}
.shc:hover{transform:scale(1.02);}
.sht{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(transparent,rgba(0,0,0,.85));color:#fff;font-size:13px;font-weight:500;padding:24px 10px 10px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.shc.on{border:2px solid #8B5CF6;}
.hr{height:1px;background:#272727;margin:0 16px;}
.sug{display:flex;gap:8px;padding:6px 8px 4px 16px;cursor:pointer;border-radius:8px;}
.sug:hover{background:#272727;}
.suth{position:relative;width:168px;min-width:168px;}
.suth img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:8px;display:block;}
.suov{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.7);color:#fff;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;opacity:0;transition:opacity .15s;}
.sug:hover .suov{opacity:1;}
.sui{flex:1;min-width:0;}
.suti{font-size:13px;font-weight:500;color:#f1f1f1;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.4;margin-bottom:4px;}
#sc2{display:flex;gap:6px;padding:8px 8px 12px;overflow-x:auto;scrollbar-width:none;}
.sch{background:#272727;color:#f1f1f1;padding:6px 12px;border-radius:8px;font-size:13px;cursor:pointer;white-space:nowrap;flex-shrink:0;}
.sch.on{background:#f1f1f1;color:#0f0f0f;font-weight:600;}
/* Fullscreen Shorts Overlay */
#shorts-overlay{display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:#000;z-index:10000;align-items:center;justify-content:center;}
#shorts-overlay.active{display:flex;}
.short-player-wrap{position:relative;height:100vh;width:100%;max-width:400px;display:flex;align-items:center;justify-content:center;}
.short-player-wrap iframe{width:100%;height:100vh;border:none;}
.short-close{position:fixed;top:20px;right:20px;z-index:10001;background:rgba(255,255,255,.15);border:none;color:#fff;width:44px;height:44px;border-radius:50%;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(8px);}
.short-close:hover{background:rgba(255,255,255,.3);}
.short-next{position:fixed;right:20px;bottom:40px;z-index:10001;background:rgba(255,255,255,.15);border:none;color:#fff;width:44px;height:44px;border-radius:50%;font-size:22px;cursor:pointer;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(8px);}
.short-next:hover{background:rgba(255,255,255,.3);}
.short-actions{display:flex;flex-direction:column;gap:24px;padding:0 28px;}
.sa{display:flex;flex-direction:column;align-items:center;gap:6px;cursor:pointer;background:none;border:none;}
.sa svg{fill:#fff;}
.sa span{font-size:13px;color:#fff;font-weight:500;}
</style>"""

BACK_BTN = (f'<a href="{nav("back","1")}" style="text-decoration:none">'
            f'<button class="bkb">&#8592; Back</button></a>') if WATCH else ""

# ═══════════════════════════════════════════════════
# STREAMLIT CHROME RESET
# ═══════════════════════════════════════════════════
st.markdown("""<style>
html,body{overflow:hidden!important;height:100vh!important;width:100vw!important;background:#0f0f0f!important;margin:0!important;padding:0!important;}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="block-container"],
[data-testid="stVerticalBlock"],[data-testid="stHorizontalBlock"]{
  background:#0f0f0f!important;padding:0!important;max-width:100vw!important;
  overflow:hidden!important;height:100vh!important;margin:0!important;width:100vw!important;}
section.main>div{padding:0!important;margin:0!important;}
header,[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stSidebar"],[data-testid="collapsedControl"],.stDeployButton,
[data-testid="stStatusWidget"]{display:none!important;}
#MainMenu,footer{visibility:hidden!important;}
.stHtml{height:0!important;min-height:0!important;overflow:hidden!important;padding:0!important;margin:0!important;}
.stHtml>*{display:none!important;}
iframe[height="0"]{display:none!important;}
[data-testid="stBlock"] iframe:not([height="0"]),
.element-container iframe:not([height="0"]),
iframe[title]:not([height="0"]) {
    position:fixed!important;
    top:0!important;left:0!important;
    width:100vw!important;height:100vh!important;
    border:none!important;z-index:9999!important;
}
</style>""", unsafe_allow_html=True)

# ── Inject setQ() into Streamlit parent ──
hist_json = json.dumps(st.session_state.search_history[:20])
st.html(f"""<script>
window.setQ = function(q) {{
    var url = new URL(window.location.href);
    url.searchParams.set('sq', q);
    window.location.href = url.toString();
}};
try {{ localStorage.setItem('yt_history', JSON.stringify({hist_json})); }} catch(e) {{}}
document.addEventListener('keydown', function(e) {{
    if ((e.ctrlKey && e.key==='k') || (e.key==='/' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName))) {{
        e.preventDefault();
        var inp = document.querySelector('#si, input[type=search]');
        if (inp) {{ inp.focus(); inp.select(); }}
    }}
    if (e.key==='Escape' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) {{
        window.location.href = '?back=1';
    }}
}});
</script>
<datalist id="ytsug">
{"".join(f'<option value="{esc(h)}"></option>' for h in st.session_state.search_history[:20])}
</datalist>""", unsafe_allow_javascript=True)

# ═══════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════
TOPBAR = f"""
<div id="tb">
  <div class="sp"></div>
  <form id="sf" onsubmit="doSearch(event)">
    <input id="si" type="search" list="ytsug" placeholder="Search  (Ctrl+K)" value="{esc(AQ)}" autocomplete="on">
    <button id="sb2" type="submit">&#128269;</button>
  </form>
  <button class="micbtn" title="Voice">&#127897;&#65039;</button>
  <div class="sp"></div>
  {BACK_BTN}
</div>"""

if not WATCH:
    PAGE_HTML = f"""<!DOCTYPE html><html><head><meta charset="utf-8">{PAGE_CSS}
</head><body>
<script>
function doSearch(e){{e.preventDefault();var q=document.getElementById('si').value.trim();if(q)window.parent.setQ(q);}}
document.addEventListener('DOMContentLoaded',function(){{
  var inp=document.getElementById('si');
  if(inp){{
    inp.addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();var q=this.value.trim();if(q)window.parent.setQ(q);}}}});
    inp.addEventListener('input',function(){{this.style.borderColor='#3ea6ff';}});
    inp.addEventListener('blur',function(){{this.style.borderColor='#303030';}});
  }}
}});
</script>
<div id="yw">
  <div id="sb">{SIDEBAR}</div>
  <div id="mn">
    {TOPBAR}
    <div id="ct">{HOME_CONTENT}</div>
  </div>
</div>
</body></html>"""
    components.html(PAGE_HTML, height=1080, scrolling=False)

else:
    # ── Full watch page as single components.html — no Streamlit layout ──
    fw = esc((AQ or "Related").split()[0])
    WATCH_PAGE_HTML = f"""<!DOCTYPE html><html><head><meta charset="utf-8">{PAGE_CSS}
<style>
/* Watch page layout — overrides base PAGE_CSS for this page */
#ct{{
    display:flex;flex-direction:row;
    height:calc(100vh - 56px);
    overflow:hidden;padding:0;background:#0f0f0f;
}}
/* Left panel — video + info, scrollable */
#wl{{
    flex:1;min-width:0;overflow-y:auto;overflow-x:hidden;
    background:#0f0f0f;padding:0 24px 60px 24px;
}}
#wl::-webkit-scrollbar{{width:6px;}}
#wl::-webkit-scrollbar-thumb{{background:#3f3f3f;border-radius:3px;}}
/* Video player */
.pw{{width:100%;background:#000;line-height:0;margin-bottom:16px;border-radius:12px;overflow:hidden;}}
.pw iframe{{width:100%;aspect-ratio:16/9;display:block;border:none;}}
/* Video info */
.wti{{font-size:20px;font-weight:700;line-height:1.4;color:#f1f1f1;margin-bottom:12px;}}
.wch{{display:flex;align-items:center;gap:12px;margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid #272727;flex-wrap:wrap;}}
.subb{{background:#f1f1f1;color:#0f0f0f;border:none;border-radius:20px;padding:8px 16px;font-size:14px;font-weight:600;cursor:pointer;margin-left:auto;white-space:nowrap;}}
.subb:hover{{background:#ddd;}}
.ar{{display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap;}}
.ab{{display:flex;align-items:center;gap:6px;background:#272727;border:none;border-radius:20px;padding:8px 16px;font-size:14px;cursor:pointer;color:#f1f1f1;white-space:nowrap;}}
.ab:hover{{background:#3f3f3f;}}
.wde{{background:#272727;border-radius:12px;padding:14px 16px;font-size:14px;line-height:1.6;margin-bottom:20px;cursor:pointer;}}
.wde:hover{{background:#303030;}}
/* Comments */
.cmt-box{{display:flex;gap:12px;margin-bottom:32px;padding-top:8px;}}
.cmt-in{{flex:1;border:none;border-bottom:1px solid #717171;background:transparent;color:#f1f1f1;font-size:14px;padding:6px 0;outline:none;}}
.cmt-in:focus{{border-bottom-color:#f1f1f1;}}
/* Right panel — suggestions, scrollable */
#wr{{
    width:400px;min-width:400px;flex-shrink:0;
    height:calc(100vh - 56px);overflow-y:auto;overflow-x:hidden;
    padding:12px 12px 40px 16px;
    border-left:1px solid #272727;background:#0f0f0f;
    scrollbar-width:thin;scrollbar-color:#555 #1a1a1a;
}}
#wr::-webkit-scrollbar{{width:6px;background:#1a1a1a;}}
#wr::-webkit-scrollbar-thumb{{background:#555;border-radius:3px;}}
#wr::-webkit-scrollbar-thumb:hover{{background:#888;}}
/* Filter chips in right panel */
#sc2{{display:flex;gap:6px;padding:0 0 12px;overflow-x:auto;scrollbar-width:none;flex-wrap:nowrap;}}
#sc2::-webkit-scrollbar{{display:none;}}
.sch{{background:#272727;color:#f1f1f1;padding:6px 12px;border-radius:8px;font-size:13px;cursor:pointer;white-space:nowrap;flex-shrink:0;border:none;}}
.sch:hover{{background:#3f3f3f;}}
.sch.on{{background:#f1f1f1;color:#0f0f0f;font-weight:600;}}
/* Suggestion cards */
.sug{{display:flex;gap:8px;padding:6px 6px 4px;cursor:pointer;border-radius:8px;margin-bottom:2px;}}
.sug:hover{{background:#272727;}}
.suth{{position:relative;width:160px;min-width:160px;}}
.suth img{{width:160px;height:90px;object-fit:cover;border-radius:8px;display:block;}}
.suov{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.75);color:#fff;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;opacity:0;transition:opacity .15s;}}
.sug:hover .suov{{opacity:1;}}
.sui{{flex:1;min-width:0;padding-top:2px;}}
.suti{{font-size:13px;font-weight:500;color:#f1f1f1;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.4;margin-bottom:4px;}}
.such{{font-size:12px;color:#aaa;margin-top:2px;}}
</style>
</head><body>
<script>
function doSearch(e){{e.preventDefault();var q=document.getElementById('si').value.trim();if(q)window.parent.setQ(q);}}
document.addEventListener('DOMContentLoaded',function(){{
  var inp=document.getElementById('si');
  if(inp){{
    inp.addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();var q=this.value.trim();if(q)window.parent.setQ(q);}}}});
    inp.addEventListener('input',function(){{this.style.borderColor='#3ea6ff';}});
    inp.addEventListener('blur',function(){{this.style.borderColor='#303030';}});
  }}
}});
</script>
<div id="yw">
  <div id="sb">{SIDEBAR}</div>
  <div id="mn">
    {TOPBAR}
    <div id="ct">

      <!-- LEFT: video + info + comments -->
      <div id="wl">
        <div class="pw">
          <iframe src="https://www.youtube-nocookie.com/embed/{vid_id}?autoplay=1&rel=0&modestbranding=1"
            allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture;fullscreen"
            allowfullscreen></iframe>
        </div>

        <div class="wti">{esc(cur_title)}</div>

        <div class="wch">
          {cur_av}
          <div style="min-width:0">
            <div style="font-size:15px;font-weight:500;color:#f1f1f1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{esc(cur_ch)}</div>
            <div style="font-size:13px;color:#6c63ff;font-weight:500">LOISEKK</div>
          </div>
          <button class="subb">Subscribe</button>
        </div>

        <div class="ar">
          <div style="display:flex">
            <button class="ab" style="border-radius:20px 0 0 20px;border-right:1px solid #3f3f3f">&#128077; Like</button>
            <button class="ab" style="border-radius:0 20px 20px 0;padding-left:10px">&#128078;</button>
          </div>
          <button class="ab">&#8599; Share</button>
          <button class="ab">&#11015; Download</button>
          <button class="ab" style="padding:8px 12px">&#8943;</button>
        </div>

        <div class="wde">
          <div style="font-weight:600;margin-bottom:4px">{esc(AQ or "trending")} &nbsp; <span style="color:#aaa;font-weight:400;font-size:13px">#{esc((AQ or "trending").replace(" ",""))} #LOISEKK</span></div>
          <div style="color:#aaa;font-size:13px">Click to expand description</div>
        </div>

        <div style="font-size:18px;font-weight:700;margin-bottom:16px;color:#f1f1f1">Comments</div>
        <div class="cmt-box">
          <div style="width:40px;height:40px;border-radius:50%;background:#272727;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">&#128522;</div>
          <input class="cmt-in" placeholder="Add a comment...">
        </div>
      </div>

      <!-- RIGHT: filter chips + suggestions -->
      <div id="wr">
        <div id="sc2">
          <button class="sch on">All</button>
          <button class="sch" onclick="{qjs(cur_ch[:20])}">{esc(cur_ch[:16] or "Channel")}</button>
          <button class="sch" onclick="{qjs(fw)}">{fw}</button>
          <button class="sch">Recently uploaded</button>
          <button class="sch">Watched</button>
        </div>
        {SUGG or '<div style="padding:20px;color:#aaa;text-align:center">No suggestions found.</div>'}
      </div>

    </div>
  </div>
</div>
</body></html>"""
    components.html(WATCH_PAGE_HTML, height=1080, scrolling=False)

# ═══════════════════════════════════════════════════
# TERMINAL SYNC
# ═══════════════════════════════════════════════════
if os.path.exists(QUERY_FILE):
    with open(QUERY_FILE) as f: latest = f.read().strip()
    if latest and latest != st.session_state.last_terminal_query:
        st.session_state.query = latest
        st.session_state.last_terminal_query = latest
        st.session_state.active_short = None
        st.session_state.active_video = None
        st.session_state.page = 1
        st.rerun()
else:
    vid_id = st.session_state.active_video
    ACTIVE_SHORT = st.session_state.active_short

    WATCH_HTML = f"""<!DOCTYPE html><html><head><meta charset="utf-8">{PAGE_CSS}
<style>
#ct{{display:flex;flex-direction:row;height:calc(100vh - 56px);overflow:hidden;padding:0;background:#0f0f0f;}}
#wl{{flex:1;min-width:0;overflow-y:auto;background:#0f0f0f;}}
#wl::-webkit-scrollbar{{width:6px;}}
#wl::-webkit-scrollbar-thumb{{background:#3f3f3f;border-radius:3px;}}
#wr{{width:360px;min-width:360px;overflow-y:auto;padding:12px 6px 40px 10px;border-left:1px solid #272727;flex-shrink:0;background:#0f0f0f;scrollbar-width:thin;scrollbar-color:#555 #1a1a1a;}}
#wr::-webkit-scrollbar{{width:6px;background:#1a1a1a;}}
#wr::-webkit-scrollbar-thumb{{background:#555;border-radius:3px;}}
#wr::-webkit-scrollbar-thumb:hover{{background:#888;}}
.pw{{width:100%;background:#000;line-height:0;}}
.pw iframe{{width:100%;aspect-ratio:16/9;display:block;border:none;}}
#wl-info{{padding:16px 24px 40px;}}
.wti{{font-size:20px;font-weight:700;line-height:1.4;color:#f1f1f1;margin-bottom:12px;}}
.wch{{display:flex;align-items:center;gap:14px;margin-bottom:14px;flex-wrap:wrap;}}
.subb{{background:#f1f1f1;color:#0f0f0f;border:none;border-radius:20px;padding:8px 16px;font-size:14px;font-weight:600;cursor:pointer;margin-left:auto;}}
.ar{{display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap;}}
.ab{{display:flex;align-items:center;gap:6px;background:#272727;border:none;border-radius:20px;padding:8px 16px;font-size:14px;cursor:pointer;color:#f1f1f1;}}
.ab:hover{{background:#3f3f3f;}}
.wde{{background:#272727;border-radius:12px;padding:14px;font-size:14px;line-height:1.6;margin-bottom:20px;}}
.sug{{display:flex;gap:8px;padding:6px 8px 4px 8px;cursor:pointer;border-radius:8px;}}
.sug:hover{{background:#272727;}}
.suth{{position:relative;width:168px;min-width:168px;}}
.suth img{{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:8px;display:block;}}
.suov{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.7);color:#fff;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;opacity:0;transition:opacity .15s;}}
.sug:hover .suov{{opacity:1;}}
.sui{{flex:1;min-width:0;}}
.suti{{font-size:13px;font-weight:500;color:#f1f1f1;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:1.4;margin-bottom:4px;}}
#sc2{{display:flex;gap:6px;padding:0 0 12px;overflow-x:auto;scrollbar-width:none;}}
#sc2::-webkit-scrollbar{{display:none;}}
.sch{{background:#272727;color:#f1f1f1;padding:6px 12px;border-radius:8px;font-size:13px;cursor:pointer;white-space:nowrap;flex-shrink:0;}}
.sch.on{{background:#f1f1f1;color:#0f0f0f;font-weight:600;}}
#shorts-overlay{{display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:#000;z-index:10000;flex-direction:row;align-items:center;justify-content:center;}}
#shorts-overlay.active{{display:flex;}}
.short-player-wrap{{position:relative;height:100vh;max-width:400px;width:100%;display:flex;align-items:center;justify-content:center;}}
.short-player-wrap iframe{{width:100%;height:100vh;max-height:100vh;border:none;}}
.short-close{{position:fixed;top:20px;right:20px;z-index:10001;background:rgba(255,255,255,.15);border:none;color:#fff;width:44px;height:44px;border-radius:50%;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(10px);}}
.short-close:hover{{background:rgba(255,255,255,.25);}}
.short-next{{position:fixed;right:20px;top:50%;transform:translateY(-50%);z-index:10001;background:rgba(255,255,255,.15);border:none;color:#fff;width:44px;height:44px;border-radius:50%;font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(10px);}}
.short-actions{{display:flex;flex-direction:column;gap:20px;padding:0 24px;}}
.sa{{display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;}}
.sa svg{{fill:#fff;}}
.sa span{{font-size:12px;color:#fff;font-weight:500;}}
</style>
</head><body>
<script>
function doSearch(e){{e.preventDefault();var q=document.getElementById('si').value.trim();if(q)window.parent.setQ(q);}}
document.addEventListener('DOMContentLoaded',function(){{
  var inp=document.getElementById('si');
  if(inp){{
    inp.addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();var q=this.value.trim();if(q)window.parent.setQ(q);}}}});
  }}
}});
</script>
<div id="yw">
  <div id="sb">{SIDEBAR}</div>
  <div id="mn">
    {TOPBAR}
    <div id="ct">
      <div id="wl">
        <div class="pw">
          <iframe src="https://www.youtube-nocookie.com/embed/{vid_id}?autoplay=1&rel=0&modestbranding=1"
            allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture;fullscreen"
            allowfullscreen></iframe>
        </div>
        <div id="wl-info">
        <div class="wti">{esc(cur_title)}</div>
        <div class="wch">
          {cur_av}
          <div>
            <div style="font-size:15px;font-weight:500;color:#f1f1f1">{esc(cur_ch)}</div>
            <div style="font-size:13px;color:#6c63ff;font-weight:500">LOISEKK</div>
          </div>
          <button class="subb">Subscribe</button>
        </div>
        <div class="ar">
          <div style="display:flex">
            <button class="ab" style="border-radius:20px 0 0 20px;border-right:1px solid #3f3f3f">&#128077; Like</button>
            <button class="ab" style="border-radius:0 20px 20px 0;padding-left:10px">&#128078;</button>
          </div>
          <button class="ab">&#8599; Share</button>
          <button class="ab">&#11015; Download</button>
          <button class="ab">&#183;&#183;&#183;</button>
        </div>
        <div class="wde">
          Search: <strong style="color:#fff">{esc(AQ or "trending")}</strong>
          <div style="color:#3ea6ff;font-size:13px;margin-top:6px">#{esc((AQ or "trending").replace(" ",""))} #LOISEKK</div>
        </div>
        <div style="font-size:18px;font-weight:600;margin-bottom:12px">Comments</div>
        <div style="display:flex;gap:12px;margin-bottom:40px">
          <div style="width:36px;height:36px;border-radius:50%;background:#272727;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0">&#128522;</div>
          <input style="flex:1;border:none;border-bottom:1px solid #717171;background:transparent;color:#f1f1f1;font-size:14px;padding:6px 0;outline:none" placeholder="Add a comment...">
        </div>
        </div>
      </div>
      <div id="wr">
        <div id="sc2">
          <span class="sch on">All</span>
          <span class="sch" onclick="{qjs(cur_ch[:20])}">{esc(cur_ch[:16])}</span>
          <span class="sch" onclick="{qjs(esc((AQ or 'Related').split()[0]))}">{esc((AQ or 'Related').split()[0])}</span>
          <span class="sch">Recently uploaded</span>
        </div>
        {SUGG or '<div style="padding:20px;color:#aaa">No suggestions.</div>'}
      </div>
    </div>
  </div>
</div>
</body></html>"""

    components.html(WATCH_HTML, height=1080, scrolling=False)
