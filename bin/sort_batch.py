#!/usr/bin/env python3
"""Move saved reels into Instagram collections from a map file.

Usage:
    python3 bin/sort_batch.py --batch <label> --map <label>_map.json

Map file: JSON object {media_id: theme_key}, where theme_key is one of the
keys defined during setup (see ~/.instagram-saved-reels-sort/config.json).

Media IDs absent from the map are left in Saved (unsorted).
"""
import argparse
import json
import os
import subprocess
import sys

CONFIG_DIR = os.path.expanduser("~/.instagram-saved-reels-sort")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        sys.exit(f"No config at {CONFIG_FILE}. Run: python3 bin/setup.py")
    cfg = json.load(open(CONFIG_FILE))
    colls = cfg.get("collections", {})
    if not colls:
        sys.exit("No collections in config. Re-run: python3 bin/setup.py")
    return cfg["account_id"], colls


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("CMD FAILED:", " ".join(args[:4]))
        print((r.stderr or "")[-1500:])
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--map", required=True)
    a = ap.parse_args()

    acct, colls = load_config()
    ids = {k: v["id"] for k, v in colls.items()}
    names = {k: v["name"] for k, v in colls.items()}

    mapping = json.load(open(a.map))
    bad = {k for k in mapping.values() if k not in ids}
    if bad:
        print("UNKNOWN THEME KEYS:", sorted(bad))
        sys.exit(1)

    groups = {}
    for mid, theme in mapping.items():
        groups.setdefault(theme, []).append(mid)

    for theme, mids in groups.items():
        ok = run("instagram-cli", "save-post", "--account-id", acct,
                 "--media-ids", ",".join(mids), "--collection-id", ids[theme])
        print(("OK  " if ok else "FAIL"), names[theme], len(mids))


if __name__ == "__main__":
    main()
