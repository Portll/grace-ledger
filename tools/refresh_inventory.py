#!/usr/bin/env python3
"""Export a local Elden Ring save snapshot and the matching item icons."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import time
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace


def default_parser_root() -> Path | None:
    """ER Save Manager location from ER_SAVE_MANAGER_ROOT, else the git-ignored tools/.parser-root file."""
    configured = os.environ.get("ER_SAVE_MANAGER_ROOT", "").strip()
    if not configured:
        local = Path(__file__).with_name(".parser-root")
        configured = local.read_text(encoding="utf-8").strip() if local.is_file() else ""
    return Path(configured) if configured else None


DEFAULT_PARSER_ROOT = default_parser_root()
DUNGEON_WORDS = ("cave", "catacomb", "tunnel", "hero's grave", "hero’s grave", "gaol")
# Session history (data/sessions.js): one compact "last" summary per character plus a diff per play session.
HISTORY_FORMAT = 1
ATTRIBUTE_KEYS = ("vigor", "mind", "endurance", "strength", "dexterity", "intelligence", "faith", "arcane")
HISTORY_WORLD_KEYS = ("graces", "locations", "enemies", "maps")
NPC_GRACE_HINTS = {
    "albus": "Village of the Albinaurics", "alexander": "Saintsbridge", "blaidd": "Mistwood Outskirts",
    "blackguard big boggart": "Boilprawn Shack", "boc the seamster": "Coastal Cave", "brother corhyn": "Roundtable Hold",
    "d hunter of the dead": "Roundtable Hold", "d's brother": "Aqueduct-Facing Cliffs", "diallos": "Roundtable Hold",
    "dung eater": "Roundtable Hold", "edgar": "Castle Morne Rampart", "enia": "Roundtable Hold",
    "fia": "Roundtable Hold", "gatekeeper gostoc": "Stormveil Main Gate", "gowry": "Sellia Under-Stair",
    "gurranq beast clergyman": "Bestial Sanctum", "hyetta": "Lake-Facing Cliffs", "iji": "Road to the Manor",
    "irina": "Bridge of Sacrifice", "iron fist alexander": "Saintsbridge", "jar bairn": "Jarburg",
    "jellyfish spirit sister": "Snow Valley Ruins Overlook", "jerren": "Chamber Outside the Plaza", "kale": "Church of Elleh",
    "kenneth haight": "Mistwood Outskirts", "knight bernahl": "Warmaster's Shack", "latenna": "Slumbering Wolf's Shack",
    "millicent": "Aeonia Swamp Shore", "miriel pastor of vows": "Church of Vows", "nepheli loux": "Stormveil Main Gate",
    "patches": "Murkwater Coast", "ranni the witch": "Church of Elleh", "ria zoraya": "Scenic Isle",
    "roderika": "Stormhill Shack", "seluvis": "Ranni's Rise", "sorcerer rogier": "Rampart Tower",
    "sorceress sellen": "Waypoint Ruins Cellar", "tanith": "Volcano Manor", "thops": "Lake-Facing Cliffs",
    "white mask varre": "The First Step", "gideon ofnir": "Roundtable Hold", "master hewg": "Roundtable Hold",
    "moore": "Main Gate Cross", "needle knight leda": "Three-Path Cross", "sir ansbach": "Main Gate Cross",
    "redmane freyja": "Three-Path Cross", "hornsent": "Three-Path Cross", "thiollier": "Pillar Path Cross",
    "drake warrior igon": "Three-Path Cross", "hornsent grandam": "Small Private Altar", "fire knight queelign": "Church District Entrance",
    "dryleaf dane": "Moorth Ruins", "count ymir": "Cathedral of Manus Metyr", "swordhand of night jolan": "Cathedral of Manus Metyr",
    "dragon communion priestess": "Grand Altar of Dragon Communion", "ghost in volcano manor": "Volcano Manor",
    "yura shabriri": "Murkwater Coast", "white mask varre": "The First Step", "miriel": "Church of Vows",
}
QUEST_NPC_ALIASES = {
    "d hunter of the dead": "D, Hunter of the Dead", "enia": "Enia",
    "ensha": "Ensha of the Royal Remains", "gurranq": "Gurranq, Beast Clergyman",
    "kale": "Kalé", "pidia": "Pidia, Carian Servant", "ria": "Rya/Zoraya",
    "rya": "Rya/Zoraya", "white mask varre": "White Mask Varré", "miriel": "Miriel, Pastor of Vows",
}
MERCHANT_NPC_ALIASES = {
    "blackguard": "Blackguard Big Boggart", "count ymir high priest": "Count Ymir",
    "finger reader enia": "Enia", "merchant kale": "Kalé", "preceptor seluvis": "Seluvis",
    "sage gowry": "Gowry", "scribe corhyn": "Brother Corhyn", "smithing master iji": "Iji",
    "sorcerer thops": "Thops", "sword of bernahl": "Knight Bernahl",
}


def normalized_label(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_value.casefold())


WEAPON_TYPES = {
    "AxeLarge": "Greataxe", "AxeNormal": "Axe", "AxhammerLarge": "Colossal weapon",
    "Ballista": "Ballista", "BowLarge": "Greatbow", "BowNormal": "Bow",
    "BowSmall": "Light bow", "Claw": "Claw", "ClossBow": "Crossbow",
    "Dagger": "Dagger", "Flail": "Flail", "HammerLarge": "Great hammer",
    "HammerNormal": "Hammer", "Knuckle": "Fist", "RapierHeavy": "Heavy thrusting sword",
    "SaberLarge": "Curved greatsword", "SaberNormal": "Curved sword",
    "ShieldLarge": "Greatshield", "ShieldNormal": "Medium shield", "ShieldSmall": "Small shield",
    "Sickle": "Reaper", "SpearAxe": "Halberd", "SpearHeavy": "Great spear",
    "SpearNormal": "Spear", "Staff": "Glintstone staff", "SwordDoubleEdge": "Twinblade",
    "SwordGigantic": "Colossal sword", "SwordLarge": "Greatsword", "SwordNormal": "Straight sword",
    "SwordPierce": "Thrusting sword", "katana": "Katana", "Talisman": "Sacred seal",
    "Torch": "Torch", "Whip": "Whip",
}
EQUIPMENT_SLOTS = (
    ("Left hand 1", "left_hand_armament1", "armament"),
    ("Right hand 1", "right_hand_armament1", "armament"),
    ("Left hand 2", "left_hand_armament2", "armament"),
    ("Right hand 2", "right_hand_armament2", "armament"),
    ("Left hand 3", "left_hand_armament3", "armament"),
    ("Right hand 3", "right_hand_armament3", "armament"),
    ("Arrow slot 1", "arrows1", "arrow"),
    ("Bolt slot 1", "bolts1", "bolt"),
    ("Arrow slot 2", "arrows2", "arrow"),
    ("Bolt slot 2", "bolts2", "bolt"),
    ("Head", "head", "head"),
    ("Chest", "chest", "chest"),
    ("Arms", "arms", "arms"),
    ("Legs", "legs", "legs"),
    ("Talisman 1", "talisman1", "talisman"),
    ("Talisman 2", "talisman2", "talisman"),
    ("Talisman 3", "talisman3", "talisman"),
    ("Talisman 4", "talisman4", "talisman"),
)


def stable_snapshot(source: Path, temp_dir: Path) -> tuple[Path, str]:
    """Copy a save only if its size and modification time stay stable."""
    for attempt in range(4):
        before = source.stat()
        snapshot = temp_dir / ("save-copy" + "".join(source.suffixes))
        with source.open("rb") as read_handle, snapshot.open("wb") as write_handle:
            shutil.copyfileobj(read_handle, write_handle, length=1024 * 1024)
            write_handle.flush()
            os.fsync(write_handle.fileno())
        after = source.stat()
        copied_size = snapshot.stat().st_size
        if (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns) and copied_size == after.st_size:
            return snapshot, f"{after.st_size}-{after.st_mtime_ns}"
        snapshot.unlink(missing_ok=True)
        time.sleep(0.25 * (attempt + 1))
    raise RuntimeError("The save kept changing while it was copied. Try again after Steam finishes writing it.")


def latest_save(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Save not found: {path}")
        return path
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("Set APPDATA or pass --save with the path to ER0000.sl2.")
    saves = list((Path(appdata) / "EldenRing").glob("*/ER0000.sl2"))
    if not saves:
        raise FileNotFoundError("No Steam save found under %APPDATA%/EldenRing. Pass --save.")
    return max(saves, key=lambda path: path.stat().st_mtime_ns)


def icon_database(path: Path):
    """Yield icon filename, blob id and bytes from supported local DB layouts."""
    connection = sqlite3.connect("file:" + path.as_posix() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    try:
        if {"icon_keys", "blobs"}.issubset(tables):
            for row in connection.execute(
                "SELECT icon_keys.name, blobs.id, blobs.data FROM icon_keys "
                "JOIN blobs ON blobs.id = icon_keys.blob_id"
            ):
                yield row["name"], int(row["id"]), row["data"]
        elif "icons" in tables:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(icons)")}
            name_column = "name" if "name" in columns else "filename"
            blob_column = next((name for name in ("data", "blob", "image") if name in columns), None)
            if not blob_column:
                raise RuntimeError("The icons table has no image blob column.")
            for row in connection.execute(f'SELECT "{name_column}", "{blob_column}" FROM icons'):
                image_name, image_data = row[0], row[1]
                stable_id = int.from_bytes(hashlib.sha256(image_name.encode("utf-8")).digest()[:4], "little")
                yield image_name, stable_id, image_data
        else:
            raise RuntimeError("Unrecognized icons.db schema; expected icon_keys/blobs or icons.")
    finally:
        connection.close()


def icon_normalizer(parser_root: Path):
    """Reuse the parser's own item-name matching rules without its DB loader."""
    sys.path.insert(0, str(parser_root / "src"))
    from er_save_manager.data import icon_manager
    from er_save_manager.data.icon_manager import _norm_icon

    def build_available(rows):
        available = {}
        by_filename = {}
        for filename, blob_id, blob in rows:
            stem = filename[:-5] if filename.lower().endswith(".webp") else filename
            if stem.startswith("ICON "):
                stem = stem[5:]
            key = _norm_icon(stem)
            available.setdefault(key, filename)
            by_filename[filename] = (filename, blob_id, blob)
        icon_manager._available = available
        icon_manager._db = object()
        return available, by_filename, icon_manager._lookup

    return build_available


