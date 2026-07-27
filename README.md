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

============================================================
  Top 5 recommendations for you
  (genre=pop, mood=happy, energy=0.8)
============================================================

1. Sunrise City — Neon Echo
   Score: 0.99
   Why:
     • energy 0.82 closely matches your target 0.80 (+0.49)
     • matches your favorite genre (pop) (+0.30)
     • matches your mood (happy) (+0.20)

2. Gym Hero — Max Pulse
   Score: 0.73
   Why:
     • energy 0.93 is near your target 0.80 (+0.43)
     • matches your favorite genre (pop) (+0.30)

3. Rooftop Lights — Indigo Parade
   Score: 0.68
   Why:
     • energy 0.76 closely matches your target 0.80 (+0.48)
     • matches your mood (happy) (+0.20)

4. Concrete Kings — MC Vertex
   Score: 0.48
   Why:
     • energy 0.85 closely matches your target 0.80 (+0.48)

5. Night Drive Loop — Neon Echo
   Score: 0.47
   Why:
     • energy 0.75 closely matches your target 0.80 (+0.47)

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Adversarial / edge-case profiles

I asked my AI coding assistant to design user profiles meant to *trick* the scoring
logic, then ran each one and captured the top-5 terminal output below. Each profile
targets a specific weakness. Every block is real output from
`python -m src.main`-style runs (energy weight 0.5, genre 0.3, mood 0.2, `k=5`).

**A. Conflicting preferences — high energy but "sad" mood.** The user asks for *sad*
but gets *intense* and *happy*. `"sad"` isn't a catalog mood, so it silently scores 0
and energy+genre steamroll the emotional request — the contradiction is invisible.

```
============================================================
  Top 5 recommendations for you
  A. Conflicting preferences (high energy + sad mood)
  user_prefs = {'genre': 'pop', 'mood': 'sad', 'energy': 0.9}
============================================================

1. Gym Hero — Max Pulse
   Score: 0.78
   Why:
     • energy 0.93 is close to your target 0.90 (+0.48)
     • matches your favorite genre (pop) (+0.30)

2. Sunrise City — Neon Echo
   Score: 0.76
   Why:
     • energy 0.82 is close to your target 0.90 (+0.46)
     • matches your favorite genre (pop) (+0.30)

3. Storm Runner — Voltline
   Score: 0.49
   Why:
     • energy 0.91 is close to your target 0.90 (+0.49)

4. Neon Pulse — Voltage Kids
   Score: 0.48
   Why:
     • energy 0.95 is close to your target 0.90 (+0.48)

5. Concrete Kings — MC Vertex
   Score: 0.47
   Why:
     • energy 0.85 is close to your target 0.90 (+0.47)
```

**B. Out-of-range energy (5.0).** Energy closeness is unclamped, so `1 − |5.0 − e|`
goes deeply negative. Songs that match *both* genre and mood surface with **negative
scores next to positive reasons** — score and explanation openly disagree.

```
============================================================
  Top 5 recommendations for you
  B. Out-of-range energy (5.0)
  user_prefs = {'genre': 'pop', 'mood': 'happy', 'energy': 5.0}
============================================================

1. Sunrise City — Neon Echo
   Score: -1.09
   Why:
     • matches your favorite genre (pop) (+0.30)
     • matches your mood (happy) (+0.20)

2. Gym Hero — Max Pulse
   Score: -1.24
   Why:
     • matches your favorite genre (pop) (+0.30)

3. Rooftop Lights — Indigo Parade
   Score: -1.42
   Why:
     • matches your mood (happy) (+0.20)

4. Iron Verdict — Ashfall
   Score: -1.52
   Why:
     • partial vibe match

5. Neon Pulse — Voltage Kids
   Score: -1.52
   Why:
     • partial vibe match
```

**C. Negative energy (-1.0).** The energy axis effectively inverts: the *calmest*
songs rank first because they're "least far" from −1.0, and nothing warns the user.

