"""Download sample portrait images and enroll watchlist face embeddings."""

import urllib.request
from pathlib import Path

from sqlalchemy.orm import Session

from ..models import WatchlistPerson
from .face_ai import enroll_face_from_bytes, embedding_to_json

FACES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "watchlist_faces"

# Distinct portrait samples for demo enrollment (public domain / CC0 style sources)
PORTRAIT_URLS = {
    "john_moyo.jpg": "https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=400",
    "sarah_chikwanha.jpg": "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=400",
    "tendai_ncube.jpg": "https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=400",
}

NAME_TO_FILE = {
    "John Moyo": "john_moyo.jpg",
    "Sarah Chikwanha": "sarah_chikwanha.jpg",
    "Tendai Ncube": "tendai_ncube.jpg",
}


def _download_portraits() -> None:
    FACES_DIR.mkdir(parents=True, exist_ok=True)
    for filename, url in PORTRAIT_URLS.items():
        path = FACES_DIR / filename
        if path.exists():
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HSUSMS/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                path.write_bytes(resp.read())
        except Exception:
            pass


def enroll_watchlist_faces(db: Session) -> None:
    """Enroll embeddings for seed watchlist persons without embeddings."""
    _download_portraits()
    people = db.query(WatchlistPerson).filter(WatchlistPerson.active == True).all()
    for person in people:
        if person.face_embedding:
            continue
        filename = NAME_TO_FILE.get(person.full_name)
        if not filename:
            continue
        path = FACES_DIR / filename
        if not path.exists():
            continue
        emb_json, meta = enroll_face_from_bytes(path.read_bytes())
        if emb_json:
            person.face_embedding = emb_json
            person.photo_file = filename
    db.commit()
