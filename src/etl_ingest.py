"""Load the checked-in CSV extracts into the MySQL warehouse."""

import argparse
import json
import os
import re
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DB_URI = os.getenv(
    "MYSQL_URI",
    "mysql+mysqlconnector://root:root@localhost:3306/spotify_analytics_dw",
)
LOAD_ORDER = [
    ("artists", "artists.csv"),
    ("tracks", "tracks.csv"),
    ("playlists", "playlists.csv"),
    ("playlist_tracks", "playlist_tracks.csv"),
    ("engagement_events", "engagement_events.csv"),
]
DELETE_ORDER = ["engagement_events", "playlist_tracks", "tracks", "artists", "playlists"]


def parse_raw_spotify_json(json_path: Path) -> pd.DataFrame:
    """Parse playlist items from legacy `track` or current `item` payloads."""
    with json_path.open(encoding="utf-8") as file:
        payload = json.load(file)

    rows = []
    for entry in payload.get("items", []):
        track = entry.get("item") or entry.get("track") or {}
        if not track or track.get("type", "track") != "track":
            continue
        spotify_url = track.get("external_urls", {}).get("spotify", "")
        match = re.search(r"track/([A-Za-z0-9]{22})(?:\?|$)", spotify_url)
        artists = track.get("artists") or []
        album = track.get("album") or {}
        duration_ms = track.get("duration_ms")
        rows.append({
            "track_id": match.group(1) if match else track.get("id"),
            "track_name": track.get("name"),
            "artist_id": artists[0].get("id") if artists else None,
            "album_name": album.get("name"),
            "release_date": album.get("release_date"),
            "duration_ms": duration_ms,
            "popularity_score": track.get("popularity"),
            "explicit": track.get("explicit"),
            "duration_mins": round(duration_ms / 60000, 2) if duration_ms is not None else None,
        })
    return pd.DataFrame(rows)


def load_warehouse(data_dir: Path = ROOT / "data" / "processed") -> None:
    """Replace the warehouse contents atomically, respecting foreign keys."""
    frames = {table: pd.read_csv(data_dir / filename) for table, filename in LOAD_ORDER}
    engine = create_engine(DB_URI)
    try:
        with engine.begin() as conn:
            for table in DELETE_ORDER:
                conn.execute(text(f"DELETE FROM `{table}`"))
            for table, _ in LOAD_ORDER:
                frames[table].to_sql(table, con=conn, if_exists="append", index=False, chunksize=500)
                print(f"[OK] Loaded {len(frames[table]):,} rows into `{table}`")
    finally:
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parse-only", action="store_true", help="Parse and preview raw JSON without connecting to MySQL")
    args = parser.parse_args()
    parsed = parse_raw_spotify_json(ROOT / "data" / "raw" / "raw_spotify_api_response.json")
    print(f"Parsed {len(parsed):,} tracks from raw JSON")
    if not parsed.empty:
        print(parsed[["track_id", "track_name", "duration_mins", "popularity_score"]].head(3).to_string(index=False))
    if not args.parse_only:
        load_warehouse()
