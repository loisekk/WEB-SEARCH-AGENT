"""
google_app.py — LOISEKK Google Search
Streamlit-native, uses Google Custom Search API
FIX: Forces entire-web search via API params (bypasses broken UI toggle)
"""
import os, json, urllib.parse
import streamlit as st
import requests

# ── Key loading (local .env + Streamlit Cloud secrets) ──
def _get(k):
    try:
        v = st.secrets.get(k)
        if v: return v
    except: pass
    try:
        from dotenv import load_dotenv; load_dotenv()
    except: pass
    return os.getenv(k, "")

GOOGLE_API_KEY = _get("GOOGLE_API_KEY")
GOOGLE_CX_ID   = _get("GOOGLE_CX_ID")

# ── Page config ──
st.set_page_config(
    page_title="LOISEKK Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Session state ──
for k, v in [("results", []), ("query", ""), ("history", []),
              ("tab", "web"), ("loading", False)]:
    if k not in st.session_state: st.session_state[k] = v



@st.cache_data(ttl=120, show_spinner=False)
def google_search(query: str, num: int = 10, search_type: str = "web") -> list:
    if not GOOGLE_API_KEY or not GOOGLE_CX_ID:
        st.error("❌ Missing API keys. Check your secrets.toml or Streamlit Cloud secrets.")
        return []
    try:
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CX_ID,
            "q": query,
            "num": min(num, 10),  # API max is 10 per request
            # FIX: These params force entire-web search regardless of UI toggle
            "filter": "1",           # deduplicate results
            "gl": "in",              # India region boost
            "lr": "lang_en",         # English results
            "safe": "active",        # SafeSearch
        }

        if search_type == "image":
            params["searchType"] = "image"
        else:
            #  KEY FIX: excludeTerms trick forces broader web results
            # when site restriction is active
            params["siteSearch"] = "www.google.com"
            params["siteSearchFilter"] = "e"  # 'e' = EXCLUDE → searches entire web

        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params=params,
            timeout=10
        )

        if r.status_code == 200:
            return r.json().get("items", [])
        elif r.status_code == 403:
            err = r.json().get("error", {})
            reason = err.get("errors", [{}])[0].get("reason", "unknown")
            if reason == "forbidden":
                st.error(" API Error: Custom Search API not enabled for this project. Go to Google Cloud Console → APIs & Services → Enable 'Custom Search JSON API'.")
            elif reason == "keyInvalid":
                st.error(" Invalid API key. Check GOOGLE_API_KEY in your secrets.")
            else:
                st.error(f" Google API Error 403: {err.get('message', 'Forbidden')}")
            return []
        elif r.status_code == 429:
            st.warning(" Daily quota exceeded (100 free searches/day). Try again tomorrow or upgrade your plan.")
            return []
        else:
            st.error(f" API Error {r.status_code}: {r.text[:200]}")
            return []

    except requests.exceptions.Timeout:
        st.error(" Request timed out. Check your internet connection.")
        return []
    except Exception as e:
        st.error(f" Unexpected error: {e}")
        return []


# ── Fetch more results (page 2) for num > 10 ──
@st.cache_data(ttl=120, show_spinner=False)
def google_search_extended(query: str, num: int = 20, search_type: str = "web") -> list:
    """Fetches up to 20 results using two API calls (API max is 10 per call)."""
    results = google_search(query, min(num, 10), search_type)
    if num > 10 and len(results) == 10:
        try:
            params = {
                "key": GOOGLE_API_KEY,
                "cx": GOOGLE_CX_ID,
                "q": query,
                "num": min(num - 10, 10),
                "start": 11,  # page 2
                "filter": "1",
                "gl": "in",
                "lr": "lang_en",
                "safe": "active",
            }
            if search_type == "image":
                params["searchType"] = "image"
            else:
                params["siteSearch"] = "www.google.com"
                params["siteSearchFilter"] = "e"

            r = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params, timeout=10
            )
            if r.status_code == 200:
                results += r.json().get("items", [])
        except: pass
    return results



