from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    score_song,
    recommend_songs,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Robustness fixes uncovered by adversarial testing (see README) ---

def _song(**overrides):
    """Build a song dict with sensible defaults, overriding only what a test needs."""
    base = dict(
        id=1, title="Test", artist="A", genre="pop", mood="happy",
        energy=0.8, tempo_bpm=120, valence=0.5, danceability=0.5, acousticness=0.2,
    )
    base.update(overrides)
    return base


def test_non_numeric_energy_does_not_crash():
    # Fixes H: a string energy must be ignored, not raise TypeError.
    score, reasons = score_song({"genre": "pop", "energy": "high"}, _song())
    assert score == 0.3  # genre bonus only; energy silently ignored
    assert isinstance(reasons, list) and reasons


def test_out_of_range_energy_never_produces_negative_score():
    # Fixes B/C: energy far outside [0, 1] is clamped, so the score stays >= 0.
    for bad in (5.0, -1.0, 100.0):
        score, _ = score_song({"energy": bad}, _song(energy=0.2))
        assert score >= 0.0


def test_genre_and_mood_match_is_case_and_space_insensitive():
    # Fixes E: "Pop " and "Happy" should still match "pop" / "happy".
    score, _ = score_song({"genre": "Pop ", "mood": "  HAPPY"}, _song(genre="pop", mood="happy"))
    assert round(score, 2) == 0.50  # 0.30 genre + 0.20 mood


def test_empty_profile_is_labeled_as_no_preferences():
    # Fixes D: an empty profile must not masquerade as a real match.
    _, reasons = score_song({}, _song())
    assert reasons == ["no preferences given — showing a default sample"]


def test_no_match_is_distinct_from_no_preferences():
    # A stated-but-unmatched preference reads differently from an empty profile.
    _, reasons = score_song({"genre": "jazz"}, _song(genre="pop", energy=0.8))
    assert reasons == ["no strong match to your preferences"]


def test_energy_contribution_is_always_explained():
    # Fixes the "silent points" bug: even a not-perfect energy match is explained.
    _, reasons = score_song({"energy": 0.8}, _song(energy=0.6))  # closeness 0.8, not >= 0.9
    assert any("energy" in r for r in reasons)


def test_ties_are_broken_by_song_attributes_not_csv_order():
    # Fixes G: equal-genre ties resolve by valence (desc), deterministically.
    songs = [
        _song(id=1, title="LowValence", genre="lofi", valence=0.10),
        _song(id=2, title="HighValence", genre="lofi", valence=0.90),
    ]
    ranked = recommend_songs({"genre": "lofi"}, songs, k=2)
    assert [r[0]["title"] for r in ranked] == ["HighValence", "LowValence"]
