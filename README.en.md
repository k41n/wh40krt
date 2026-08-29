# Levelling Codex — Warhammer 40,000: Rogue Trader

**[Open the app →](https://k41n.github.io/wh40krt/)** · [Русский](README.md)

An offline, phone-first PWA: pick a character, pick a build, set the level —
the app tells you exactly what to take at that level. No respecs, no wiki
tab-hopping in the middle of a fight.

The interface is **entirely in Russian** — names, item names, build titles and
talent descriptions all use the official game localisation — with the English
original kept next to each one in small type so you can cross-check against the
wiki.

## Install on a phone

1. Open **https://k41n.github.io/wh40krt/** in the phone browser.
2. **iOS (Safari):** Share → "Add to Home Screen".
   **Android (Chrome):** "⋮" menu → "Install app".
3. Works offline after the first load — everything is cached.

Updates are automatic: on launch and whenever you return to the app it checks for
a new version, and a bar appears at the bottom — **«Есть новая версия кодекса →
Обновить»** ("new version → update"). Tap it and the app reloads. Ignore it and
the update is applied on the next launch.

## Using it

- **Home** — 12 companions, the Rogue Trader, and the "secret" characters.
  Characters you are already levelling show the chosen build and **what to take
  next** right in the row ("Дальше — ур. 12: …"); tapping jumps straight to that
  level.
  The gear icon holds the DLC switches: a disabled DLC hides the builds that
  cannot be assembled without it.
- **Character** → a **"Как выбрать"** ("how to choose") card at the top explains
  how the builds differ and which one to start with. Below it the builds are
  grouped by their Tier II archetype; each shows a one-line **"how it plays"**
  summary and the guide author's full note, untruncated; each carries a role chip ("universal
  damage", "tank", "extra turns for the party"…) and the recommended one is
  marked "советую начать с него" ("start with this one").
  Abelard has 8 builds, Heinrix 12, the Rogue Trader 64.
- **Build** → three tabs:
  - **Уровень** (Level) — a 1–55 slider and the answer: "at level 28 take …".
  - **План 1–55** (Plan) — the whole progression at once, split by tier.
  - **Снаряжение** (Gear) — what to wear, slot by slot.
- On the **Уровень** tab, the **«Взял — дальше»** button marks the level as taken
  and skips to the next choice. Progress lives in localStorage, per character,
  and can be reset from the same screen.
- Inside a build, a **«Как играется»** ("how it plays") card expands that into
  4–5 sentences: what you do for the first 15 levels, what changes at 16, what
  weapon is in your hands, which ability is the button you press every fight.
- Tapping a talent or ability opens its description — Russian first, English original below.
- Builds affected by patches released after the guide was written are tagged
  **«правка патчем 1.6.1»** and carry a "what changed" card; the full list is in
  the settings sheet under «Актуальность».

## The game's progression model

Level cap 55, three archetype tiers:

| Levels | Tier | What happens |
|---|---|---|
| 1–15 | I | starting archetype: Warrior, Soldier, Operative, Officer, Blade Dancer *(Void Shadows)* |
| 16–35 | II | advanced: Assassin, Vanguard, Arch-Militant, Master Tactician, Grand Strategist, Bounty Hunter, Executioner *(Void Shadows)*, Overseer *(Lex Imperialis)* |
| 36–55 | III | Exemplar — picks up talents and abilities from the two earlier tiers |

Not every Tier I leads to every Tier II; the builds already respect the legal
combinations.

The builds are meant for a 1–55 run **without respeccing**: early levels are
tuned for specific bosses (lvl 15 Aurora, 18–21 the Daemon Smith, 30 Fabricator
Delphim, 40 Yremeryss, 50 Uralon and the Dawn).

## Data and sources

Level-by-level pick lists and gear sets come from Revan619's guide (current as of
patch 1.6):

