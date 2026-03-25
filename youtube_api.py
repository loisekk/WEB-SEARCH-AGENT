"""
youtube_api.py — YouTube search helper for app.py
Returns video_id, title, channel, channel_id, channel_thumb, thumb
"""
import os
from dotenv import load_dotenv
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def _yt_service():
    from googleapiclient.discovery import build
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def search_videos(query: str, max_results: int = 20) -> list[dict]:
    if not YOUTUBE_API_KEY:
        return []
    try:
        service  = _yt_service()
        response = service.search().list(
            q=query, part="snippet",
            maxResults=max_results, type="video", safeSearch="none",
        ).execute()

        results = []
        channel_ids = []
        for item in response.get("items", []):
            cid = item["snippet"]["channelId"]
            results.append({
                "video_id":    item["id"]["videoId"],
                "title":       item["snippet"]["title"],
                "channel":     item["snippet"]["channelTitle"],
                "channel_id":  cid,
                "channel_thumb": "",   # filled below
                "thumb":       item["snippet"]["thumbnails"]["high"]["url"],
            })
            channel_ids.append(cid)

        # Batch fetch channel thumbnails (one API call)
        if channel_ids:
            ch_resp = service.channels().list(
                part="snippet",
                id=",".join(set(channel_ids)),
                maxResults=50,
            ).execute()
            ch_map = {}
            for ch in ch_resp.get("items", []):
                ch_map[ch["id"]] = ch["snippet"]["thumbnails"]["default"]["url"]
            for r in results:
                r["channel_thumb"] = ch_map.get(r["channel_id"], "")

        return results
    except Exception as e:
        print(f"[youtube_api] search_videos error: {e}")
        return []

def search_shorts(query: str, max_results: int = 12) -> list[dict]:
    return search_videos(f"{query} #shorts", max_results=max_results)