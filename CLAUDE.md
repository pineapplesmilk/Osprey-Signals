# Osprey Signals — read this first

Finds fresh, evidenced buying signals across Jay's Osprey accounts. Runs on Jay's **personal laptop** with personal Claude (Apify, Apollo, web search and fetch). Output is a signals CSV that Jay downloads to the work laptop.

## Rules

1. **Run on command only.** No scheduled or proactive runs.
2. **Public data only.** Never Osprey's own products, alerts or data.
3. **Estimate before spending.** Show expected Apify spend and Apollo credits and wait for Jay's yes. Stop at the monthly cap; never top up.
4. **Evidence or it doesn't count:** every signal has a link and a date inside its freshness window.
5. **Scan only — no outreach, no contact reveals, nothing written to any CRM.**
6. **Triggers come only from `triggers.md`.** Don't invent new ones; propose them to Jay.
7. **Company claims about Osprey come only from `context.md`.** Missing → leave the claim out.
8. **Input holds four columns only:** `name,domain,segment,band`. Anything more → stop and ask Jay to re-export.
9. **After every run:** one line in `log.md` (date, accounts, signals, spend, lesson).

## Commands

| Jay says | Do |
|---|---|
| "Scan signals" · "Run the signal scan" | `sops/scan-signals.md` |
| "Pilot the signal scan" | `sops/scan-signals.md`, pilot mode (10 accounts) |
| "Refresh routes" | `sops/scan-signals.md` §A |
| "Update triggers" | Replace `triggers.md` with the latest from the work brain's `company/triggers.md` (no customer names) |

## Map

```
CLAUDE.md                 this file
triggers.md               the approved triggers, windows and opener angles
context.md                what Osprey sells, for opener angles (Jay fills in)
sops/scan-signals.md      the SOP
scripts/route_exposure.py route × conflict-zone exposure (code, no AI)
data/input/               accounts-<date>.csv from the work laptop
data/reference/           routes.csv, zones.csv, exposure.csv, airports.csv
data/output/              signals-<date>.csv for the work laptop
log.md                    run log
```
