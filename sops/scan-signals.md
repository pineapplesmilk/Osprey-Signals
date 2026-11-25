# SOP — Scan signals

**Commands:** "Scan signals" · "Pilot the signal scan" (10 accounts) · "Refresh routes" (§A only)

Checks band A and B accounts for the triggers in `triggers.md`, from public data, and writes a signals CSV for the work laptop. Fit (the band) says *who*; this says *when*.

**Inputs:**
- `data/input/accounts-<latest date>.csv` — `name,domain,segment,band` (from the work brain's "Score my accounts")
- `triggers.md` — triggers, what counts, windows, opener angles
- `context.md` — what Osprey sells, for opener angles
- `data/reference/routes.csv`, `zones.csv`, `exposure.csv` — built and refreshed here
- Tools: Apify (Google Search Results Scraper, Google News), web search and fetch, Apollo (people search — free; news search — optional)

## Fixed decisions (don't revisit without Jay)

- **Public data only.** Never Osprey's own alerts or data.
- **Bands A and B only.** C is never scanned.
- **Lead triggers are T1 and T2.** T3, S1 and S2 are checked only for accounts that already have a lead trigger (saves spend), except that T3's search is the same one as T1's.
- **Conflict is route-based, not destination-based,** and only level 1–2 events count (see `triggers.md` → T2).
- **Monthly caps:** £10 of Apify, 100 Apollo credits *(defaults; Jay can change)*. At the cap, stop.
- **Pilot first:** the first run is 10 accounts (5 airline, 5 business aviation) Jay knows well. Full runs start only after the pilot passes.

## A. Route map — first run, then quarterly ("Refresh routes")

1. For each A/B account in the **airline** segment: find its bases and published destinations (the airline's own route map or destinations page first, then its Wikipedia destinations list). Write city pairs to `data/reference/routes.csv` with the source link and date.
2. **Business aviation:** no published routes. Record home bases only (origin = destination = base) and rely on T1, T3 and S1 news for these accounts.
3. Report: accounts mapped, accounts with no route source found.

Cost: free (web fetch). Refresh quarterly or when an account's T3 fires.

## B. The scan

### 1. Check the input
- Latest file in `data/input/`. Exactly the four columns; otherwise stop.
- Pilot: take the 10 accounts Jay names (ask if he hasn't). Full run: all A and B.

### 2. Estimate — gate
- Per account: 1 Google search for T1/T3 (`site:aeroroutes.com "<name>"` plus a launch/route query, last 90 days) ≈ $0.0045 each.
- Once per run: the zone refresh (free pages) plus Google News on escalations (≈ 20 queries).
- Supporting checks for accounts with a lead trigger: S1 news search; S2 Apollo people search (free).
- Optional Apollo news search: 1 credit per 25 articles.
- Show the expected $ and credits against the caps and what's already spent this month (`log.md`). **Wait for Jay's yes.**

### 3. Refresh the conflict zone register (once per run)
- Read the current EASA conflict-zone information bulletins, FAA airspace bans and advisories, and closure notices for affected regions.
- Update `data/reference/zones.csv`: one row per zone, with `status_level`, `last_changed`, `source_url` and a rough polygon (`lat lon; lat lon; …`) covering the affected airspace.
- Run Google News on escalations in the last 6 weeks. Classify each event: level 1 (closure, new or upgraded ban/bulletin), level 2 (cancellations, diversions, groundings, airport attack), level 3 (no aviation impact — record as watch only).
- Run `python3 scripts/route_exposure.py` to rebuild `data/reference/exposure.csv`.

### 4. T2 — conflict events
- For each level 1–2 event in the last 2–6 weeks: match its zone to `exposure.csv`. High or medium exposure → T2 signal for that account.
- Record the event, the date, the source link, the affected route(s) and the likely impact (reroute, suspension, cost).

### 5. T1 and T3 — deadlines and routes
- Run the per-account search. Open the most relevant results (Aeroroutes, the airline's newsroom, aviation news).
- **T1:** a dated launch, season start, AOC or base opening still in the future → signal, with the date.
- **T3:** new, resumed or expanding routes announced in the last 90 days, before the first flight.
- A result older than its window, or with no date → no signal.

### 6. Supporting checks (only accounts with T1 or T2)
- **S1:** fleet additions or deliveries in the last 180 days (delivery news, registry entries).
- **S2:** Apollo people search on the domain for security, operations and CEO titles; keep only someone who started in the last 90 days, with a source.

### 7. Write the output
- Strength: **strongest** = T1 plus T2 or T3; **strong** = T1 or T2; **support only** = T3/S1 without a lead trigger (listed, not prioritised).
- Write `data/output/signals-<YYYY-MM-DD>.csv` (below). One row per signal; an account can have several.
- Signals from earlier runs that are past their window are not carried over.

### 8. Report, log and hand over
- Report: accounts scanned; accounts with a signal by strength; signals by trigger; spend and the month's balance.
- **Pilot:** Jay marks each signal right or wrong. Pass = at least 80% right and a cost per account he's happy with. Record the result and any source that found nothing (drop it).
- One line in `log.md`.
- Commit `data/output/`, `data/reference/` and `log.md` and push, so Jay can download the output on the work laptop.

## Output

`data/output/signals-<date>.csv`:

| Column | What goes in it |
|---|---|
| `name`, `domain`, `segment`, `band` | From the input |
| `trigger` | T1, T2, T3, S1 or S2 |
| `strength` | strongest · strong · support only |
| `summary` | The observable fact, one line |
| `event_date` | When it happened (T2, T3, S1, S2) |
| `deadline_date` | The future date (T1 only) |
| `route` | Affected city pair(s), if any |
| `evidence_url` | The link |
| `opener_angle` | One line from `triggers.md`'s angle, filled with their facts; no Osprey claims unless in `context.md` |
| `scanned_on` | Run date |

## Rules

- No outreach, no contact reveals beyond the S2 name, nothing written to any CRM.
- No signal without a link and a date inside its window.
- Never exceed the monthly caps.
- Only the four input columns enter this repo from the work side.

## What's worked / what hasn't

- **2026-11-25 pilot (10 accounts):** Apify Google search with `quickDateRange: m3` beat Claude's web search on the same accounts (signals for 8 accounts vs about 3); web search mostly returned stale pages. Use Apify for the per-account searches; use web search for the zone register (EASA bulletins surface well). Cost about $0.06 for 14 queries.
- The OurAirports download is blocked in some environments; `pip install airportsdata` and the script uses it instead.
- Social posts often carry no date: they can point to a route but don't count as evidence on their own.
