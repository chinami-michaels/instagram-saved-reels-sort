#!/usr/bin/env python3
"""One-time setup for instagram-saved-reels-sort.

- Verifies instagram-cli is available and an Instagram account is connected.
- Lists the user's existing saved collections.
- Defines short theme keys per topic and creates missing collections.
- Writes ~/.instagram-saved-reels-sort/config.json and a starter
  ~/.instagram-saved-reels-sort/my-collections.md.

Usage:
    python3 bin/setup.py [--account-id <id>]
"""
import argparse
import json
import os
import subprocess
import sys

CONFIG_DIR = os.path.expanduser("~/.instagram-saved-reels-sort")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
COLL_FILE = os.path.join(CONFIG_DIR, "my-collections.md")
WORK_DIR = os.path.join(CONFIG_DIR, "work")


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("CMD FAILED:", " ".join(args[:3]))
        print((r.stderr or "")[-1200:])
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        print("BAD JSON:", (r.stdout or "")[:300])
        return None


def find_accounts(d):
    """Return a list of (fbid, username) from `instagram-cli accounts` output."""
    out = []
    cands = []
    if isinstance(d, dict):
        for k in ("accounts", "data", "results"):
            if isinstance(d.get(k), list):
                cands = d[k]
                break
        else:
            cands = [d]
    elif isinstance(d, list):
        cands = d
    for a in cands:
        if not isinstance(a, dict):
            continue
        fbid = a.get("user_own_fbid") or a.get("user_fbid") or a.get("id")
        if fbid:
            out.append((str(fbid), a.get("username") or a.get("name") or "?"))
    return out


def find_collections(d):
    """Return a list of (collection_id, name) from `saved-collections` output."""
    cands = []
    if isinstance(d, dict):
        for k in ("collections", "data", "results", "items"):
            if isinstance(d.get(k), list):
                cands = d[k]
                break
    elif isinstance(d, list):
        cands = d
    out = []
    for c in cands:
        if not isinstance(c, dict):
            continue
        cid = c.get("collection_id") or c.get("id")
        name = c.get("name") or c.get("title")
        if cid and name:
            out.append((str(cid), name))
    return out


def ask(prompt, default=None):
    hint = f" [{default}]" if default else ""
    v = input(prompt + hint + ": ").strip()
    return v or (default or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account-id")
    a = ap.parse_args()

    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(WORK_DIR, exist_ok=True)

    acct = a.account_id
    if not acct:
        d = run("instagram-cli", "accounts")
        if d is None:
            sys.exit("Could not reach instagram-cli. Is it installed?")
        accts = find_accounts(d)
        if not accts:
            cr = run("instagram-cli", "connect-url")
            url = (cr or {}).get("connect_url", "")
            print("\nNo Instagram account is connected.")
            if url:
                print("Connect one at:", url)
            sys.exit("Connect an Instagram account, then re-run setup.")
        if len(accts) == 1:
            acct, uname = accts[0]
            print(f"Using Instagram account: {uname}")
        else:
            print("Multiple accounts found:")
            for i, (fbid, uname) in enumerate(accts, 1):
                print(f"  {i}. {uname}")
            n = ask("Which account", "1")
            try:
                acct, uname = accts[int(n) - 1]
            except (ValueError, IndexError):
                sys.exit("Invalid choice.")
            print(f"Using Instagram account: {uname}")

    d = run("instagram-cli", "saved-collections", "--account-id", acct)
    existing = find_collections(d) if d else []
    if existing:
        print("\nExisting saved collections:")
        for cid, name in existing:
            print(f"  - {name}")
    else:
        print("\nNo existing saved collections found (or none readable).")

    print("\nNow define the topics you want reels sorted into.")
    print("Give each a short key (letters only, e.g. ai, recipes, travel).")
    print("Type 'done' when finished. Existing collections can be reused by key.")
    print("Example keys: ai, recipes, travel, workouts, home, style\n")

    by_name = {name.lower(): cid for cid, name in existing}
    themes = {}
    while True:
        key = ask("Theme key (or 'done')").lower().replace(" ", "")
        if key in ("done", "quit", ""):
            break
        if not key.isalpha():
            print("  Keys must be letters only, no spaces.")
            continue
        if key in themes:
            print("  Key already defined.")
            continue
        name = ask(f"  Collection name for '{key}'", key.capitalize())
        cid = by_name.get(name.lower())
        if cid:
            print(f"  Reusing existing collection '{name}'.")
        else:
            print(f"  Creating collection '{name}' on Instagram...")
            r = run("instagram-cli", "create-saved-collection",
                    "--account-id", acct, "--name", name)
            nc = find_collections(r) if r else []
            if nc:
                cid = nc[0][0]
                print("  Created.")
            else:
                cid = ask("  Could not read the new collection id — paste it here")
        themes[key] = {"name": name, "id": str(cid)}

    if not themes:
        sys.exit("No themes defined — nothing to write.")

    cfg = {"account_id": acct, "work_dir": WORK_DIR, "collections": themes}
    json.dump(cfg, open(CONFIG_FILE, "w"), indent=2)
    print(f"\nWrote {CONFIG_FILE}")

    lines = ["# My collections & routing rules",
             "",
             "The agent reads this file every batch to decide where each reel goes.",
             "Edit the routing rules as your tastes change.",
             "",
             "## Collections",
             "",
             "| key | name | id |",
             "|-----|------|----|"]
    for key, t in themes.items():
        lines.append(f"| {key} | {t['name']} | {t['id']} |")
    lines += ["",
              "## Routing rules",
              "",
              "- Assign by what the reel is *about*, using the caption plus the",
              "  narrative summary in the review file.",
              "- Write your edge cases here explicitly (e.g. 'AI-topic reels go to",
              "  ai; AI-adjacent-but-not-AI like robotics or coding stays in its",
              "  original collection').",
              "- No usable description and nothing inferable from the caption →",
              "  leave unsorted in Saved; list it in the batch report.",
              ""]
    open(COLL_FILE, "w").write("\n".join(lines))
    print(f"Wrote {COLL_FILE}")
    print("\nSetup complete. Next: ask your agent to sort your saved reels.")


if __name__ == "__main__":
    main()