```
============================================================
  Top 5 recommendations for you
  C. Negative energy (-1.0)
  user_prefs = {'mood': 'happy', 'energy': -1.0}
============================================================

1. Winter Elegy — Anya Sokolova
   Score: -0.11
   Why:
     • partial vibe match

2. Spacewalk Thoughts — Orbit Bloom
   Score: -0.14
   Why:
     • partial vibe match

3. Cabin Smoke — The Willows
   Score: -0.15
   Why:
     • partial vibe match

4. Library Rain — Paper Lanterns
   Score: -0.18
   Why:
     • partial vibe match

5. Rooftop Lights — Indigo Parade
   Score: -0.18
   Why:
     • matches your mood (happy) (+0.20)
```

**D. Empty profile.** With no preferences every song scores 0.00 and the system
returns the first five CSV rows in file order — dressed up as "recommendations."

```
============================================================
  Top 5 recommendations for you
  D. Empty profile
  user_prefs = {}
============================================================

1. Sunrise City — Neon Echo
   Score: 0.00
   Why:
     • partial vibe match

2. Midnight Coding — LoRoom
   Score: 0.00
   Why:
     • partial vibe match

3. Storm Runner — Voltline
   Score: 0.00
   Why:
     • partial vibe match

4. Library Rain — Paper Lanterns
   Score: 0.00
   Why:
     • partial vibe match

5. Gym Hero — Max Pulse
   Score: 0.00
   Why:
     • partial vibe match
```

**E. Case / whitespace mismatch.** The user *did* express a clear taste, but `"Pop "`
(capital P, trailing space) and `"Happy"` fail the exact-string match, so the profile
silently degrades to the empty-profile result above. Realistic front-end typos produce
garbage that looks intentional.

```
============================================================
  Top 5 recommendations for you
  E. Case / whitespace mismatch
  user_prefs = {'genre': 'Pop ', 'mood': 'Happy'}
============================================================

1. Sunrise City — Neon Echo
   Score: 0.00
   Why:
     • partial vibe match

2. Midnight Coding — LoRoom
   Score: 0.00
   Why:
     • partial vibe match

3. Storm Runner — Voltline
   Score: 0.00
   Why:
     • partial vibe match

4. Library Rain — Paper Lanterns
   Score: 0.00
   Why:
     • partial vibe match

5. Gym Hero — Max Pulse
   Score: 0.00
   Why:
     • partial vibe match
```

**F. Boundary energy = 1.0.** The README claims the design "rewards closeness, not
magnitude" — but at `target = 1.0`, closeness becomes monotonic in loudness, so it just
picks the loudest tracks (metal, edm). The stated safeguard evaporates at the extreme.

```
============================================================
  Top 5 recommendations for you
  F. Boundary energy = 1.0 (magnitude test)
  user_prefs = {'energy': 1.0}
============================================================

1. Iron Verdict — Ashfall
   Score: 0.48
   Why:
     • energy 0.97 is close to your target 1.00 (+0.48)

2. Neon Pulse — Voltage Kids
   Score: 0.47
   Why:
     • energy 0.95 is close to your target 1.00 (+0.47)

3. Gym Hero — Max Pulse
   Score: 0.47
   Why:
     • energy 0.93 is close to your target 1.00 (+0.47)

4. Storm Runner — Voltline
   Score: 0.46
   Why:
     • energy 0.91 is close to your target 1.00 (+0.46)

5. Concrete Kings — MC Vertex
   Score: 0.42
   Why:
     • partial vibe match
```

**G. Genre-only (mass ties).** Every lofi song scores exactly 0.30; ordering is decided
purely by CSV row order (stable sort), not by any musical relevance. The "ranking" among
matches is an illusion.

