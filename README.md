# Instagram Saved Reels Sort

An agent skill that files your Instagram saved reels into topic collections —
in small, human-reviewable batches. Built for backlogs of hundreds or
thousands of saved reels, and for a light recurring run that keeps new saves
filed.

**Who this is for:** people using an AI agent with Instagram connected
(specifically [Muse](https://muse.ai), which provides the `instagram-cli`
tool this skill shells out to). If that sentence didn't make sense, this isn't
for you yet.

## How it works

1. **Fetch** — pulls 2 pages of your saved posts (50/page), keeps the reels,
   and generates a plain-text review file with a one-line summary of each.
2. **Review** — you (or your agent) assign every reel a theme key, or skip it.
3. **Sort** — moves the mapped reels into your Instagram collections. Nothing
   is deleted, unpublished, or removed from Saved — it only files things into
   folders.

Two pages per batch keeps the review human-sized. Reels with no usable
description stay in Saved rather than being misfiled.

## Quick start

```bash
git clone https://github.com/<you>/instagram-saved-reels-sort.git
cd instagram-saved-reels-sort
python3 bin/setup.py
```

Setup verifies your Instagram connection, walks you through defining your
topics (short keys like `ai`, `recipes`, `travel`), creates any missing
collections on Instagram, and writes your routing rules to a file you own.

Then tell your agent: *"sort my saved reels."*

## Battle-tested

Built while sorting a real backlog of ~3,280 saved reels into 13 topic
collections. Survived a wiped `/tmp` mid-sort (state lives outside it), cursor
re-syncs, and every edge case a thousand-reel backlog throws at you.

## Files

- `SKILL.md` — the skill itself (drop this folder into your agent's skills dir)
- `bin/setup.py` — one-time interactive setup
- `bin/fetch_batch.py` — fetch 2 pages of reels + write the review file
- `bin/sort_batch.py` — move mapped reels into collections
- `references/collections-template.md` — how to define collections + routing rules
- `references/batch-procedure.md` — the full batch workflow + troubleshooting
- `references/dining-dossier.md` — opt-in per-restaurant health-inspection + review-trend reports

## License

MIT — see [LICENSE](LICENSE).
