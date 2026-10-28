# Grace Ledger

A local, read-only progress tracker for an Elden Ring save. A Python exporter reads your Steam save (from a temporary copy; it never writes to `ER0000.sl2`) and writes a snapshot that a single HTML page turns into:

- **Item catalogue:** every item marked present or missing in your inventory and storage, with upgrade levels and Ashes of War.
- **Journey:** Sites of Grace and named bosses found or missing, plus the earliest remaining named enemies by region.
- **Reveal:** the main story, all six endings and every NPC questline as branching trees. Each tree shows its choices, its rewards (with a check on rewards you hold now), and which steps your save flags record. Below that is a sortable NPC status table.
- **Latest changes:** one entry per play session, as sortable tables: bosses, graces, level and stats, items gained and spent, and upgrades.
- **Travel Menu:** merchant stock, what you have bought and a rune budget, sortable per merchant or as one table.
- **Create:** respec suggestions from the weapons you own, with an upgrade-stone budget. A **Melee only** setting, remembered in your browser, keeps the suggestions free of spellcasting.
- Dragons, a tier list and a manual Steam achievement checklist.

Names of characters, places and Sites of Grace throughout the page are dotted links. NPCs with a questline open their storyline; everything else opens an "elden ring …" web search in a new tab. Where the save shows an NPC has moved on, the NPC table and storyline cards give their current location next to where you first met them. A questline whose next location sits behind a story or item gate you have not passed yet (for example the Forge of the Giants before the Fire Giant) is silvered out and marked "Not available yet" with the requirement. One whose location is reachable but whose Site of Grace you have not activated is marked "Not discovered". The gates are listed in `data/storylines.js` under `areas`.

## Requirements

- Windows with the Steam version of Elden Ring, and Python 3.13 or newer (ER Save Manager's minimum).
- **[ER Save Manager](https://github.com/Hapfel1/er-save-manager)** by Hapfel, which does the save parsing. Download it yourself from its own GitHub or Nexus page. Its source-available license forbids redistribution, so this repository includes none of its code, data or icons, and none of the files generated from them.

## Set up

1. Get an ER Save Manager source copy (the folder that contains `src/er_save_manager`).
2. Tell the exporter where it is, in one of three ways:
   - pass `--parser-root <folder>` each time;
   - set the `ER_SAVE_MANAGER_ROOT` environment variable;
   - put the folder path on one line in `tools/.parser-root` (this file is git-ignored).
3. Run `python tools/refresh_inventory.py`. It finds the newest `ER0000.sl2` under `%APPDATA%\EldenRing` and exports its highest-level character. Use `--slot N` for another character, `--save <path>` for a specific save, and `--icons-db <path>` for another icon database.
4. Open `index.html` in a browser. Add `#activity`, `#reveal` or another tab name to the address to open that tab directly.

After each play session, run the exporter again and select **Reload snapshot** on the page.

## What stays on your machine

The exporter writes `data.js`, `data/sessions.js` and `assets/items/`. These hold your save progress, plus item data and icons derived from ER Save Manager and the game, so they are git-ignored. Keep them out of any repository you publish.

The page itself makes one kind of background request. When you open an item's details, it fetches that item's public reference data, keyed by the item name, from `eldenring.fanapis.com`. Google and almanauts.com links open only when you click them. Nothing from your save is uploaded, and the page never signs in to Steam.

## Play sessions

Each export that finds a changed save appends a session to `data/sessions.js`. Re-running the exporter on an unchanged save records nothing. The file keeps one compact summary of the last export plus the changes for each session. Delete it to start the history again. If no on-disk session exists yet, the page falls back to a baseline your browser stored on an earlier visit, labelled "Session (browser)".

## Notes on accuracy

- "Missing" means absent from your inventory and storage now; a consumed item may have been found earlier.
- Quest steps and their recorded, ambiguous or unconfirmed states come from save event flags. Flags record milestones; they cannot show whether an NPC is standing nearby or whether their dialogue is exhausted.
- The main story structure, the six endings and the key questline choices in `data/storylines.js` are written by hand. Their "taken" and "requirement met" marks come from your save flags.

## Not affiliated

Grace Ledger is an unofficial fan tool. It is not affiliated with or endorsed by FromSoftware or Bandai Namco. ELDEN RING is a trademark of its owners.

## License

Grace Ledger's own code is MIT licensed (see `LICENSE`). ER Save Manager, game data and game art are not part of this repository and keep their own terms.
