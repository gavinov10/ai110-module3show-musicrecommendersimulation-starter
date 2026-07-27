import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# --- Algorithm Recipe: scoring weights ---
# Genre is weighted higher than mood because genre carries unique information,
# while mood largely overlaps the energy/valence signals we already score.
# (A Weight Shift experiment — energy 1.0 / genre 0.15 — is documented in the README;
# it was reverted here because it broke the sum-to-1.0 scale without improving accuracy.)
W_ENERGY = 0.5   # numeric closeness
W_GENRE = 0.3    # exact genre match (worth more)
W_MOOD = 0.2     # exact mood match (worth less)


def _norm(text: Optional[str]) -> Optional[str]:
    """Normalize a categorical value for comparison: strip surrounding spaces and
    lowercase it, so 'Pop ', 'pop', and 'POP' all match. Returns None for blanks."""
    if text is None:
        return None
    cleaned = str(text).strip().lower()
    return cleaned or None


def _clamp01(x: float) -> float:
    """Clamp a number into the [0, 1] range so a score can never go negative or blow up."""
    return min(1.0, max(0.0, x))


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
    OOP implementation of the recommendation logic. It delegates to the same
    scoring functions used by the CLI (score_song / recommend_songs) so the two
    entry points can never drift apart.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog of songs this recommender will rank."""
        self.songs = songs

    @staticmethod
    def _prefs(user: UserProfile) -> Dict:
        """Translate a UserProfile into the dict shape the scoring functions expect."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for a user, ranked by score."""
        prefs = self._prefs(user)
        ranked = recommend_songs(prefs, [asdict(s) for s in self.songs], k=k)
        by_id = {s.id: s for s in self.songs}
        return [by_id[row[0]["id"]] for row in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable reason a song was recommended."""
        _, reasons = score_song(self._prefs(user), asdict(song))
        return "; ".join(reasons)

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

    Robustness rules (added after adversarial testing):
    - energy is validated and clamped to [0, 1]; a non-numeric energy is ignored,
      not fatal, and the closeness term is clamped so a score can never go negative;
    - genre/mood matches are case- and whitespace-insensitive;
    - the "why" always reports the energy contribution when it adds points;
    - a song with no matches is labeled honestly, distinguishing "no strong match"
      from "no preferences were given at all".

    Expected return format: (score, reasons)
    """
    score = 0.0
    reasons: List[str] = []

    # Did the user express any usable preference? Lets us tell "nothing matched"
    # apart from "you told me nothing to match on".
    gave_pref = False

    # 1. Numeric closeness on energy: 1.0 at an exact match, 0.0 at the far end.
    raw_energy = user_prefs.get("energy")
    target_energy: Optional[float] = None
    if raw_energy is not None:
        try:
            target_energy = _clamp01(float(raw_energy))  # tolerate out-of-range / string
        except (TypeError, ValueError):
            target_energy = None  # non-numeric energy: ignore instead of crashing

    if target_energy is not None:
        gave_pref = True
        closeness = _clamp01(1.0 - abs(target_energy - song["energy"]))  # both scaled 0..1
        points = W_ENERGY * closeness
        score += points
        # Faithful "why": report the energy contribution whenever it adds points,
        # not only on a near-perfect match, so the score is never left unexplained.
        if points > 0:
            if closeness >= 0.9:
                fit = "closely matches"
            elif closeness >= 0.6:
                fit = "is near"
            else:
                fit = "is somewhat far from"
            reasons.append(
                f"energy {song['energy']:.2f} {fit} your target "
                f"{target_energy:.2f} (+{points:.2f})"
            )

    # 2. Genre match (weighted higher — unique information).
    pref_genre = _norm(user_prefs.get("genre"))
    if pref_genre:
        gave_pref = True
        if _norm(song.get("genre")) == pref_genre:
            score += W_GENRE
            reasons.append(f"matches your favorite genre ({song['genre']}) (+{W_GENRE:.2f})")

    # 3. Mood match (weighted lower — overlaps energy/valence).
    pref_mood = _norm(user_prefs.get("mood"))
    if pref_mood:
        gave_pref = True
        if _norm(song.get("mood")) == pref_mood:
            score += W_MOOD
            reasons.append(f"matches your mood ({song['mood']}) (+{W_MOOD:.2f})")

    # 4. Honest fallback so an empty/garbage profile can't masquerade as a real match.
    if not reasons:
        reasons.append(
            "no strong match to your preferences" if gave_pref
            else "no preferences given — showing a default sample"
        )
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song, then returns the top k as (song, score, explanation).
    Required by src/main.py
    """
    # Score every song, building a (song, score, explanation) tuple for each.
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        s, reasons = score_song(user_prefs, song)
        scored.append((song, s, "; ".join(reasons)))

    # Deterministic, musical tie-break: among equal scores prefer higher valence,
    # then higher danceability, then title (alphabetical) — so ties are broken by
    # the songs themselves, never by their arbitrary row order in the CSV.
    scored.sort(key=lambda t: t[0]["title"])  # stable base: title ascending
    scored.sort(
        key=lambda t: (t[1], t[0].get("valence", 0.0), t[0].get("danceability", 0.0)),
        reverse=True,
    )
    return scored[:k]
