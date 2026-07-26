import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# --- Algorithm Recipe: scoring weights ---
# Genre is weighted higher than mood because genre carries unique information,
# while mood largely overlaps the energy/valence signals we already score.
W_ENERGY = 0.5   # numeric closeness
W_GENRE = 0.3    # exact genre match (worth more)
W_MOOD = 0.2     # exact mood match (worth less)

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file, converting numeric columns to floats.
    Required by src/main.py
    """
    numeric = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")
    songs: List[Dict] = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for col in numeric:
                row[col] = float(row[col])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences (Algorithm Recipe).

    Rule: reward *closeness*, not magnitude. A song whose energy is near the
    user's target scores high; a big gap scores low. Exact genre/mood matches
    add weighted bonuses, with genre worth more than mood.

    Expected return format: (score, reasons)
    """
    score = 0.0
    reasons: List[str] = []

    # 1. Numeric closeness on energy: 1.0 at an exact match, 0.0 at the far end.
    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        closeness = 1.0 - abs(target_energy - song["energy"])  # both scaled 0..1
        score += W_ENERGY * closeness
        if closeness >= 0.9:
            reasons.append(
                f"energy {song['energy']:.2f} is close to your target {target_energy:.2f}"
            )

    # 2. Genre match (weighted higher — unique information).
    if user_prefs.get("genre") and song.get("genre") == user_prefs["genre"]:
        score += W_GENRE
        reasons.append(f"matches your favorite genre ({song['genre']})")

    # 3. Mood match (weighted lower — overlaps energy/valence).
    if user_prefs.get("mood") and song.get("mood") == user_prefs["mood"]:
        score += W_MOOD
        reasons.append(f"matches your mood ({song['mood']})")

    if not reasons:
        reasons.append("partial vibe match")
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song, then returns the top k as (song, score, explanation).
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
