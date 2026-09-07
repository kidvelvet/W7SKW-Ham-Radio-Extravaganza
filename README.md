# W7SKW Ham Radio Study Extravaganza

Ham Radio Study Guide for Friends and Family.

A Home Screen web app covering all three US amateur radio license classes —
**Technician**, **General**, and **Amateur Extra** — with flashcard study,
sourced answer explanations, and full scored practice exams.

No code signing, no Apple Developer account, no 7-day expiry. It installs on any
number of iPhones and iPads by opening a link.

**Live:** <https://kidvelvet.github.io/W7SKW-Ham-Radio-Extravaganza/>

| License | Element | Pool | Questions | Exam | Pass | Explanations |
|---|---|---|---|---|---|---|
| Technician | 2 | 2026–2030 | 409 | 35 | 26 | **409 / 409** |
| General | 3 | 2023–2027 | 423 | 35 | 26 | **423 / 423** |
| Amateur Extra | 4 | 2024–2028 | 599 | 50 | 37 | **599 / 599** |

**Every question in all three pools has a sourced explanation.**

**1,431 questions total.** Questions withdrawn by the NCVEC (9 in General,
4 in Extra) are excluded, so they can never appear in study or on an exam.

---

## Using it

Pick a license class on the home screen, then choose a mode. Each license keeps
its own scores and its own in-progress exam; they never mix.

**Study mode** — flashcards filtered by section or the entire pool. Tap a choice
for instant right/wrong feedback, or hit *Show Answer*. Shows the FCC rule
reference (§97.x) where the pool provides one, plus a **sourced explanation** of
why the answer is right. Swipe left/right between cards. Optional shuffle.

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

**Explanations never appear in exam mode.** They are rendered only from the study
path, so an exam is always a clean test.

**History** — every exam is scored and kept on the device, with best and average
on the home screen.

An exam in progress is saved automatically, so if the phone locks or a call comes
in, you're offered *Resume* when you come back.

Diagram questions (Technician T-1/T-2/T-3, General G7-1, and ten Extra figures)
render the schematic inline — tap it to view full screen.

---

## Answer explanations

Each explanation is under 150 words and cites its authority, ranked by
reliability:

1. **47 CFR Part 97** — the amateur service rules themselves
2. **Other FCC sources** — §1.1310 exposure limits, OET Bulletin 65, PRB-1,
   Public Notice DA 16-1048
3. **ARRL** — Handbook, Antenna Book, band plans, NTS and ARES practice
4. **Peer-reviewed engineering** — IEEE standards (145, 270, 315, C95.1),
   ITU-R and ITU-T recommendations, NFPA 70, IEC, IPC, OSHA, BIPM/SI, ETSI
5. **Third-party study sites** — avoided entirely; none are cited

Part 97 quotations are taken from the full regulation text in `sources/`, fetched
from the eCFR API, rather than from memory. Where no authority states a fact
directly the explanation derives it, so numbers like the 19-inch 2-meter
quarter wave or the 300/frequency shortcut can be rebuilt from first principles.

The build refuses to run if any explanation exceeds 150 words or references a
question id that does not exist. `add_expl.py` also rejects a batch containing an
em dash or common AI-vocabulary tells before it can be merged.

Across all 1,431 explanations: 51,000 words, averaging 36 each (range 20 to 57).
Sources break down as 227 citing Part 97 directly, 27 other FCC material, 354
ARRL and other amateur organizations, and 823 peer-reviewed engineering
standards. Every calculated answer was recomputed rather than recalled.

---

## Installing on iPhone / iPad

The app must be served over **HTTPS** once, because iOS only allows offline
caching on a secure origin. After that first load it runs entirely offline.

On each device:

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

### On a Mac

Open the URL in Safari, then **File → Add to Dock**. You get a real app with its
own window, Dock icon and Launchpad entry. Chrome and Edge offer the same thing
under **⋮ → Cast, Save and Share → Install page as app**.

Scores are stored per device and per origin. A Mac install, an iPhone install and
a `localhost` copy all keep separate history; there is no sync.