```
============================================================
  Top 5 recommendations for you
  G. Genre-only (mass ties)
  user_prefs = {'genre': 'lofi'}
============================================================

1. Midnight Coding — LoRoom
   Score: 0.30
   Why:
     • matches your favorite genre (lofi) (+0.30)

2. Library Rain — Paper Lanterns
   Score: 0.30
   Why:
     • matches your favorite genre (lofi) (+0.30)

3. Focus Flow — LoRoom
   Score: 0.30
   Why:
     • matches your favorite genre (lofi) (+0.30)

4. Sunrise City — Neon Echo
   Score: 0.00
   Why:
     • partial vibe match

5. Storm Runner — Voltline
   Score: 0.00
   Why:
     • partial vibe match
```

**H. Non-numeric energy.** A plausible natural-language value (`"high"`) is never
validated, so the subtraction throws and the whole run crashes instead of degrading
gracefully.

```
Traceback (most recent call last):
  File "src/main.py", line 27, in main
    recommendations = recommend_songs(user_prefs, songs, k=5)
  File "src/recommender.py", line 123, in recommend_songs
    for score, reasons in [score_song(user_prefs, song)]
  File "src/recommender.py", line 91, in score_song
    closeness = 1.0 - abs(target_energy - song["energy"])  # both scaled 0..1
TypeError: unsupported operand type(s) for -: 'str' and 'float'
```

### Does one song dominate every list? (variety check)

The prompt to watch for: *"If the same song keeps appearing at the top of every list,
your genre weight might be too strong, or your dataset might be too small."* I tested
both halves.

**Catalog-level: no single song dominates.** I ran **1,084 profiles** spanning every
genre × mood × energy combination (plus genre-only, mood-only, energy-only profiles) and
tallied which song landed at #1.

```
Distinct songs that ever reached #1:  18 / 18
Songs that NEVER appeared in any top-5: 0 / 18

Most frequent #1 song (out of 1084 profiles):
    89  ( 8.2%)  Island Time
    83  ( 7.7%)  Dusty Backroads
    79  ( 7.3%)  Winter Elegy
    78  ( 7.2%)  Iron Verdict
```

No song holds the top spot more than **8.2%** of the time, and all 18 songs reach both
#1 and the top-5. The "same song every list" symptom does **not** occur here.

**Is the genre weight too strong? No — and lowering it slightly *hurts* variety.** I
swept `W_GENRE` from 0.0 to 2.0 across the same 1,084 profiles:

```
 W_GENRE | #distinct #1 | most frequent #1 (share)
---------+--------------+--------------------------
     0.0 |      17      | Iron Verdict (14%)
     0.1 |      18      | Iron Verdict (11%)
     0.3 |      18      | Island Time  ( 8%)   <- default
     0.6 |      18      | Winter Elegy ( 7%)
     1.0 |      18      | Winter Elegy ( 7%)
     2.0 |      18      | Winter Elegy ( 7%)
```

