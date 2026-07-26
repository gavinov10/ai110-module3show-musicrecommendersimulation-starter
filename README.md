# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

**How real-world recommenders work (and what my version prioritizes).**
Large platforms like Spotify and YouTube predict what you'll enjoy by blending two
ideas: *collaborative filtering* ("people with similar taste liked this") and
*content-based filtering* ("this song's attributes resemble songs you already like").
They run these through massive two-stage pipelines that first narrow billions of items
down to a few candidates, then rank them. My simulation is deliberately smaller and
focuses on the **content-based** half: it ignores other users entirely and instead
scores each song purely by how closely its *attributes* match a single user's stated
taste profile. It prioritizes **matching the user's energy level and genre**, rewarding
songs whose "vibe" is closest to what the user asked for rather than just the loudest or
most popular tracks.

**How my `Recommender` computes a score.** For each song it applies a weighted
**Scoring Rule**:

- **Energy closeness (weight 0.5):** `1 − |target_energy − song_energy|` — rewards being
  *near* the target, not simply high or low.
- **Genre match (weight 0.3):** exact-match bonus.
- **Mood match (weight 0.2):** exact-match bonus.

Genre is weighted above mood because genre carries unique information, while mood overlaps
the energy signal. A **Ranking Rule** then sorts every song by score and returns the top
*k* recommendations.

### Algorithm Recipe (finalized)

For each song, `total_score` is the sum of three weighted signals, then songs are ranked
high-to-low and the top *k* are returned:

| Signal | Weight | How it's computed | Why this weight |
|---|---|---|---|
| **Energy closeness** | 0.5 | `1 − \|target_energy − song_energy\|` (both scaled 0–1) | Continuous and most discriminating — rewards being *near* the target, not just loud. |
| **Genre match** | 0.3 | `+0.3` on exact match, else `0` | Unique categorical info that can't be inferred from other fields. |
| **Mood match** | 0.2 | `+0.2` on exact match, else `0` | A bonus, not a pillar — mood overlaps energy/valence, so it's worth ~1.5× less than genre. |

Weights sum to **1.0**, so a perfect song scores ~1.0 and every score stays interpretable.
The design principle: **reward closeness, not magnitude**, and give the continuous signal
(energy) more room than the binary category matches so recommendations don't pile up on ties.

### Potential biases I expect

- **Genre over-prioritization.** With a small catalog and few genres, a genre match is
  common and adds a flat 0.3. The system may surface same-genre songs while ignoring great
  tracks that nail the user's *mood* but sit in a different genre.
- **Popularity/loudness is ignored, energy is not.** Because energy carries the most weight,
  a user with an unusual target energy can get recommendations that match the number but feel
  off in vibe, since mood only contributes a small tiebreaker.
- **Redundant-signal double counting.** Mood correlates with energy and valence, so a song
  can be rewarded twice for essentially the same "feel," subtly crowding out variety.
- **Cold, single-user view.** The system uses no collaborative signal, so it can never
  recommend something *outside* the stated profile — it reinforces existing taste rather than
  helping the user discover anything new (a filter-bubble effect).

**Features used in my simulation.**

Each `Song` uses:

| Field | Role |
|---|---|
| `id`, `title`, `artist` | identity (not scored) |
| `genre` | scored — categorical match |
| `mood` | scored — categorical match |
| `energy` | scored — numeric closeness |
| `tempo_bpm` | available (not yet scored) |
| `valence` | available (not yet scored) |
| `danceability` | available (not yet scored) |
| `acousticness` | available (not yet scored) |

Each `UserProfile` stores:

| Field | Role |
|---|---|
| `favorite_genre` | target for genre match |
| `favorite_mood` | target for mood match |
| `target_energy` | target for energy closeness |
| `likes_acoustic` | stored preference (available for future scoring) |

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Beyond the scoring biases noted under [How The System Works](#how-the-system-works), the
simulation carries a few structural limits:

- It runs on a tiny, hand-made catalog, so results won't generalize to real listening data.
- It scores only attributes — it has no sense of lyrics, language, or cultural context.
- It reflects a single stated profile, so it can reinforce a user's taste more than broaden it.

I go deeper on these trade-offs in the model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



