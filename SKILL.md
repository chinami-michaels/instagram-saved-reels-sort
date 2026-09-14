---
name: "instagram_saved_reels_sort"
description: "Sort Instagram saved reels into the user's topic collections, in small reviewable batches. Use when the user asks to sort saved reels, run a recurring sort, or work through a saved-reels backlog. Requires a connected Instagram account (instagram-cli)."
---

# Instagram Saved Reels Sort

## Purpose
Move saved Instagram reels out of the unsorted Saved bucket into the user's
own topic collections, two pages at a time, with a human review step before
anything moves. Built for backlogs of hundreds or thousands of saved reels,
and for a light recurring run that keeps new saves filed.

## Requirements
- An agent environment with the `instagram-cli` tool available and the user's
  Instagram account connected (`instagram-cli accounts` must return an
  account). This skill was built for Muse; on other platforms, substitute the
  equivalent commands for listing saved posts, describing media, managing
  saved collections, and moving posts between collections.
- Python 3 (standard library only).

## Setup (one time)
1. Run `python3 bin/setup.py`. It verifies the Instagram connection, lists the
   user's existing saved collections, and walks through defining topics.
2. The user picks a short theme key per topic (e.g. `ai`, `recipes`,
   `travel`). Collections that don't exist yet are created on Instagram.
3. Setup writes `~/.instagram-saved-reels-sort/config.json` (account id and
   the key → collection-id map) and a starter
   `~/.instagram-saved-reels-sort/my-collections.md`.
4. The user writes their routing rules — which reels go where, plus the edge
   cases — into `my-collections.md`. See
   `references/collections-template.md` for a worked example. This file is the
   source of truth for every batch; keep it current as tastes change.

## Tooling
Helpers live in `bin/`; all state (config, cursor, batch files) lives in
`~/.instagram-saved-reels-sort/` — never in `/tmp`, which can be wiped without
warning and would lose your place mid-sort.

- Fetch a batch: `python3 bin/fetch_batch.py fetch 2 <label>` — pulls 2 pages
  of saved posts (50/page), keeps reels, runs media-understanding, writes
  `<label>_reels.json` and `<label>_review.txt`, advances `cursor.txt`.
- Re-sync a lost cursor: `python3 bin/fetch_batch.py advance <pages>` — walks
  forward N pages without processing.
- Sort a batch: `python3 bin/sort_batch.py --batch <label> --map <map.json>` —
  moves reels into collections per a `{media_id: theme_key}` map.

Collection map and routing rules: the user's `my-collections.md` (template:
`references/collections-template.md`). Step-by-step with examples and
troubleshooting: `references/batch-procedure.md`. Dining dossiers (opt-in
per-restaurant health-inspection + review-trend reports for food-spot reels):
`references/dining-dossier.md`.

## Workflow
1. Fetch one batch (`fetch 2 <label>`), then read `<label>_review.txt`.
2. Assign every reel a theme key per the user's `my-collections.md`, or leave
   it unassigned (stays in Saved).
3. Write the map to `<label>_map.json` (`{"<media_id>": "<theme_key>"}`), run
   the sorter.
4. Report per-collection move counts plus the unsorted leftovers with reasons.
   Repeat per batch.

## Output Contract
After each batch: counts moved into each collection + list of reels left
unsorted (with reason, e.g. no description).

## Operating Rules
1. Two pages per batch — keeps reviews human-sized. Continue to the next batch
   only when asked, or during a full scheduled run.
2. Never move a reel with no usable description and no inferable content;
   unsortable reels stay in Saved.
3. Write actions only move posts between collections — nothing is deleted,
   unpublished, or unsaved globally. Say that plainly to the user before the
   first sort.
4. The cursor file is the source of truth for progress; if it looks stale,
   re-sync with `advance` rather than guessing pages.
5. Confirm the first batch's moves with the user before running unattended.
   After that, a recurring run (e.g. weekly) can process everything saved
   since the last batch until caught up.
6. Dining dossiers are opt-in: after a batch, offer one for any reel filed
   into a food/dining collection that's about a specific restaurant, or run
   one on demand. Never auto-run them for every food reel.
