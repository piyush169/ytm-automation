import logging
import re
import subprocess
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional, Tuple

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- Configuration & Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Music Downloader API")
MUSIC_ROOT = Path("/music")

class DownloadRequest(BaseModel):
    url: str
    title: str = "Unknown Title"
    artist: str = "Unknown Artist"
    album: Optional[str] = None

# --- Helper Functions ---

def safe_filename(s: str) -> str:
    """Sanitizes strings for filesystem safety."""
    s = (s or "").strip()
    s = re.sub(r'[\/\\\?\%\*\:\|"<>\n\r\t]', "_", s)
    return re.sub(r"\s+", " ", s).strip() or "Unknown"

def get_similarity(a: str, b: str) -> float:
    """Returns a similarity ratio between two strings."""
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()

def fetch_album_metadata(title: str, artist: str) -> Tuple[Optional[str], str]:
    """Queries MusicBrainz to find the most likely album for a track."""
    try:
        query = f'recording:"{title}" AND artist:"{artist}"'
        url = "https://musicbrainz.org/ws/2/recording"
        headers = {"User-Agent": "music-downloader/1.1 (n8n-pipeline)"}
        params = {"query": query, "fmt": "json", "limit": 5}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        best_album = None
        highest_score = 0.0

        for rec in data.get("recordings", []):
            mb_score = float(rec.get("score", 0)) / 100.0
            rec_title = rec.get("title", "")
            
            # Extract artist name from credit list
            credits = rec.get("artist-credit", [])
            rec_artist = credits[0].get("name", "") if credits else ""

            # Calculate weighted confidence score
            title_sim = get_similarity(title, rec_title)
            artist_sim = get_similarity(artist, rec_artist)
            score = (0.5 * mb_score) + (0.3 * title_sim) + (0.2 * artist_sim)

            releases = rec.get("releases", [])
            if releases and score > highest_score:
                highest_score = score
                best_album = releases[0].get("title")

        if best_album and highest_score >= 0.7:
            return best_album, "musicbrainz"
            
    except Exception as e:
        logger.warning(f"MusicBrainz lookup failed: {e}")
        
    return None, "fallback"

# --- API Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "online", "storage_ready": MUSIC_ROOT.exists()}

@app.post("/download")
async def download_track(req: DownloadRequest):
    logger.info(f"Received request: {req.artist} - {req.title}")
    
    # 1. Resolve Metadata
    raw_title = req.title.strip()
    raw_artist = req.artist.strip()
    
    if req.album and req.album.strip():
        raw_album = req.album.strip()
        album_source = "request"
    else:
        inferred, album_source = fetch_album_metadata(raw_title, raw_artist)
        raw_album = inferred if inferred else "Singles"

    # 2. Setup File Paths
    artist_dir = safe_filename(raw_artist)
    album_dir = safe_filename(raw_album)
    file_name = safe_filename(raw_title)
    
    out_dir = MUSIC_ROOT / artist_dir / album_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    
    target_path = out_dir / f"{file_name}.mp3"
    temp_template = str(out_dir / f"{file_name}.%(ext)s")

    # 3. Execute Download (yt-dlp)
    # Note: We strip playlist/radio params to avoid downloading entire lists
    clean_url = req.url.split('&')[0] if 'watch?v=' in req.url else req.url
    
    ytdl_cmd = [
        "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0",
        "--no-playlist", "-o", temp_template, clean_url
    ]
    
    result = subprocess.run(ytdl_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"yt-dlp error: {result.stderr}")
        raise HTTPException(status_code=500, detail="Download failed")

    # 4. Tagging (ffmpeg)
    # We create a temporary tagged file then rename it to ensure atomic writes
    tagged_path = out_dir / f"{file_name}.tagged.mp3"
    
    tag_cmd = [
        "ffmpeg", "-y", "-i", str(target_path),
        "-metadata", f"title={raw_title}",
        "-metadata", f"artist={raw_artist}",
        "-metadata", f"album={raw_album}",
        "-metadata", f"album_artist={raw_artist}",
        "-codec", "copy", str(tagged_path)
    ]
    
    tag_result = subprocess.run(tag_cmd, capture_output=True, text=True)
    if tag_result.returncode == 0 and tagged_path.exists():
        tagged_path.replace(target_path)
        logger.info(f"Successfully downloaded and tagged: {target_path}")
    else:
        logger.warning("Tagging failed, original file kept.")

    return {
        "status": "success",
        "path": str(target_path),
        "metadata": {
            "title": raw_title,
            "artist": raw_artist,
            "album": raw_album,
            "source": album_source
        }
    }
