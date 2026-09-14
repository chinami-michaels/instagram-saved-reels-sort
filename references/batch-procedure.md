# Batch procedure (detail)

## 0. One-time setup

```bash
python3 bin/setup.py
```

Verifies the Instagram connection, defines theme keys, creates missing
collections, and writes the config plus a starter `my-collections.md`. See
`collections-template.md` for how to write good routing rules.

## 1. Fetch

```bash
python3 bin/fetch_batch.py fetch 2 batch1
```

Fetches 2 pages of 50 saved posts starting after the saved cursor, keeps reels
(`media_type == VIDEO` or `/reel/` in the permalink), saves
`batch1_reels.json`, runs media-understanding, writes `batch1_review.txt`,
and advances `cursor.txt`. All files land in the configured work dir (default
`~/.instagram-saved-reels-sort/work/`).

The review file looks like:

```
[1] someuser :: 48392017561234567
    An agent explains how it automates client onboarding with voice notes...

[2] otheruser :: 58392017561234568
    (NO DESCRIPTION) cap: pov: your sunday reset tags:['wellness','sunday']
```

## 2. Review and map

Read every entry, pick a theme key from the user's `my-collections.md` (or
skip it to leave it in Saved). Write the map:

```json
{"48392017561234567": "ai", "58392017561234568": "food"}
```

Save as `batch1_map.json` in the work dir.

## 3. Sort

```bash
python3 bin/sort_batch.py --batch batch1 --map <work-dir>/batch1_map.json
```

Moves each mapped reel into its collection via `instagram-cli save-post`. Keys
not in the map are left alone. This only files posts into collections —
nothing is deleted, unpublished, or removed from Saved.

## 4. Report

Per-collection move counts, plus the unsorted leftovers with reasons.

## Troubleshooting

- **Cursor lost or blank:** re-sync with `python3 bin/fetch_batch.py advance N`
  (N = pages already processed). Never store the cursor in `/tmp` — it gets
  wiped without warning and you'll lose your place mid-sort.
- **Understanding returns nothing:** the page fetch and the understanding call
  are separate steps; re-run `fetch` for that batch label.
- **A page returns 0 posts:** end of the saved list — caught up, stop.
- **Command failure:** both helpers print the failing command prefix and the
  tail of stderr; fix and retry the batch, don't skip ahead.
- **Rate limits:** the Instagram API enforces them and they are not retried.
  Two pages per batch stays comfortably inside; don't raise the page size to
  "go faster."
