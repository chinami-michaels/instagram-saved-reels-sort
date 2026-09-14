#!/usr/bin/env python3
"""Fetch a batch of saved reels for review.

Usage:
    python3 bin/fetch_batch.py fetch 2 <label>   # fetch 2 pages, write review files
    python3 bin/fetch_batch.py advance <pages>   # walk cursor forward N pages without processing

Reads account id and work dir from ~/.instagram-saved-reels-sort/config.json
(written by bin/setup.py). Keeps everything out of /tmp, which can be wiped
without warning.
"""
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
    work = os.path.expanduser(cfg.get("work_dir", os.path.join(CONFIG_DIR, "work")))
    os.makedirs(work, exist_ok=True)
    return cfg["account_id"], work


ACCT, WORK = load_config()
CURSOR_FILE = os.path.join(WORK, "cursor.txt")


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print("CMD FAILED:", " ".join(args[:4]), file=sys.stderr)
        print((r.stderr or "")[-1500:], file=sys.stderr)
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        print("BAD JSON:", (r.stdout or "")[:300], file=sys.stderr)
        return None


def get_cursor():
    if os.path.exists(CURSOR_FILE):
        return open(CURSOR_FILE).read().strip() or None
    return None


def set_cursor(c):
    open(CURSOR_FILE, "w").write(c or "")


def saved_page(cursor):
    args = ["instagram-cli", "saved-posts", "--account-id", ACCT, "--limit", "50"]
    if cursor:
        args += ["--after", cursor]
    return run(*args)


mode = sys.argv[1] if len(sys.argv) > 1 else "fetch"

if mode == "advance":
    # advance the cursor N pages without processing (to re-sync after a wipe)
    pages = int(sys.argv[2])
    cursor = get_cursor()
    for n in range(pages):
        d = saved_page(cursor)
        if d is None:
            sys.exit(1)
        cursor = d.get("end_cursor")
        set_cursor(cursor)
        print(f"advanced page {n + 1}: {len(d.get('posts', []))} posts", flush=True)
    print("cursor now:", (cursor or "")[:40])

elif mode == "fetch":
    # fetch N pages of reels + media understanding; save for review
    pages = int(sys.argv[2])
    label = sys.argv[3] if len(sys.argv) > 3 else "batch"
    cursor = get_cursor()
    all_reels = []
    for n in range(pages):
        d = saved_page(cursor)
        if d is None:
            sys.exit(1)
        posts = d.get("posts", [])
        reels = [p for p in posts
                 if p.get("media_type") == "VIDEO"
                 or "/reel/" in (p.get("media_permalink") or "")]
        for p in reels:
            u = ((p.get("author_info") or {}).get("username")) or "?"
            cap = (p.get("post_caption") or "").replace("\n", " ")[:160]
            all_reels.append((p["media_id"], u, cap, p.get("hashtags") or []))
        cursor = d.get("end_cursor")
        set_cursor(cursor)
        print(f"page: {len(posts)} posts, {len(reels)} reels", flush=True)

    print("TOTAL reels:", len(all_reels))
    json.dump(all_reels, open(os.path.join(WORK, f"{label}_reels.json"), "w"))

    mids = [m for m, _, _, _ in all_reels]
    if mids:
        d = run("instagram-cli", "media-understanding", "--account-id", ACCT,
                "--media-ids", ",".join(mids))
        if d is None:
            sys.exit(1)
        json.dump(d["media"],
                  open(os.path.join(WORK, f"{label}_understanding.json"), "w"))
        print("understanding received:", len(d["media"]))
        ums = {m["media_id"]: (m.get("narrative_summary") or "")
               for m in d["media"]}
        out = open(os.path.join(WORK, f"{label}_review.txt"), "w")
        for i, (mid, u, cap, tags) in enumerate(all_reels, start=1):
            s = ums.get(mid, "").replace("\n", " ")
            out.write(f"\n[{i}] {u} :: {mid}\n")
            out.write("    " + (s[:280] if s else
                                "(NO DESCRIPTION) cap: " + cap[:160] +
                                " tags:" + str(tags)) + "\n")
        out.close()
        print("review written:", os.path.join(WORK, f"{label}_review.txt"))