- [Steam guide "Strongest Companion Builds"](https://steamcommunity.com/sharedfiles/filedetails/?id=3398861511)
- [the builds & items spreadsheet](https://docs.google.com/spreadsheets/d/1rskX4sYcNm6Wqt4rtm8EQqRR4__yrEuxCEzjwoKlHOY/)
- archetype rank structure — [Fextralife wiki](https://roguetrader.wiki.fextralife.com/Archetypes)
  and [roguetrader.wh40k.wiki](https://roguetrader.wh40k.wiki/)

## Russian names

Everything visible in the app is Russian: archetypes, talents, abilities,
characteristics, skills, items, gear slots, build titles and build blurbs.
The English original stays next to it in small type.

The source is the game itself, matched by UUID (`enGB[uuid] → ruRU[uuid]`).

| layer | coverage | source |
|---|---|---|
| pick names | 15,051 / 15,085 (99.8 %) | game localisation |
| talent descriptions | 701 / 793 from the game + 92 written by hand = **793** | game localisation + `tools/ru_manual.json` |
| gear items | 3,028 / 3,216 from the game, the rest by hand | same |
| build titles, blurbs, slots, remarks | 150 titles, 138 blurbs | by hand — this is the guide author's own prose, not game text |

Roughly thirty leftovers are typos and shorthand from the guide (`MSSP`,
`Combat Locust`, free-text remarks such as "Lore Imperium (Chartist Pendant)")
and are shown as-is.

Game markup is stripped from the descriptions (`{g|…}`, `{br}`), and computed
numbers (`{uip|…}`) become "…" — the game fills those in from your stats.

To rebuild the translation (e.g. after a game patch), copy from the game folder

```
<Steam>/steamapps/common/Warhammer 40,000 Rogue Trader/WH40KRT_Data/StreamingAssets/Localization/
    enGB.json
    ruRU.json
```

and run:

```
python3 tools/apply_ru.py enGB.json ruRU.json        # names
python3 tools/apply_ru_desc.py enGB.json ruRU.json   # descriptions and items
python3 tools/apply_ru_manual.py                     # what the game has no text for
```

## What's inside

| file | what it is |
|---|---|
| `index.html` | the whole app: markup, styles, logic |
| `data.json` | 150 builds across 17 characters + 793 talent/ability descriptions |
| `sw.js` | service worker: offline support, network-first for `index.html` and `data.json` |
| `manifest.webmanifest`, `icon*.png/svg` | PWA plumbing |
| `tools/feel.py` | "how it plays": what sets a build apart from its siblings — weapon, ultimate, keystone and talents that are rare for that character, plus the archetype gist |
| `tools/patch_notes.py` | the currency layer: what changed in the game after the guide was compiled |
| `tools/ru_manual.json` | the hand-written layer: build titles and blurbs, slots, rare items, the "how to choose" advice |
| `tools/` | the scripts that generated `data.json` |

## Running locally

Static files, no build step. Any HTTP server will do (service workers don't run
from `file://`):

```
python3 -m http.server 8765
# open http://<your-ip>:8765/ on the phone
```

## Regenerating `data.json`

```
cd tools
python3 build_data.py   # parsed spreadsheet CSVs → data.json
python3 enrich.py       # classifies picks, attaches descriptions
cd ..
python3 tools/apply_ru.py enGB.json ruRU.json        # Russian names from the game
python3 tools/apply_ru_desc.py enGB.json ruRU.json   # Russian descriptions and items from the game
python3 tools/apply_ru_manual.py                     # hand-written layer: builds, slots, advice
python3 tools/feel.py                                # "how it plays" text per build
python3 tools/patch_notes.py                         # post-guide patch notices
```

Order matters: each script fills in what the previous one could not find.

`build_data.py` expects the spreadsheet tab exports next to it
(`s_<gid>.csv`, downloaded via `gviz/tq?tqx=out:csv&gid=<gid>`).

## How current is this?

| what | version |
|---|---|
| build data | Revan619's spreadsheet, "Build cover up to patch 1.6" |
| game it was checked against | 1.6.1.514 (hotfix of 20 July 2026) |
| last check | 29 August 2026 |

As of 29 August 2026 all 19 sheets are byte-identical to the ones `data.json`
was built from — the guide's author has not changed anything since.

The only balance patch after the guide was compiled is **1.6.1.493** of
30 June 2026 (everything later is bug fixes). What it changed is recorded in the
app: Eogunn's Galvanic Field combos nerfed, Wounded Beast and Facing the End
capped, Pasqal's Axial Fortification now only boosts Shock damage, Ogryn Grip
buffed. The psyker-staff melee bug is still unfixed, so the guide's builds that
rely on it still work. 11 builds are tagged in the list.

To re-check: `tools/patch_notes.py` holds the dates, versions and notice texts;
run it last in the pipeline after editing.

## Deploying

GitHub Pages serves branch `main` from the repository root. Bump `VERSION` in
`sw.js` before pushing — that's how installed apps notice a new release.

---

An unofficial fan tool. Not affiliated with Owlcat Games or Games Workshop.