def decode_inventory_row(row, gaitems, item_db, get_item_name, is_convergence):
    handle = int(row.gaitem_handle)
    gaitem = gaitems.get(handle)
    ash_name = None
    ash_id = None
    upgrade = 0
    if gaitem:
        raw_id = int(gaitem.item_id)
        if (int(gaitem.gaitem_handle) & 0xF0000000) == 0x80000000:
            full_id = (raw_id // 100) * 100
            upgrade = raw_id % 100
        else:
            full_id = raw_id
        gem_handle = getattr(gaitem, "gem_gaitem_handle", None)
        if gem_handle not in (None, 0, -1):
            gem = gaitems.get(int(gem_handle) & 0xFFFFFFFF)
            if gem:
                ash_id = int(gem.item_id)
                ash_name = get_item_name(0x80000000 | (ash_id & 0x0FFFFFFF), 0, is_convergence)
    elif (handle & 0xF0000000) == 0xA0000000:
        full_id = 0x20000000 | (handle & 0x00FFFFFF)
    elif (handle & 0xF0000000) == 0xB0000000:
        full_id = 0x40000000 | (handle & 0x00FFFFFF)
    else:
        full_id = handle

    name = get_item_name(full_id, upgrade, is_convergence)
    item = item_db.get_item_by_id(full_id, is_convergence)
    if item is None and name and not name.startswith("Unknown"):
        suffix = re.match(r"^(.*?)\s*\+\s*(\d+)$", name)
        base_name = suffix.group(1).strip() if suffix else name
        candidates = [
            candidate for candidate in item_db.search_items(base_name)
            if candidate.name.casefold() == base_name.casefold()
            and item_db.get_item_by_id(candidate.full_id, is_convergence) is candidate
        ]
        category_bits = full_id & 0xF0000000
        category_matches = [candidate for candidate in candidates if candidate.full_id & 0xF0000000 == category_bits]
        item = (category_matches or candidates or [None])[0]
        if item is not None:
            full_id = item.full_id
            if suffix:
                upgrade = int(suffix.group(2))
            if item.category_name in ("Melee Weapons", "Ranged Weapons", "DLC Melee Weapons", "DLC Ranged Weapons", "Tarnished Pack Weapons"):
                name = item.name + (f" +{upgrade}" if upgrade else "")
    if name.startswith("Unknown") and (full_id & 0xF0000000) == 0x40000000:
        talisman_id = 0x20000000 | (full_id & 0x0FFFFFFF)
        alt = item_db.get_item_by_id(talisman_id, is_convergence)
        if alt:
            full_id, name = talisman_id, alt.name
    if not name or name.startswith("Unknown") or name == "(empty)":
        return None
    item = item_db.get_item_by_id(full_id, is_convergence) or item
    return {
        "id": f"{full_id:08x}:{upgrade}:{ash_id if ash_id is not None else ''}",
        "catalogId": f"{full_id:08x}",
        "name": name,
        "category": item.category_name if item else "Other",
        "weaponType": WEAPON_TYPES.get(getattr(item, "wep_type_col", ""), getattr(item, "wep_type_col", "")) if item else "",
        "reinforcement": getattr(item, "reinforcement", "") if item and item.category_name in ("Melee Weapons", "Ranged Weapons", "Weapons", "Shields", "Spell Tools", "DLC Melee Weapons", "DLC Ranged Weapons", "DLC Shields", "DLC Spell Tools", "Tarnished Pack Weapons") else "",
        "upgrade": upgrade or None,
        "ashOfWar": ash_name,
        "quantity": int(row.quantity),
        "rawItemId": full_id,
    }


def read_js_payload(path: Path, variable: str):
    """Return the JSON assigned by a generated `window.<variable> = ...;` file, or None."""
    prefix = f"window.{variable} = "
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text[len(prefix):].rstrip().rstrip(";")) if text.startswith(prefix) else None
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def write_js_payload(path: Path, variable: str, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(f"window.{variable} = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    os.replace(temporary, path)


def profile_key(export: dict) -> str:
    """History is kept per character: "<slot>:<name>", matching the page's lookup."""
    return f"{(export.get('source') or {}).get('slot')}:{(export.get('character') or {}).get('name')}"


def is_upgradeable(item: dict) -> bool:
    return bool(item.get("upgrade")) or item.get("reinforcement") in ("standard", "somber") or item.get("category") in ("Ashes", "DLC Ashes")


def snapshot_summary(export: dict) -> dict:
    """Reduce an export to what the session diff compares: catalogId -> [quantity, upgrade levels], stats, world flags."""
    levels = defaultdict(list)
    for item in export.get("items") or []:
        if is_upgradeable(item):
            levels[item["catalogId"]].extend([int(item.get("upgrade") or 0)] * int(item.get("quantity") or 0))
    quantities = defaultdict(int)
    for item in export.get("catalog") or export.get("items") or []:
        quantities[item["catalogId"]] += int(item.get("quantity") or 0)
    character, world = export.get("character") or {}, export.get("world") or {}
    attributes = character.get("attributes") or {}
    return {
        "format": HISTORY_FORMAT,
        "generatedAt": export.get("generatedAt"),
        "generation": export.get("generation"),
        "level": character.get("level"),
        "attributes": {key: attributes[key] for key in ATTRIBUTE_KEYS if key in attributes},
        "runes": character.get("runes"),
        "items": {
            catalog_id: [quantity, sorted(levels[catalog_id])] if levels.get(catalog_id) else [quantity]
            for catalog_id, quantity in sorted(quantities.items()) if quantity > 0
        },
        "world": {key: list(world.get(key) or []) for key in HISTORY_WORLD_KEYS},
    }


def multiset_minus(left, right) -> list:
    return sorted((Counter(left) - Counter(right)).elements())


def summary_changes(old: dict, new: dict, catalog: list) -> dict:
    """What changed between two summaries. index.html's browser fallback (diffSummaries) mirrors this shape."""
    changes = {}
    if None not in (old.get("level"), new.get("level")) and old["level"] != new["level"]:
        changes["level"] = [old["level"], new["level"]]
    old_attributes, new_attributes = old.get("attributes") or {}, new.get("attributes") or {}
    attributes = {
        key: [old_attributes[key], new_attributes[key]]
        for key in ATTRIBUTE_KEYS
        if key in old_attributes and key in new_attributes and old_attributes[key] != new_attributes[key]
    }
    if attributes:
        changes["attributes"] = attributes
    if None not in (old.get("runes"), new.get("runes")) and old["runes"] != new["runes"]:
        changes["runes"] = [old["runes"], new["runes"]]
    by_id = {row["catalogId"]: row for row in catalog}
    old_items, new_items = old.get("items") or {}, new.get("items") or {}
    gained, spent, upgrades = [], [], []
    for catalog_id in set(old_items) | set(new_items):
        before, after = old_items.get(catalog_id, [0]), new_items.get(catalog_id, [0])
        row = by_id.get(catalog_id, {})
        entry = {"id": catalog_id, "name": row.get("name") or f"Item {catalog_id}", "category": row.get("category") or "Other"}
        if after[0] != before[0]:
            (gained if after[0] > before[0] else spent).append({**entry, "from": before[0], "to": after[0]})
        if len(before) > 1 and len(after) > 1:
            lost, added = multiset_minus(before[1], after[1]), multiset_minus(after[1], before[1])
            if lost and added:
                upgrades.append({**entry, "from": lost, "to": added})
    for key, rows in (("gained", gained), ("spent", spent), ("upgrades", upgrades)):
        if rows:
            changes[key] = sorted(rows, key=lambda entry: (entry["category"].casefold(), entry["name"].casefold()))
    old_world, new_world = old.get("world") or {}, new.get("world") or {}
    for key in HISTORY_WORLD_KEYS:
        if not isinstance(old_world.get(key), list):
            continue
        seen = set(old_world[key])
        added = [name for name in new_world.get(key) or [] if name not in seen]
        if added:
            changes[key] = added
    return changes


def change_count(changes: dict) -> int:
    return sum(1 if key in ("level", "runes") else len(value) for key, value in changes.items())


def record_session(history: dict, export: dict, previous_export: dict | None = None) -> str:
    """Append a play session when the save generation changed since this character's last export.

    Returns "session", "baseline" (first export for this character) or "unchanged" (nothing recorded).
    `previous_export` is the data.js being replaced; it seeds a character's first comparison.
    """
    key = profile_key(export)
    profiles = history.setdefault("profiles", {})
    current = snapshot_summary(export)
    profile = profiles.get(key)
    previous = profile.get("last") if profile else None
    if previous and previous.get("generation") == current["generation"]:
        return "unchanged"
    if profile is None:
        profile = profiles[key] = {"character": export["character"]["name"], "slot": export["source"]["slot"], "last": None, "sessions": []}
        if previous_export and profile_key(previous_export) == key:
            previous = snapshot_summary(previous_export)
    outcome = "baseline"
    if previous and previous.get("generation") != current["generation"]:
        sessions = profile.setdefault("sessions", [])
        sessions.insert(0, {
            "session": sessions[0]["session"] + 1 if sessions else 1,
            "from": {"generatedAt": previous.get("generatedAt"), "generation": previous.get("generation")},
            "to": {"generatedAt": current["generatedAt"], "generation": current["generation"]},
            "changes": summary_changes(previous, current, export.get("catalog") or []),
        })
        outcome = "session"
    profile["last"] = current
    history["updatedAt"] = current["generatedAt"]
    return outcome


def main() -> int:
    here = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", help="Steam save path (default: newest ER0000.sl2 in AppData).")
    parser.add_argument("--slot", type=int, help="Character slot index (default: highest-level active slot).")
    parser.add_argument("--parser-root", type=Path, default=DEFAULT_PARSER_ROOT, help="ER Save Manager source/install folder.")
    parser.add_argument("--icons-db", type=Path, help="Path to the local item icons database.")
    args = parser.parse_args()

    save_path = latest_save(args.save)
    if args.parser_root is None:
        raise SystemExit("ER Save Manager not configured. Pass --parser-root, set ER_SAVE_MANAGER_ROOT, or put its folder path in tools/.parser-root.")
    parser_root = args.parser_root.expanduser().resolve()
    icons_path = (args.icons_db.expanduser().resolve() if args.icons_db else parser_root / "src" / "er_save_manager" / "data" / "icons.db")
    if not (parser_root / "src" / "er_save_manager").is_dir():
        raise FileNotFoundError(f"Parser package not found under {parser_root}. Pass --parser-root.")
    if not icons_path.is_file():
        raise FileNotFoundError(f"Item icon database not found: {icons_path}. Pass --icons-db.")

    sys.path.insert(0, str(parser_root / "src"))
    from er_save_manager.data.event_flags_db import get_category_flags, get_flag_info
    from er_save_manager.data.grace_data import get_graces, grace_from_last_rested
    from er_save_manager.data.item_database import get_item_database, get_item_name
    from er_save_manager.data.npc_data import NPC_DEFEAT_FLAGS, NPC_FLAGS, NPC_VANISH_FLAGS
    from er_save_manager.data.quest_flags_db import QUEST_FLAGS
    from er_save_manager.data.shop_stock import bought as shop_bought, get_stock
    from er_save_manager.data.starting_classes import get_class_data
    from er_save_manager.parser.event_flags import EventFlags
    from er_save_manager.parser.save import Save

    with tempfile.TemporaryDirectory(prefix="grace-ledger-") as temporary:
        safe_copy, generation = stable_snapshot(save_path, Path(temporary))
        save = Save.from_file(str(safe_copy))
        active_slots = save.get_active_slots()
        if not active_slots:
            raise RuntimeError("The selected save has no active character slots.")
        if args.slot is not None:
            if args.slot not in active_slots:
                raise RuntimeError(f"Character slot {args.slot} is not active in the selected save.")
            slot_index = args.slot
        else:
            slot_index = max(active_slots, key=lambda i: save.character_slots[i].get_level())
        slot = save.character_slots[slot_index]
        player = slot.player_game_data
        item_db = get_item_database()
        is_convergence = bool(save.is_convergence)
        class_info = get_class_data(player.archetype, is_convergence)
        armor_slot_path = parser_root / "src" / "er_save_manager" / "data" / "items" / "armor_slot_types.csv"
        armor_slots = {}
        if armor_slot_path.is_file():
            with armor_slot_path.open("r", encoding="utf-8-sig", newline="") as armor_file:
                armor_slots = {
                    int(row["ID"]): row["Slot"].strip().lower()
                    for row in csv.DictReader(armor_file)
                    if row.get("ID") and row.get("Slot")
                }

        gaitems = {int(g.gaitem_handle): g for g in slot.gaitem_map if int(g.gaitem_handle)}
        grouped = {}
        for inventory in (slot.inventory_held, slot.inventory_storage_box):
            for section in (inventory.common_items, inventory.key_items):
                for row in section:
                    if not row.gaitem_handle or not row.quantity:
                        continue
                    item = decode_inventory_row(row, gaitems, item_db, get_item_name, is_convergence)
                    if not item:
                        continue
                    key = item["id"]
                    if key not in grouped:
                        grouped[key] = item
                    else:
                        grouped[key]["quantity"] += item["quantity"]

        owned_counts = {}
        upgrade_levels = {}
        attached_skills = {}
        for item in grouped.values():
            catalog_id = item["catalogId"]
            owned_counts[catalog_id] = owned_counts.get(catalog_id, 0) + item["quantity"]
            if item.get("upgrade"):
                upgrade_levels.setdefault(catalog_id, set()).add(int(item["upgrade"]))
            if item.get("ashOfWar"):
                attached_skills.setdefault(catalog_id, set()).add(item["ashOfWar"])

        catalog = {}
        for item in item_db.items:
            category = item.category_name
            if not item.name or str(item.name).strip().casefold() in ("none", "(empty)"):
                continue
            if category.startswith("Convergence") or category == "Seamless Co-op Items":
                continue
            if item_db.get_item_by_id(item.full_id, is_convergence) is not item:
                continue
            catalog_id = f"{item.full_id:08x}"
            if catalog_id in catalog:
                continue
            catalog[catalog_id] = {
                "id": catalog_id,
                "catalogId": catalog_id,
                "rawItemId": item.full_id,
                "name": item.name,
                "category": category,
                "weaponType": WEAPON_TYPES.get(item.wep_type_col, item.wep_type_col),
                "armorSlot": armor_slots.get(item.id, "") if "Armor" in category else "",
                "reinforcement": item.reinforcement if category in ("Melee Weapons", "Ranged Weapons", "Weapons", "Shields", "Spell Tools", "DLC Melee Weapons", "DLC Ranged Weapons", "DLC Shields", "DLC Spell Tools", "Tarnished Pack Weapons") else "",
                "quantity": 0,
                "found": False,
                "upgradeLevels": [],
                "ashOfWar": "",
            }
        for catalog_id, owned_item in ((item["catalogId"], item) for item in grouped.values()):
            catalog_item = catalog.get(catalog_id)
            if catalog_item is None:
                catalog_item = dict(owned_item)
                catalog_item.update({"id": catalog_id, "catalogId": catalog_id, "found": False, "upgradeLevels": []})
                catalog[catalog_id] = catalog_item
        for catalog_id, item in catalog.items():
            item["quantity"] = owned_counts.get(catalog_id, 0)
            item["found"] = item["quantity"] > 0
            item["upgradeLevels"] = sorted(upgrade_levels.get(catalog_id, set()))
            item["ashOfWar"] = ", ".join(sorted(attached_skills.get(catalog_id, set()), key=str.lower))

        equipment = []
        for label, field, kind in EQUIPMENT_SLOTS:
            handle = int(getattr(slot.equipped_items_gaitem_handle, field, 0)) & 0xFFFFFFFF
            equipped_item = None
            if handle not in (0, 0xFFFFFFFF):
                equipped_item = decode_inventory_row(
                    SimpleNamespace(gaitem_handle=handle, quantity=1),
                    gaitems,
                    item_db,
                    get_item_name,
                    is_convergence,
                )
                if (
                    equipped_item is None
                    and kind == "armament"
                    and int(getattr(slot.equipped_items_item_id, field, 0)) == 110000
                ):
                    equipped_item = {
                        "id": "unarmed",
                        "catalogId": "unarmed",
                        "name": "Unarmed",
                        "category": "Melee Weapons",
                        "weaponType": "Fist",
                        "reinforcement": "",
                        "upgrade": None,
                        "ashOfWar": "",
                        "quantity": 1,
                    }
            equipment.append({
                "name": label,
                "kind": kind,
                "armorSlot": kind if kind in ("head", "chest", "arms", "legs") else "",
                "item": equipped_item,
            })

        build_available = icon_normalizer(parser_root)
        available, icons_by_name, lookup_icon = build_available(icon_database(icons_path))
        used_icons = {}
        equipped_items = [entry["item"] for entry in equipment if entry["item"]]
        for item in list(catalog.values()) + list(grouped.values()) + equipped_items:
            lookup_name = item["name"]
            if lookup_name.startswith("Map: "):
                lookup_name = lookup_name.replace("- ", ", ")
            icon_name = lookup_icon(lookup_name, item["category"])
            match = icons_by_name.get(icon_name) if icon_name else None
            if match:
                filename, blob_id, blob = match
                asset_name = f"item_{blob_id}.webp"
                item["icon"] = "./assets/items/" + asset_name
                used_icons[asset_name] = blob

        assets = here / "assets" / "items"
        assets.mkdir(parents=True, exist_ok=True)
        expected = set(used_icons)
        for old_asset in assets.glob("item_*.webp"):
            if old_asset.name not in expected:
                old_asset.unlink()
        for asset_name, blob in used_icons.items():
            (assets / asset_name).write_bytes(blob)

        grace_catalog = []
        for grace in get_graces(include_convergence=is_convergence):
            try:
                unlocked = EventFlags.get_flag(slot.event_flags, grace.flag_id)
            except (ValueError, IndexError):
                unlocked = False
            grace_catalog.append({"name": grace.name, "region": grace.region, "label": f"{grace.name} ({grace.region})", "isDlc": grace.is_dlc, "found": unlocked})
        grace_catalog.sort(key=lambda entry: (entry["isDlc"], entry["region"].lower(), entry["name"].lower()))
        grace_details = [entry for entry in grace_catalog if entry["found"]]
        grace_by_flag = {grace.flag_id: {"name": grace.name, "region": grace.region, "label": f"{grace.name} ({grace.region})", "isDlc": grace.is_dlc} for grace in get_graces(include_convergence=is_convergence)}
        grace_by_name = {normalized_label(grace["name"]): grace for grace in grace_catalog}
        grace_hint_by_npc = {normalized_label(name): normalized_label(grace) for name, grace in NPC_GRACE_HINTS.items()}

        def nearest_grace(location: str | None, npc_name: str = ""):
            location_key = normalized_label(location or "")
            if location_key:
                exact = grace_by_name.get(location_key)
                if exact:
                    return {key: exact[key] for key in ("name", "region", "label", "isDlc")}
                matches = [grace for key, grace in grace_by_name.items() if len(key) >= 5 and (key in location_key or location_key in key)]
                if matches:
                    match = max(matches, key=lambda grace: len(normalized_label(grace["name"])))
                    return {key: match[key] for key in ("name", "region", "label", "isDlc")}
                region_matches = [grace for grace in grace_catalog if normalized_label(grace["region"]) == location_key]
                if region_matches:
                    match = region_matches[0]
                    return {key: match[key] for key in ("name", "region", "label", "isDlc")}
            hint_key = grace_hint_by_npc.get(normalized_label(npc_name))
            hinted = grace_by_name.get(hint_key or "")
            if hinted is None and hint_key:
                hinted = next((grace for grace in grace_catalog if normalized_label(grace["region"]) == hint_key), None)
            if hinted:
                return {key: hinted[key] for key in ("name", "region", "label", "isDlc")}
            return None

        def read_event_flag(flag_id: int):
            try:
                return EventFlags.get_flag(slot.event_flags, int(flag_id)) if EventFlags.has_flag(int(flag_id)) else None
            except (ValueError, IndexError, TypeError):
                return None

        npc_state_by_key = {}
        npc_catalog = []
        dlc_npc_keys = {normalized_label(name) for name in ("Needle Knight Leda", "Sir Ansbach", "Redmane Freyja", "Hornsent", "Moore", "Thiollier", "Drake Warrior Igon", "Hornsent Grandam", "Fire Knight Queelign", "Dryleaf Dane", "Count Ymir", "Swordhand of Night Jolán", "Dragon Communion Priestess")}
        all_npcs = dict(NPC_FLAGS)
        all_npcs.update(NPC_DEFEAT_FLAGS)
        for npc_name, (base_flag, location) in all_npcs.items():
            if npc_name in NPC_DEFEAT_FLAGS:
                dead_value = read_event_flag(base_flag)
                state = {"alive": None if dead_value is None else not dead_value, "hostile": False, "dead": dead_value, "vanished": False}
            else:
                alive, aggro_a, aggro_b, dead = (read_event_flag(base_flag + offset) for offset in range(4))
                vanished_values = [read_event_flag(flag_id) for flag_id in NPC_VANISH_FLAGS.get(npc_name, ())]
                state = {"alive": alive, "hostile": None if aggro_a is None or aggro_b is None else aggro_a or aggro_b, "dead": dead, "vanished": any(value is True for value in vanished_values)}
            if state["dead"] is True:
                status = "Dead flag set"
            elif state["hostile"] is True:
                status = "Hostile flag set"
            elif state["alive"] is True:
                status = "Alive flag set"
            else:
                status = "Not confirmed by save flags"
            record = {"name": npc_name, "location": location, "nearestGrace": nearest_grace(location, npc_name), "status": status, **state, "isDlc": normalized_label(npc_name) in dlc_npc_keys}
            npc_catalog.append(record)
            npc_state_by_key[normalized_label(npc_name)] = record

        quest_aliases = {normalized_label(key): value for key, value in QUEST_NPC_ALIASES.items()}
        quest_catalog = []
        for npc_name, steps in QUEST_FLAGS.items():
            alias = quest_aliases.get(normalized_label(npc_name), npc_name)
            state = npc_state_by_key.get(normalized_label(alias))
            step_records = []
            latest_recorded = -1
            for index, step in enumerate(steps):
                conditions = step.get("flags", [])
                values = [read_event_flag(condition["id"]) for condition in conditions]
                supported = bool(conditions) and all(value is not None for value in values)
                matches = supported and all(value == bool(condition["value"]) for value, condition in zip(values, conditions))
                has_positive_marker = any(bool(condition["value"]) for condition in conditions)
                step_state = "recorded" if matches and has_positive_marker else "ambiguous" if matches else "not-confirmed"
                if step_state == "recorded":
                    latest_recorded = index
                step_records.append({"index": index, "description": step.get("description", "Quest step"), "location": step.get("location"), "nearestGrace": nearest_grace(step.get("location"), alias), "state": step_state})
            next_index = min(latest_recorded + 1, len(step_records) - 1) if step_records else -1
            next_step = step_records[next_index] if next_index >= 0 else None
            latest_location = next((step.get("location") for step in reversed(step_records[:latest_recorded + 1]) if step.get("location")), None)
            display_location = (next_step or {}).get("location") or latest_location or (state or {}).get("location")
            closest = nearest_grace((next_step or {}).get("location"), alias) or nearest_grace(latest_location, alias) or (state or {}).get("nearestGrace")
            quest_catalog.append({"name": npc_name, "npcName": alias, "location": display_location, "nearestGrace": closest, "npcStatus": (state or {}).get("status", "No separate NPC life flag"), "isDlc": bool((state or {}).get("isDlc", False)), "latestRecordedStep": latest_recorded, "nextStep": next_step, "steps": step_records})
        quest_catalog.sort(key=lambda row: (row["isDlc"], row["name"].casefold()))

        merchant_aliases = {normalized_label(key): normalized_label(value) for key, value in MERCHANT_NPC_ALIASES.items()}
        shop_stock = []
        for row in get_stock(is_convergence):
            try:
                purchased = min(row.quantity, shop_bought(row, lambda flag_id: read_event_flag(flag_id) is True))
            except (ValueError, IndexError, TypeError):
                purchased = 0
            grace = grace_by_flag.get(row.grace_flag)
            merchant_key = merchant_aliases.get(normalized_label(row.merchant), normalized_label(row.merchant))
            merchant_state = npc_state_by_key.get(merchant_key)
            shop_stock.append({"id": row.row_id, "merchant": row.merchant, "item": row.item_name, "price": row.price, "quantity": row.quantity, "purchased": purchased, "remaining": max(0, row.quantity - purchased), "nearestGrace": grace, "merchantStatus": (merchant_state or {}).get("status", "NPC status not tracked"), "isDlc": row.is_dlc})
        shop_stock.sort(key=lambda row: (row["isDlc"], row["merchant"].casefold(), row["item"].casefold()))

        last_rested_value = int(getattr(slot, "last_rested_grace", 0) or 0)
        last_rested = grace_from_last_rested(last_rested_value, is_convergence) if last_rested_value else None
        boss_records = {}
        for flag_id in get_category_flags("Bosses"):
            info = get_flag_info(flag_id)
            if not info:
                continue
            flag_name = info["name"]
            region = ""
            if flag_name.startswith("Defeated "):
                boss_name = flag_name[len("Defeated "):]
            elif flag_name.startswith("[") and "|" in flag_name and "Defeated" in flag_name:
                boss_name = flag_name.split("]", 1)[1].split("|", 1)[0].strip()
                region = flag_name[1:].split("]", 1)[0].strip()
            elif "Boss Defeated:" in flag_name:
                boss_name = flag_name.split("Boss Defeated:", 1)[1].strip()
            else:
                continue
            if not boss_name:
                continue
            try:
                if not EventFlags.has_flag(flag_id):
                    continue
                found = EventFlags.get_flag(slot.event_flags, flag_id)
                key = boss_name.casefold()
                boss_records.setdefault(key, {"name": boss_name, "entries": {}})
                entry_key = region.casefold()
                previous_entry = boss_records[key]["entries"].get(entry_key, {"region": region, "found": False})
                boss_records[key]["entries"][entry_key] = {"region": previous_entry["region"], "found": previous_entry["found"] or found}
            except (ValueError, IndexError):
                continue
        boss_catalog = []
        for record in boss_records.values():
            entries = record["entries"]
            regions = [region for region, entry in entries.items() if entry["region"]]
            if regions:
                for region in regions:
                    region_name = entries[region]["region"]
                    label = record["name"] + (" · " + region_name if len(regions) > 1 else "")
                    found = entries[region]["found"] or (len(regions) == 1 and entries.get("", {}).get("found", False))
                    boss_catalog.append({"name": label, "found": found, "region": region_name})
            else:
                boss_catalog.append({"name": record["name"], "found": entries.get("", {}).get("found", False)})
        boss_catalog.sort(key=lambda entry: entry["name"].casefold())
        enemies = [entry["name"] for entry in boss_catalog if entry["found"]]
        dungeon_catalog = [entry for entry in grace_catalog if any(word in entry["name"].lower() for word in DUNGEON_WORDS)]
        dungeons = [entry["name"] for entry in dungeon_catalog if entry["found"]]
        ashes = sorted(
            {item["name"] for item in grouped.values() if item["category"].endswith("Gems")},
            key=str.lower,
        )
        map_catalog = []
        excluded_map_labels = {"center", "sw", "nw", "se", "ne", "n", "show underground", "show shadow realm map"}
        for flag_id in get_category_flags("Maps"):
            info = get_flag_info(flag_id)
            if not info:
                continue
            map_name = info["name"].split("|", 1)[0].strip()
            if map_name.casefold() in excluded_map_labels:
                continue
            if map_name == "Altus Plateur":
                map_name = "Altus Plateau"
            try:
                if EventFlags.has_flag(flag_id):
                    map_catalog.append({"name": map_name, "found": EventFlags.get_flag(slot.event_flags, flag_id)})
            except (ValueError, IndexError):
                continue
        map_catalog.sort(key=lambda entry: entry["name"].casefold())
        map_catalog = list({entry["name"].casefold(): entry for entry in map_catalog}.values())
        map_catalog.sort(key=lambda entry: entry["name"].casefold())
        character = {
            "name": slot.get_character_name(),
            "className": class_info.get("name", "Character"),
            "level": slot.get_level(),
            "startingLevel": int(class_info.get("level", 1)),
            "startingAttributes": {
                key: int(class_info[key])
                for key in ("vigor", "mind", "endurance", "strength", "dexterity", "intelligence", "faith", "arcane")
            },
            "attributes": {
                key: int(getattr(player, key))
                for key in ("vigor", "mind", "endurance", "strength", "dexterity", "intelligence", "faith", "arcane")
            },
            "runes": int(getattr(player, "runes", 0)),
            "equipment": equipment,
        }
        data = {
            "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "generation": generation,
            "character": character,
            "world": {
                "graces": [entry["name"] for entry in grace_details],
                "graceDetails": grace_details,
                "graceCatalog": grace_catalog,
                "locations": dungeons,
                "dungeonCatalog": dungeon_catalog,
                "enemies": enemies,
                "bossCatalog": boss_catalog,
                "ashes": ashes,
                "ashCatalog": [item for item in sorted(catalog.values(), key=lambda row: row["name"].lower()) if item["category"].endswith("Gems")],
                "maps": [entry["name"] for entry in map_catalog if entry["found"]],
                "mapCatalog": map_catalog,
                "questCatalog": quest_catalog,
                "npcCatalog": npc_catalog,
                "shopStock": shop_stock,
                "lastRestedGrace": ({"name": last_rested.name, "region": last_rested.region, "label": f"{last_rested.name} ({last_rested.region})", "isDlc": last_rested.is_dlc} if last_rested else None),
            },
            "items": sorted(grouped.values(), key=lambda item: (item["category"].lower(), item["name"].lower(), item["id"])),
            "catalog": sorted(catalog.values(), key=lambda item: (item["category"].lower(), item["name"].lower(), item["id"])),
            "source": {"saveName": save_path.name, "slot": slot_index, "readOnly": True},
        }
        output = here / "data.js"
        history_path = here / "data" / "sessions.js"
        history = read_js_payload(history_path, "ER_LEDGER_SESSIONS")
        if history_path.exists() and not (isinstance(history, dict) and history.get("format") == HISTORY_FORMAT):
            aside = history_path.with_name(f"sessions.unreadable-{datetime.now():%Y%m%d-%H%M%S}.js")
            history_path.replace(aside)
            print(f"Warning: {history_path.name} was unreadable or an unsupported format; moved it to {aside.name} and started a new history.")
            history = None
        if not isinstance(history, dict):
            history = {"format": HISTORY_FORMAT, "profiles": {}}
        # Read the export being replaced before overwriting it: it seeds a character's first session.
        previous_export = None if profile_key(data) in history["profiles"] else read_js_payload(output, "ER_LEDGER_DATA")
        history_outcome = record_session(history, data, previous_export)
        output.write_text("window.ER_LEDGER_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
        if history_outcome != "unchanged":
            write_js_payload(history_path, "ER_LEDGER_SESSIONS", history)

    found_catalog = sum(1 for item in data["catalog"] if item["found"])
    print(f"Exported {found_catalog}/{len(data['catalog'])} catalog items found, {len(used_icons)} item icons, "
          f"{len(grace_details)} Sites of Grace and {len(enemies)} named foes.")
    print(f"Character: {character['name']} · level {character['level']} · save: {save_path}")
    print(f"Wrote {output}")
    profile = history["profiles"][profile_key(data)]
    if history_outcome == "session":
        latest = profile["sessions"][0]
        print(f"History: recorded session {latest['session']} ({change_count(latest['changes'])} changes) in {history_path}")
    elif history_outcome == "baseline":
        print(f"History: baseline recorded in {history_path}; the next export after playing records a session.")
    else:
        print("History: save unchanged since the last export; no new session recorded.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        raise SystemExit(f"Error: {error}")
