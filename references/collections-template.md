# Collections & routing rules — template

`bin/setup.py` writes a starter copy of this to
`~/.instagram-saved-reels-sort/my-collections.md` with your actual collection
IDs filled in. That file — not this template — is what the agent reads every
batch. Edit its routing rules whenever your tastes change.

## Format

```markdown
## Collections

| key  | name    | id               |
|------|---------|------------------|
| ai   | AI      | 1000000000000001 |
| food | Recipes | 1000000000000002 |

## Routing rules

- ...
```

Keys are short, letters-only labels you type in the map file. Keep them
stable — the map file references keys, and the config maps keys to Instagram
collection IDs, so renaming a collection on Instagram never breaks a batch.

## Worked example

A user saving a mix of tech, cooking, and travel reels might define:

| key    | name    | notes                                    |
|--------|---------|------------------------------------------|
| ai     | AI      | tools, demos, explainers, agent builds   |
| food   | Recipes | dishes to try; restaurant roundups stay out |
| travel | Trips   | places to go; hotel reviews go to `food`? no — decide once, write it down |

…and routing rules like:

- Assign by what the reel is *about*, using the caption plus the narrative
  summary in the review file — not by who posted it.
- **AI rule:** AI-topic reels → `ai`. AI-adjacent-but-not-AI stays in its
  original collection: robotics demos, creative coding, app builds.
- **Food rule:** recipes to cook → `food`. Restaurant *roundups* ("10 spots in
  Austin") → `travel`, even if the reel is mostly food shots.
- **No usable description** and nothing inferable from the caption → leave
  unsorted in Saved; list it in the batch report with the reason.

The pattern to copy: name the theme, then name the near-miss that belongs
somewhere else. Most misfiles come from near-misses, not from reels with no
plausible home at all.

## Tips

- 5–15 collections is the sweet spot. Fewer and the sort isn't worth running;
  more and every batch turns into taxonomy debate.
- A "misc" collection is a trap — it becomes a second unsorted pile. If a reel
  doesn't fit, leave it in Saved and revisit your themes after a few batches.
- Revisit this file after the first 2–3 batches. The rules you *thought* you
  wanted always need one round of corrections.