---

## Publishing with GitHub Pages

The `docs/` folder is the whole site. With Pages set to serve `main` → `/docs`,
the app is live at the URL above.

To enable it: **Settings → Pages → Source: Deploy from a branch → Branch: main,
folder: /docs → Save.**

---

## Rebuilding

Everything in `docs/` is generated — edit the sources in `build/`, not the output.

```bash
python3 build/extract.py   # parses + validates the pools, merges explanations
python3 build/build.py     # assembles docs/, regenerates sw.js
```

To add explanations, write a batch keyed by question id and merge it:

```bash
python3 build/add_expl.py batch.json
```

`add_expl.py` refuses a batch that overwrites an existing entry without
`_overwrite`, exceeds 150 words, contains an em or en dash, or trips its
AI-vocabulary check.

`extract.py` cross-checks every question in each flashcard deck against that
pool's plain-text file — question text, correct answer, and all four choices —
and refuses to build on any mismatch, on a withdrawn question, or on a malformed
question id.

The service worker's cache name is a **content hash**, so each rebuild
automatically retires the old cache. There is no version number to bump; devices
pick up the new build on next launch.

To preview locally:

```bash
python3 -m http.server 8734 --directory docs
```

---

## Layout

```
docs/                    the published site (generated, do not edit)
  index.html             markup shell, ~8 KB
  app.css                stylesheet
  app.js                 app logic with all three pools baked in
  sw.js                  generated service worker (offline cache)
  manifest.webmanifest   name, icon, standalone display
  icons/                 app icons
  figures/               14 schematic PNGs

build/
  shell.html             editable markup
  app.css                editable stylesheet
  app.js.template        editable app logic (__DATA__ placeholder)
  explanations.json      answer explanations, keyed by question id
  extract.py             parses + validates pools, merges explanations
  build.py               assembles docs/, generates sw.js
  add_expl.py            merges an explanation batch with validation
  mkicon.py              generates the app icons
  pools.json             normalized question data (generated)

pools/                   original question pool files
sources/                 47 CFR Part 97, fetched from the eCFR API
```

---

## Security posture

The app is entirely static and makes no network requests after install. Nothing
is sent anywhere, there is no account, and no analytics.

- **Content-Security-Policy** of `default-src 'none'` with `script-src 'self'`
  and `style-src 'self'`. No `unsafe-inline`, no `unsafe-eval`. All event
  handling is delegated through `data-act` attributes and dynamic styling goes
  through the CSSOM, so no element carries a `style` attribute.
- **All rendered data is escaped**, including question text, answers, ids,
  explanations and anything read back from local storage.
- **Storage is never trusted.** Scores are coerced to numbers, and a saved exam
  is discarded unless every question id still exists in the pool and the answer
  order and selection are in range. That also covers a question pool being
  replaced under an exam saved from the previous pool.
- **Build-time guards.** `build.py` fails if `unsafe-inline`, an `onclick=` or a
  `style="` reappears in the sources. Figure filenames from third-party decks are
  stripped to a basename, allowlisted, and confirmed to resolve inside
  `docs/figures/`.

Two caveats that cannot be fixed in this repo. All GitHub Pages sites under one
account share an origin, so another Pages site of yours could read this app's
local storage. And `frame-ancestors` is ignored in a `<meta>` CSP while Pages
cannot send headers, so the page can be framed. Neither matters much here: there
is no login and nothing sensitive stored.

---

## Notes

- Pool validity: Technician **2026–2030**, General **2023–2027**, Extra
  **2024–2028**. The General pool expires June 30 2027 and Extra June 30 2028.
  Drop the replacement files into `pools/`, adjust the paths in `extract.py`,
  and rebuild. Explanations are keyed by question id, so any that survive the
  new pool carry over and the build reports coverage.
- The FCC reference shown on a card comes from the pool itself. Where a pool
  citation looked wrong, the explanation cites the section that actually governs
  and the pool's own field is left untouched.
