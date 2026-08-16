# W7SKW Ham Radio Study Extravaganza

Ham Radio Study Guide for Friends and Family.

A Home Screen web app covering all three US amateur radio license classes —
**Technician**, **General**, and **Amateur Extra** — with flashcard study and
full scored practice exams.

No code signing, no Apple Developer account, no 7-day expiry. It installs on any
number of iPhones and iPads by opening a link.

| License | Element | Pool | Questions | Exam | Pass |
|---|---|---|---|---|---|
| Technician | 2 | 2026–2030 | 409 | 35 | 26 |
| General | 3 | 2023–2027 | 423 | 35 | 26 |
| Amateur Extra | 4 | 2024–2028 | 599 | 50 | 37 |

**1,431 questions total.** Questions withdrawn by the NCVEC (9 in General,
4 in Extra) are excluded, so they can never appear in study or on an exam.

---

## Using it

Pick a license class on the home screen, then choose a mode. Each license keeps
its own scores and its own in-progress exam; they never mix.

**Study mode** — flashcards filtered by section or the entire pool. Tap a choice
for instant right/wrong feedback, or hit *Show Answer*. Shows the FCC rule
reference (§97.x) where the pool provides one. Swipe left/right between cards.
Optional shuffle.

**Exam mode** — questions are drawn the way a real VE session builds an exam:
**one random question from each group**, never a duplicate. That's 35 questions
for Technician and General, 50 for Extra. Answer order is shuffled by default so
you learn the answers rather than the letters.

- Move freely forward and back; skip a question and return to it
- *Review* screen: a grid of every question — coloured = answered (showing your
  letter), amber = skipped — plus a full list of your answers. Tap any square or
  row to jump straight to that question.
- *Finish Exam* opens a confirmation with **End Exam** or **Return to Exam**.
  If anything is unanswered it says how many and warns they're scored incorrect.
- Results: score ring, PASS / NOT PASSED against the real threshold, a
  per-section breakdown, and every missed question with your answer beside the
  correct one.

An exam in progress is saved automatically, so if the phone locks or a call comes
in, you're offered *Resume* when you come back.

Diagram questions (Technician T-1/T-2/T-3, General G7-1, and ten Extra figures)
render the schematic inline — tap it to view full screen.

---

## Installing on iPhone / iPad

The app must be served over **HTTPS** once, because iOS only allows offline
caching on a secure origin. After that first load it runs entirely offline.

Once it's published (see below), on each device:

1. Open the URL **in Safari** — this does not work from Chrome on iOS
2. Tap **Share** (square with an up arrow)
3. Scroll down and tap **Add to Home Screen**
4. Name it and tap **Add**
5. Launch it once from the Home Screen icon **while online** so it caches

After that it works in airplane mode. Send the same link to anyone else and they
do the same thing — nothing ever plugs into a Mac.

> **Use the Home Screen icon, not a Safari tab.** Installed web apps keep their
> stored data indefinitely; pages left in Safari can have local storage cleared
> after a period of disuse, which would wipe exam history.

---

## Publishing with GitHub Pages

The `docs/` folder is the whole site. With Pages set to serve `main` → `/docs`,
the app is live at:

```
https://kidvelvet.github.io/W7SKW-Ham-Radio-Extravaganza/
```

To enable it: **Settings → Pages → Source: Deploy from a branch → Branch: main,
folder: /docs → Save.** It goes live about a minute later.

---

## Rebuilding

`docs/index.html` is generated — edit `build/index.template.html`, not the output.

```bash
python3 build/extract.py   # re-reads the pools, writes build/pools.json + figures
python3 build/build.py     # injects data, regenerates docs/index.html and sw.js
```

`extract.py` cross-checks every question in each flashcard deck against that
pool's plain-text file — question text, correct answer, and all four choices —
and refuses to build on any mismatch or if a withdrawn question slipped in.

The service worker's cache name is a **content hash**, so each rebuild
automatically retires the old cache. There is no version number to remember to
bump; devices pick up the new build on next launch.

To preview locally:

```bash
python3 -m http.server 8734 --directory docs
```

Then open <http://localhost:8734>.

---

## Layout

```
docs/                    the published site
  index.html             the app (476 KB, all three pools baked in)
  sw.js                  generated service worker (offline cache)
  manifest.webmanifest   name, icon, standalone display
  icons/                 app icons
  figures/               14 schematic PNGs

build/
  index.template.html    editable source for the app
  extract.py             parses + validates the three pools
  build.py               generates docs/index.html and docs/sw.js
  pools.json             normalized question data

pools/                   original question pool files
```

---

## Notes

- Scores live in each device's local storage. Nothing is sent anywhere, there is
  no account, and no network request is made after install.
- Pool validity: Technician **2026–2030**, General **2023–2027**, Extra
  **2024–2028**. The General pool expires June 30 2027 and Extra June 30 2028 —
  drop the replacement files into `pools/`, adjust the paths in `extract.py`,
  and rebuild.
