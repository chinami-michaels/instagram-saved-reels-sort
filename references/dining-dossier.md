# Dining dossier (opt-in enrichment)

For reels about a specific restaurant or food spot (filed into a
food/dining-themed collection), offer a dossier: health-inspection record +
review summary with recent-review trends. Offer it after the batch report,
or run one on demand ("dossier <restaurant name>"). Never auto-run dossiers
for every food reel — each one is a separate research task.

## 1. Identify the place
- Pull the restaurant name + city from the caption/review file.
- Resolve the exact place with the places_search skill (`local-search` as a
  `known_place` query) to confirm name, city, and address. If you can't
  resolve an exact match, say so — don't guess.

## 2. Health inspection
- US inspection data is county-by-county; there is no national API. Find
  the county health department's public inspection portal for the
  restaurant's city/county and search the establishment name there.
- Worked example: Phoenix-metro spots → Maricopa County Environmental
  Services restaurant search (envapp.maricopa.gov) — public records, free,
  with A/B/C/D grades where the establishment participates.
- Report: latest grade (if the county grades), inspection date(s), and
  violations from the last ~12 months grouped by severity (e.g. Priority /
  Priority Foundation / Core in Maricopa County's system), noting which
  were corrected at time of inspection.
- News check: search the restaurant name (plus "health violation" /
  "inspection"). Local outlets often headline notable inspections as
  roundups or single stories. Include any recent headlines with dates, but
  pair every headline with the actual inspection record above: a headline
  is a snapshot, the record shows whether it was corrected.

## 3. Review summary + trends
- Pull recent Google and Yelp reviews (`places details` from the
  places_search skill, plus web search for the Yelp/Google Maps pages when
  more review text is needed).
- Summarize: overall sentiment, what people consistently praise, what they
  consistently complain about.
- Trends: weight the last 3–6 months heaviest. Call out new or worsening
  themes ("service complaints cluster since spring") and old complaints
  that seem resolved. Date-bound every trend claim.

## 4. Output
One compact dossier per restaurant: name + city, grade + latest violations
with dates, review summary, recent trends. Present violations factually with
dates — a single old violation is not a current danger; say what the record
actually shows.

## Rules
- Opt-in only, per restaurant.
- Never present inspection data for a place you couldn't exactly resolve.
- If the county has no public portal, say so and fall back to Yelp's health
  info (where available) plus the review trends.
- Outside the US, find the equivalent local food-safety authority; if none
  is public, say so.