Raising the genre weight keeps variety high; setting it to **0** actually concentrates
results (only 17 distinct #1s, and high-energy Iron Verdict jumps to 14%). The reason is
structural: this catalog has **15 genres for 18 songs**, so a genre bonus can't pile
same-genre songs on top of each other — there usually aren't any. Genre acts as a
tie-breaker here, not a homogenizer.

**The real limit is the dataset, not the weight.** The moment a user names a genre,
**12 of 15 genres contain exactly one song**, so that lone song wins its genre almost
regardless of mood or energy:

```
genre        #songs   dominant #1 (share across all mood/energy combos)
-------------------------------------------------------------------------
reggae         1       Island Time          (86%)
r&b            1       Velvet Hours         (86%)
country        1       Dusty Backroads      (86%)
jazz           1       Coffee Shop Stories  (82%)
synthwave      1       Night Drive Loop     (82%)
indie pop      1       Rooftop Lights       (81%)
...
pop            2       Sunrise City         (54%)
lofi           3       Midnight Coding      (48%)
```

Genres with only one song lock to that song 68–86% of the time; the two genres with
multiple songs (pop, lofi) are the *only* ones where mood and energy meaningfully
re-order the top pick (54% and 48%). **Verdict: the genre weight is well-calibrated for
this catalog — the constraint is dataset size/depth per genre.** The fix is more songs
per genre (so mood/energy have something to choose between), not reweighting.

### Small data experiment: Weight Shift (double energy, halve genre)

To test how sensitive the rankings are to the scoring weights, I doubled energy and
halved genre — `W_ENERGY 0.5 → 1.0`, `W_GENRE 0.3 → 0.15`, mood unchanged at `0.2` — and
re-ran the same profiles. (I changed only the weight constants, then reverted them; the
committed code keeps the original 0.5 / 0.3 / 0.2.)

**Canonical profile — barely moves.** For `{genre: pop, mood: happy, energy: 0.8}` the
top pick is unchanged and only ranks #2/#3 swap: the extra energy weight nudges the
happy/near-target *Rooftop Lights* above the intense *Gym Hero*.

```
{genre: pop, mood: happy, energy: 0.8}

BASELINE (e0.5 g0.3 m0.2)              SHIFTED (e1.0 g0.15 m0.2)
  1. 0.99  Sunrise City   (pop)          1. 1.33  Sunrise City   (pop)
  2. 0.73  Gym Hero       (pop)          2. 1.16  Rooftop Lights (indie pop)  ↑
  3. 0.68  Rooftop Lights (indie pop)    3. 1.02  Gym Hero       (pop)        ↓
  4. 0.48  Concrete Kings (hip-hop)      4. 0.95  Concrete Kings (hip-hop)
  5. 0.47  Night Drive    (synthwave)    5. 0.95  Night Drive    (synthwave)
```

**Conflicting profile — the ranking flips completely.** For a user who wants *lofi &
chill* but sets a high `energy: 0.9`, the shift lets energy override the stated genre.
The baseline respects "lofi" and returns three quiet lofi tracks; the shifted version
throws all of them out for loud rock/metal/edm — the user asked for chill lofi and got
*Iron Verdict* (metal, angry).

```
{genre: lofi, mood: chill, energy: 0.9}   <- contradictory: chill genre, high energy

BASELINE (e0.5 g0.3 m0.2)              SHIFTED (e1.0 g0.15 m0.2)
  1. 0.76  Midnight Coding (lofi)         1. 0.99  Storm Runner   (rock, intense)
  2. 0.72  Library Rain    (lofi)         2. 0.97  Gym Hero       (pop, intense)
  3. 0.55  Focus Flow      (lofi)         3. 0.95  Neon Pulse     (edm, euphoric)
  4. 0.49  Storm Runner    (rock)         4. 0.95  Concrete Kings (hip-hop)
  5. 0.48  Gym Hero        (pop)          5. 0.93  Iron Verdict   (metal, angry)
```

**Effect on variety (all 1,084 profiles).**

```
BASELINE: 18/18 distinct #1  |  most frequent #1: Island Time  ( 8.2%)
SHIFTED : 18/18 distinct #1  |  most frequent #1: Iron Verdict (11.9%)
```

**What I learned.** The system is *locally* robust (clear, non-conflicting profiles hardly
move) but *sensitive at the edges*: when genre and energy disagree, the weights decide who
wins, and halving genre hands the decision entirely to energy. The variety numbers reinforce
the earlier finding — a bigger energy weight concentrates results on the loudest tracks
(*Iron Verdict* rises from 8% to 12% of all #1 spots), so energy weight, not genre weight,
is what pushes this catalog toward same-song monotony.

### Applying the Weight Shift to the code and re-running `main.py`

I applied the shift directly in `recommender.py` (`W_ENERGY 0.5→1.0`, `W_GENRE 0.3→0.15`)
and re-ran `python -m src.main` on the default profile.

```
============================================================
  Top 5 recommendations for you
  (genre=pop, mood=happy, energy=0.8)
============================================================

1. Sunrise City — Neon Echo
   Score: 1.33
   Why:
     • energy 0.82 is close to your target 0.80 (+0.98)
     • matches your favorite genre (pop) (+0.15)
     • matches your mood (happy) (+0.20)

2. Rooftop Lights — Indigo Parade
   Score: 1.16
   Why:
     • energy 0.76 is close to your target 0.80 (+0.96)
     • matches your mood (happy) (+0.20)

3. Gym Hero — Max Pulse
   Score: 1.02
   Why:
     • matches your favorite genre (pop) (+0.15)

4. Concrete Kings — MC Vertex
   Score: 0.95
   Why:
     • energy 0.85 is close to your target 0.80 (+0.95)

5. Night Drive Loop — Neon Echo
   Score: 0.95
   Why:
     • energy 0.75 is close to your target 0.80 (+0.95)
```

**Is the math still valid?** I recomputed every song's score independently
(`W_ENERGY·(1−|Δenergy|) + genre_bonus + mood_bonus`) and all 18 matched exactly — the
scoring logic is internally consistent. The *one* caveat: the weights now sum to **1.35**,
so scores are no longer normalized to `[0, 1]` (*Sunrise City* scores 1.33, and a perfect
match could reach 1.35). Ranking is unaffected, but the README's "perfect ≈ 1.0"
interpretation no longer holds under this experiment.

**More accurate, or just different?** Mostly **just different**, and *worse* at the edges:

- **Same top pick.** *Sunrise City* still wins; only #2 and #3 swap — the heavier energy
  weight lifts the happy, near-target *Rooftop Lights* over the off-mood *Gym Hero*. That
  single swap is arguably a *small* accuracy gain (it better honors "happy").
- **But genre is now nearly ignored.** *Gym Hero* (a genuine pop match) sits at #3 scoring
  only for genre, while non-pop tracks with good energy crowd the list. As the earlier
  Tension test showed, a user who asks for "lofi" can now be handed rock/metal, because a
  0.15 genre bonus can't outweigh a ~1.0 energy term.
- **Loudness monotony increases.** Across all 1,084 profiles the most-frequent #1 song rose
  from 8.2% to 11.9% — less variety, not more.
- **The scale broke.** Scores above 1.0 make the "why" harder to read and the design's
  interpretability guarantee no longer holds.

**Verdict:** the change makes results *different* without making them meaningfully more
accurate, and it regresses genre fidelity, variety, and score interpretability — so I
**reverted to the original 0.5 / 0.3 / 0.2 weights** for the committed code.

### What these experiments revealed — and the fixes now applied

> **Note:** the adversarial outputs above were captured against the *original* scoring
> logic to expose its weaknesses. The fixes below are now implemented in
> `src/recommender.py` and locked in by tests in `tests/test_recommender.py`, so
> re-running those profiles today produces the safe behavior described here (no crashes,
> no negative scores, case-insensitive matching, honest empty-profile labels).

- ✅ **Validate & clamp `energy`** to numeric `[0, 1]`, and clamp energy closeness to
  `[0, 1]` so scores can never go negative (fixed B, C, H). A non-numeric energy is now
  ignored instead of crashing.
- ✅ **Normalize categorical matches** — `.strip()` + lowercase both sides — so realistic
  typos like `"Pop "` still match (fixed E).
- ✅ **Distinguish "no preference" from "no match"** — an empty profile is labeled
  *"no preferences given — showing a default sample"* rather than masquerading as a real
  recommendation (fixed D and E's silent degradation).
- ✅ **Make the "Why" faithful to the score** — the energy contribution is now reported
  whenever it adds points (with a *closely matches / is near / is somewhat far from*
  label), so a song like *Gym Hero* no longer shows a score with no visible energy reason
  (fixed the A–C mismatch).
- ✅ **Break ties with song attributes** — equal scores now resolve by valence, then
  danceability, then title, deterministically, instead of falling back to CSV row order
  (fixed G).
- ⬜ **Add depth per genre, not weight tuning** — *(data change, not yet done)* the variety
  check shows the top-of-list monotony comes from 12/15 genres having a single song, so
  mood/energy have nothing to choose between. More songs per genre is the real fix, not
  lowering `W_GENRE`.

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



