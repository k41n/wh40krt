# Levelling Codex — Warhammer 40,000: Rogue Trader

**[Open the app →](https://k41n.github.io/wh40krt/)** · [Русский](README.md)

An offline, phone-first PWA: pick a character, pick a build, set the level —
the app tells you exactly what to take at that level. No respecs, no wiki
tab-hopping in the middle of a fight.

The interface and all in-game names are **in Russian** (official game
localisation), with the English name kept next to each one so you can cross-check
against the wiki.

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
  The gear icon holds the DLC switches: a disabled DLC hides the builds that
  cannot be assembled without it.
- **Character** → the list of ready builds (Abelard has 8, Heinrix 12, the
  Rogue Trader 64 across archetypes and weapon types).
- **Build** → three tabs:
  - **Уровень** (Level) — a 1–55 slider and the answer: "at level 28 take …".
  - **План 1–55** (Plan) — the whole progression at once, split by tier.
  - **Снаряжение** (Gear) — what to wear, slot by slot.
- Tapping a talent or ability opens its description.

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

Archetype, talent, ability, characteristic and skill names come from the game's
own localisation, matched by UUID (`enGB[uuid] → ruRU[uuid]`): 15,051 of 15,085
picks, 99.8 %. Roughly thirty leftovers are typos and shorthand from the guide
(`MSSP`, `Combat Locust`, free-text remarks) and are shown as-is. Talent
descriptions stay English — they come from the guide's spreadsheet, not from the
game strings.

To rebuild the translation (e.g. after a game patch), copy from the game folder

```
<Steam>/steamapps/common/Warhammer 40,000 Rogue Trader/WH40KRT_Data/StreamingAssets/Localization/
    enGB.json
    ruRU.json
```

and run:

```
python3 tools/apply_ru.py enGB.json ruRU.json
```

## What's inside

| file | what it is |
|---|---|
| `index.html` | the whole app: markup, styles, logic |
| `data.json` | 150 builds across 17 characters + 793 talent/ability descriptions |
| `sw.js` | service worker: offline support, network-first for `index.html` and `data.json` |
| `manifest.webmanifest`, `icon*.png/svg` | PWA plumbing |
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
python3 tools/apply_ru.py enGB.json ruRU.json   # applies the Russian names
```

`build_data.py` expects the spreadsheet tab exports next to it
(`s_<gid>.csv`, downloaded via `gviz/tq?tqx=out:csv&gid=<gid>`).

## Deploying

GitHub Pages serves branch `main` from the repository root. Bump `VERSION` in
`sw.js` before pushing — that's how installed apps notice a new release.

---

An unofficial fan tool. Not affiliated with Owlcat Games or Games Workshop.
