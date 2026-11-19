"""Route exposure: which routes fly into or over which conflict zones.

Usage:
    python3 scripts/route_exposure.py [--airports data/reference/airports.csv]

Reads:
    data/reference/routes.csv   account,domain,origin_iata,dest_iata,source_url,last_refreshed
    data/reference/zones.csv    zone_id,name,status_level,last_changed,source_url,polygon
                                polygon = "lat lon; lat lon; ..." (at least 3 points)
    data/reference/airports.csv OurAirports file (downloaded on first run if missing)
Writes:
    data/reference/exposure.csv account,domain,origin_iata,dest_iata,zone_id,exposure
        exposure = high   (origin or destination inside the zone)
                   medium (the great-circle path crosses the zone)

The path is a great-circle approximation sampled every 50 km. Real tracks
deviate around closed airspace, so treat "medium" as likely, not certain.
Zones crossing the antimeridian are not supported.
"""
import argparse
import csv
import math
import os
import sys
import urllib.request

AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
REF = "data/reference"
STEP_KM = 50


def load_airports(path):
    if not os.path.exists(path):
        print(f"Downloading airports to {path} ...", file=sys.stderr)
        urllib.request.urlretrieve(AIRPORTS_URL, path)
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            code = (r.get("iata_code") or "").strip().upper()
            if code:
                out[code] = (float(r["latitude_deg"]), float(r["longitude_deg"]))
    return out


def parse_polygon(text):
    pts = []
    for part in text.split(";"):
        part = part.strip()
        if part:
            lat, lon = part.split()
            pts.append((float(lat), float(lon)))
    if len(pts) < 3:
        raise ValueError(f"polygon needs at least 3 points: {text!r}")
    return pts


def inside(pt, poly):
    """Ray casting on lat/lon; fine for zone-sized polygons away from the poles."""
    lat, lon = pt
    hit = False
    j = len(poly) - 1
    for i in range(len(poly)):
        yi, xi = poly[i]
        yj, xj = poly[j]
        if (yi > lat) != (yj > lat):
            x_cross = xi + (lat - yi) * (xj - xi) / (yj - yi)
            if lon < x_cross:
                hit = not hit
        j = i
    return hit


def great_circle_points(a, b, step_km=STEP_KM):
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    d = 2 * math.asin(math.sqrt(
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2))
    if d == 0:
        return [a]
    n = max(1, int(d * 6371 / step_km))
    pts = []
    for k in range(n + 1):
        f = k / n
        A = math.sin((1 - f) * d) / math.sin(d)
        B = math.sin(f * d) / math.sin(d)
        x = A * math.cos(lat1) * math.cos(lon1) + B * math.cos(lat2) * math.cos(lon2)
        y = A * math.cos(lat1) * math.sin(lon1) + B * math.cos(lat2) * math.sin(lon2)
        z = A * math.sin(lat1) + B * math.sin(lat2)
        pts.append((math.degrees(math.atan2(z, math.hypot(x, y))),
                    math.degrees(math.atan2(y, x))))
    return pts


def exposure(origin, dest, poly):
    if inside(origin, poly) or inside(dest, poly):
        return "high"
    if any(inside(p, poly) for p in great_circle_points(origin, dest)):
        return "medium"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--airports", default=f"{REF}/airports.csv")
    ap.add_argument("--routes", default=f"{REF}/routes.csv")
    ap.add_argument("--zones", default=f"{REF}/zones.csv")
    ap.add_argument("--out", default=f"{REF}/exposure.csv")
    args = ap.parse_args()

    airports = load_airports(args.airports)
    with open(args.zones, newline="", encoding="utf-8") as f:
        zones = [(z["zone_id"], parse_polygon(z["polygon"])) for z in csv.DictReader(f)]
    missing, rows = set(), []
    with open(args.routes, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            o, d = r["origin_iata"].strip().upper(), r["dest_iata"].strip().upper()
            if o not in airports or d not in airports:
                missing.update(c for c in (o, d) if c not in airports)
                continue
            for zone_id, poly in zones:
                level = exposure(airports[o], airports[d], poly)
                if level:
                    rows.append({"account": r["account"], "domain": r["domain"],
                                 "origin_iata": o, "dest_iata": d,
                                 "zone_id": zone_id, "exposure": level})
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["account", "domain", "origin_iata",
                                          "dest_iata", "zone_id", "exposure"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} exposed route-zone pairs written to {args.out}")
    if missing:
        print("Unknown airport codes (routes skipped): " + ", ".join(sorted(missing)))


if __name__ == "__main__":
    main()