# CSS — LOISEKK dark theme

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@400;500&display=swap');
html,body,[data-testid="stAppViewContainer"]{background:#080810!important;color:#f1f1f1;}
[data-testid="stMain"],[data-testid="block-container"]{
  background:#080810!important;padding:0 0 60px!important;max-width:860px;margin:0 auto;}
header,[data-testid="stHeader"],[data-testid="stToolbar"],footer,
[data-testid="stSidebar"],[data-testid="collapsedControl"],.stDeployButton{display:none!important;}
*{font-family:'DM Sans',sans-serif;}
h1,h2,h3,.logo{font-family:'Syne',sans-serif;}

/* Stagger fade-in */
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.rc{animation:fadeUp .3s ease both;}
.rc:nth-child(1){animation-delay:.05s}
.rc:nth-child(2){animation-delay:.10s}
.rc:nth-child(3){animation-delay:.15s}
.rc:nth-child(4){animation-delay:.20s}
.rc:nth-child(5){animation-delay:.25s}

/* Result card */
.rc{
  background:#0f0f1e;border:1px solid #1e1e38;border-radius:16px;
  padding:20px 22px;margin-bottom:10px;cursor:pointer;
  transition:border-color .18s,box-shadow .18s,transform .18s;
}
.rc:hover{border-color:#7c6aff;box-shadow:0 0 0 1px #7c6aff33,0 8px 32px #7c6aff15;transform:translateY(-1px);}
.rc-url{font-size:12px;color:#7c6aff;margin-bottom:5px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:6px;}
.rc-title{font-size:17px;font-weight:700;font-family:'Syne',sans-serif;color:#f1f1f1;
  margin-bottom:7px;line-height:1.3;}
.rc-snippet{font-size:14px;color:#777;line-height:1.6;}
.rc-badge{display:inline-block;background:#13132a;color:#7c6aff;
  border-radius:6px;padding:2px 9px;font-size:11px;margin-top:10px;font-weight:700;}

/* Image grid */
.img-card{border-radius:12px;overflow:hidden;background:#0f0f1e;
  border:1px solid #1e1e38;cursor:pointer;transition:transform .18s,border-color .18s;
  animation:fadeUp .3s ease both;}
.img-card:hover{transform:scale(1.03);border-color:#7c6aff;}
.img-card img{width:100%;height:155px;object-fit:cover;display:block;}
.img-card-title{padding:7px 10px;font-size:12px;color:#888;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}

/* History / related chips */
.chip{
  display:inline-block;background:#0f0f1e;border:1px solid #222240;
  border-radius:20px;padding:5px 16px;font-size:13px;cursor:pointer;
  color:#888;margin:3px;transition:all .15s;
}
.chip:hover{border-color:#7c6aff;color:#f1f1f1;background:#13132a;}

/* Meta bar */
.meta{font-size:13px;color:#444;margin:8px 0 16px;}
.pill{display:inline-block;background:#0f0f1e;border:1px solid #222240;
  border-radius:10px;padding:2px 10px;font-size:11px;color:#666;margin-right:5px;}

/* No results */
.no-results{
  text-align:center;padding:60px 0;color:#333;
}
.no-results .icon{font-size:48px;margin-bottom:16px;}
</style>""", unsafe_allow_html=True)


# HEADER

st.markdown("""
<div style="text-align:center;padding:36px 0 10px">
  <div style="font-size:38px;font-weight:800;letter-spacing:4px;font-family:'Syne',sans-serif;
    background:linear-gradient(90deg,#7c6aff,#b48bfa,#00d4aa);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent">
    ⬡ LOISEKK SEARCH
  </div>
  <div style="font-size:12px;color:#333;margin-top:6px;letter-spacing:2px;text-transform:uppercase;">
    India's Search Engine · Powered by Google
  </div>
</div>
""", unsafe_allow_html=True)

# ── API key warning ──
if not GOOGLE_API_KEY or not GOOGLE_CX_ID:
    st.error(" API keys not configured. Add `GOOGLE_API_KEY` and `GOOGLE_CX_ID` to your secrets.")
    st.code("""
# .streamlit/secrets.toml
GOOGLE_API_KEY = "AIzaSy..."
GOOGLE_CX_ID   = "b11c8dec6844f4432"
    """)
    st.stop()

# ── Query params ──
gq    = st.query_params.get("gq", "")
num_r = int(st.query_params.get("num", "10"))
tab   = st.query_params.get("tab", "web")


# SEARCH BAR

col_inp, col_btn = st.columns([5, 1])
with col_inp:
    query_input = st.text_input(
        "search", value=gq, placeholder="Search the entire web...",
        label_visibility="collapsed", key="search_input"
    )
with col_btn:
    go = st.button("Search 🔍", use_container_width=True, type="primary")

if go and query_input.strip():
    st.query_params["gq"]  = query_input.strip()
    st.query_params["tab"] = tab
    st.rerun()

# Handle Enter key via query param
if query_input.strip() and query_input.strip() != gq and not go:
    pass  # wait for button or rerun

# ── Controls when searching ──
if gq:
    c1, c2, c3 = st.columns([3, 1, 1])
    with c2:
        n = st.selectbox("Results", [5, 10, 20],
                         index=[5,10,20].index(num_r) if num_r in [5,10,20] else 1,
                         label_visibility="collapsed")
        if n != num_r:
            st.query_params["num"] = str(n); st.rerun()
    with c3:
        mode = st.radio("Mode", ["web", "image"], horizontal=True,
                        index=0 if tab == "web" else 1,
                        label_visibility="collapsed")
        if mode != tab:
            st.query_params["tab"] = mode; st.rerun()


# HISTORY (empty state)

if not gq:
    if st.session_state.history:
        st.markdown('<div style="margin-top:28px;font-size:12px;color:#444;letter-spacing:1px;text-transform:uppercase;">Recent</div>', unsafe_allow_html=True)
        chips = "".join(
            f'<a href="?gq={urllib.parse.quote(h)}" style="text-decoration:none"><span class="chip">{h}</span></a>'
            for h in st.session_state.history[-8:]
        )
        st.markdown(f'<div style="margin:10px 0 24px">{chips}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="no-results">
          <div class="icon">🔍</div>
          <div style="font-size:16px;color:#444;">Type something to search the web</div>
          <div style="font-size:13px;color:#333;margin-top:8px;">Anime · Gaming · Movies · Study · Music · Anything</div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()


# RUN SEARCH

if gq and gq not in st.session_state.history:
    st.session_state.history.insert(0, gq)
    st.session_state.history = st.session_state.history[:30]

with st.spinner(f"Searching for **{gq}**..."):
    results = google_search_extended(gq, num_r, tab)

# ── Meta bar ──
st.markdown(f"""
<div class="meta">
  <strong style="color:#f1f1f1">{len(results)}</strong> results for
  <strong style="color:#b48bfa">"{gq}"</strong>
  <span class="pill">{'🖼 Images' if tab=='image' else '🌐 Web'}</span>
  <span class="pill">India</span>
</div>
""", unsafe_allow_html=True)

if not results:
    st.markdown("""
    <div class="no-results">
      <div class="icon">😶</div>
      <div style="font-size:16px;color:#555;">No results found</div>
      <div style="font-size:13px;color:#333;margin-top:8px;">Try different keywords or check your API quota</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════
# RESULTS — WEB
# ══════════════════════════════════════════════════════
if tab == "web":
    for i, item in enumerate(results):
        title   = item.get("title", "—")
        link    = item.get("link", "#")
        snippet = item.get("snippet", "").replace("\n", " ")
        domain  = urllib.parse.urlparse(link).netloc.replace("www.", "")
        favicon = f"https://www.google.com/s2/favicons?domain={domain}&sz=16"
        path    = link.split(domain)[-1][:55] if domain in link else ""

        st.markdown(f"""
<div class="rc" onclick="window.open('{link}','_blank')">
  <div class="rc-url">
    <img src="{favicon}" style="width:14px;height:14px;vertical-align:middle;border-radius:3px;" onerror="this.style.display='none'">
    <span>{domain}</span>
    <span style="color:#333;">›</span>
    <span style="color:#555;">{path}</span>
  </div>
  <div class="rc-title">{title[:90]}</div>
  <div class="rc-snippet">{snippet[:220]}{'…' if len(snippet) > 220 else ''}</div>
  <span class="rc-badge">#{i+1}</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# RESULTS — IMAGES
# ══════════════════════════════════════════════════════
else:
    imgs = [r for r in results if r.get("link")]
    cols = st.columns(3)
    for i, item in enumerate(imgs):
        img_url = item.get("link", "")
        title   = item.get("title", "")[:40]
        page    = item.get("image", {}).get("contextLink", "#")
        with cols[i % 3]:
            st.markdown(f"""
<div class="img-card" onclick="window.open('{page}','_blank')">
  <img src="{img_url}"
    onerror="this.src='https://placehold.co/300x155/0f0f1e/7c6aff?text=No+Image'"
    loading="lazy">
  <div class="img-card-title">{title}</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# RELATED SEARCHES
# ══════════════════════════════════════════════════════
st.markdown('<hr style="border:none;border-top:1px solid #111;margin:28px 0 16px">', unsafe_allow_html=True)
st.markdown('<div style="font-size:12px;color:#444;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">Related</div>', unsafe_allow_html=True)

words = set()
for r in results[:5]:
    for w in r.get("title", "").split():
        if len(w) > 4 and w.lower() not in gq.lower() and w.isalpha():
            words.add(w.title())

chips = list(words)[:10]
if chips:
    chips_html = "".join(
        f'<a href="?gq={urllib.parse.quote(c)}" style="text-decoration:none"><span class="chip">{c}</span></a>'
        for c in chips
    )
    st.markdown(chips_html, unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div style="text-align:center;margin-top:48px;font-size:12px;color:#222;letter-spacing:2px;text-transform:uppercase;">
  LOISEKK · India's Platform · Built with 
</div>
""", unsafe_allow_html=True)
