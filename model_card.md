# 🎧 Model Card: Music Recommender Simulation

## Model Name

**VibeMatch 1.0** — a small, content-based music recommender.

---

## Goal / Task

VibeMatch suggests songs for one listener. You give it three things: a favorite **genre**,
a **mood**, and a **target energy level** (calm to hype). It returns the **top 5 songs**
that fit best, and it shows a short reason for each pick. It is trying to predict which
songs match your stated taste.

---

## Data Used

- **Size:** 18 songs in a small hand-made CSV.
- **Variety:** 15 genres and 14 moods.
- **Features per song:** genre, mood, energy, tempo, valence, danceability, acousticness.
- **Limits:** The dataset is tiny. Most genres have only **one song** (12 of the 15). It
  has no lyrics, language, culture, or popularity data. So a "match" only means similar
  attributes, not music you would truly love.

---

## Algorithm Summary

Each song earns points in three ways:

- **Energy closeness (worth the most):** how near the song's energy is to your target.
- **Genre match:** a bonus if the genre is exactly yours.
- **Mood match (worth the least):** a smaller bonus if the mood matches.

The app adds up the points, sorts every song from highest to lowest, and shows the top 5.
Energy is worth the most because it is a smooth dial that can be *partly* right. Genre and
mood are simple yes/no bonuses. A perfect song scores about 1.0.

---

## Observed Behavior / Biases

- **Energy runs the show.** If your energy number and your genre disagree, energy usually
  wins. Ask for calm lofi but set a high energy, and you get loud rock and metal instead.
- **Mood barely counts.** A pop song with the wrong mood still beats a happy song from
  another genre. This is why *Gym Hero* (an intense track) keeps showing up when you ask
  for "Happy Pop" — it is pop and it is energetic, and mood is too weak to stop it.
- **Thin data hurts variety.** Because most genres have only one song, naming a genre often
  locks you to that single track no matter what mood or energy you pick.

Together these create a "loudness filter bubble": the system leans toward energetic songs
and can ignore the exact vibe the user asked for.

---

## Evaluation Process

- **Profiles:** I tested four listener types — Happy Pop, Gym (high energy), Chill study,
  and EDM party. I checked that the #1 pick made sense.
- **Comparisons:** I compared profiles in pairs. Calm and party profiles pulled to opposite
  ends of the catalog, which is what I hoped for.
- **Stress tests:** I ran "trick" profiles — bad numbers, an empty profile, and typos like
  `"Pop "`. These found real bugs, which I then fixed (no crashes, no negative scores,
  case-insensitive matching, honest labels).
- **Weight experiment:** I doubled the energy weight. That made one loud song show up even
  more often, which confirmed the energy bias.
- **Method:** I read and compared the outputs by hand. I did not compute number scores.

---

## Intended Use and Non-Intended Use

**Intended use.** This is a **classroom demo**. It is meant to show how a recommender turns
simple data into ranked picks, and where bias can sneak in. It works best for clear,
one-genre requests.

**Non-intended use.** It should **not** be used in a real music app, with real users, or for
any real decision. The catalog is tiny and it ignores most of what real taste is about, so
its picks are for learning only.

---

## Ideas for Improvement

1. **Add more songs per genre** so there is real choice when someone names a genre.
2. **Use the extra features** (valence, danceability, tempo) and make energy less dominant,
   so it stops overriding the user's genre and mood.
3. **Match similar moods** (treat *sad ≈ melancholy*) instead of requiring the exact word.

---

## Personal Reflection

My biggest learning moment was realizing that the recommender only does exactly what my
scoring rule tells it to do — nothing more. When "Gym Hero" kept showing up for people who
asked for "Happy Pop," it wasn't a bug. It was my weights doing their job. Energy and genre
were worth a lot, and mood was worth almost nothing, so a loud pop song beat a genuinely
happy one. Seeing that made the whole system click for me: the model optimizes the rule I
wrote, not the wish in the user's head.

AI tools helped me move fast. They were great for drafting the scoring code, coming up with
"trick" profiles I wouldn't have thought of, and turning my messy ideas into clean tables
and explanations. But I learned I still had to double-check them. When I applied the weight
experiment, the AI's change technically ran, but the weights no longer added up to 1.0 and
the scores went above 1.0. I only caught that by checking the math myself. I also had to
verify the actual outputs by running the code, not just trust that the description was
right. The rule I settled on: let AI draft and suggest, but I confirm the numbers and run
it before I believe it.

What surprised me most was how a simple pile of add-and-sort math can still "feel" like a
real recommendation. There is no learning, no history, and no magic — just three numbers
added together. But because it comes back with a ranked list and a confident reason for each
pick, it *feels* like the app knows me. That made me think differently about the real music
apps I use. When the same kind of song keeps coming up, it's probably not the app
understanding me — it's a weighting choice and a limited catalog.

If I kept going, I would first fix the thin data by adding more songs per genre, since that
was the biggest limit on variety. Then I would use the features I'm currently ignoring
(valence, danceability, tempo) and dial back how much energy dominates, so the system stops
overriding what the user actually asked for. After that, I'd try adding a small "people who
liked this also liked that" signal, so it could suggest something new instead of just
echoing my stated taste back at me.
