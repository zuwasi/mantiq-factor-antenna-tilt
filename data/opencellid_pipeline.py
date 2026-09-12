"""OpenCelliD -> antenna-tilt instance pipeline.

Turns real cell-tower data into a tilt-optimization instance compatible
with the verified QAOA objective  Cost(t) = t^T*I*t - lambda*c^T*t + mu*E(t)
(docs/antenna_tilt_problem.md) and the CSV instance format used by
data/instance_3sitesx3sectors*.csv.

Three input modes (first available wins):
  1. --token TOKEN   download country CSV from OpenCelliD (Israel = MCC 425).
                     Free token: register at https://opencellid.org/downloads
  2. --csv PATH      use an already-downloaded OpenCelliD CSV (.csv or .csv.gz)
  3. --demo          no network: seed cells from data/towers_telaviv_raw.csv (OSM)

Then, for every mode:
  - filter to a bounding box (--bbox lat_min,lon_min,lat_max,lon_max)
  - cluster cells into --sites sites (greedy radius clustering)
  - each site = up to --sectors (3) cells nearest its centroid, azimuths 0/120/240
  - interference I[i][j] = I_MAX * exp(-d_ij / D0)  (meters, haversine)
  - coverage gain c[i] = C_MIN + C_SPAN * (1 - exp(-d_nn / D0))  (denser -> higher)
  - writes <prefix>.csv, <prefix>_interference.csv, <prefix>_meta.json

ASSUMPTIONS (documented per docs/assumptions.md): no public dataset carries
tilt angles or interference matrices - positions are real, RF parameters are
physically-motivated synthetic constants below.

Run:
  py -3.12 data/opencellid_pipeline.py --demo --sites 3 --out-prefix opencellid_demo
  py -3.12 data/opencellid_pipeline.py --token XXX --sites 10 --out-prefix opencellid_il
"""
import argparse
import csv
import gzip
import json
import math
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---- physical / model constants (ASSUMPTIONS - cite as such in the pitch) ----
I_MAX = 1.35          # interference coupling at zero distance (same site)
D0_M = 1000.0         # interference decay length in meters
C_MIN, C_SPAN = 0.8, 0.4  # coverage gain range as a function of neighbor distance
DEFAULT_TILT_LEVELS = 10  # official brief: +/-10 deg electronic fine-tuning
SECTOR_AZIMUTHS = (0, 120, 240)
DEFAULT_BBOX = (32.00, 34.70, 32.15, 34.90)  # Tel Aviv (matches DATA_SOURCES.md)
OPENCELLID_URL = "https://opencellid.org/ocid/downloads?token={token}&type=mcc&file={mcc}.csv.gz"
OPENCELLID_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def in_bbox(lat, lon, bbox):
    return bbox[0] <= lat <= bbox[2] and bbox[1] <= lon <= bbox[3]


OCID_FIELDS = ["radio", "mcc", "net", "area", "cell", "unit", "lon", "lat",
               "range", "samples", "changeable", "created", "updated", "averageSignal"]


def iter_rows(path, gzipped=False):
    """Materialize CSV rows so file handles die before iteration.
    Handles both headered CSVs and headerless OpenCelliD country exports
    (radio,mcc,net,area,cell,unit,lon,lat,...)."""
    opener = gzip.open if gzipped else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        lines = f.readlines()
    if lines and "lat" in lines[0].lower():
        reader = csv.DictReader(lines)  # headered (OSM/manual CSV)
    else:
        reader = csv.DictReader(lines, fieldnames=OCID_FIELDS)
    return list(reader)


def load_raw_cells(args):
    """Return list of {id, lat, lon} inside the bbox."""
    bbox = parse_bbox(args.bbox)
    if args.csv:
        path = Path(args.csv)
        if not path.exists():
            sys.exit(f"csv not found: {path}")
        print(f"[1/4] reading existing CSV {path.name}")
        rows = iter_rows(path, gzipped=path.suffix == ".gz")
    elif args.token or os.environ.get("OPENCELLID_TOKEN"):
        token = args.token or os.environ["OPENCELLID_TOKEN"]
        url = OPENCELLID_URL.format(token=token, mcc=args.mcc)
        target = HERE / f"opencellid_{args.mcc}.csv.gz"
        if target.exists() and target.read_bytes()[:2] == b"\x1f\x8b":
            print(f"[1/4] reusing cached {target.name} (delete it to force re-download)")
        else:
            print(f"[1/4] downloading OpenCelliD MCC {args.mcc} -> {target.name}")
            req = urllib.request.Request(url, headers={"User-Agent": OPENCELLID_UA})
            with urllib.request.urlopen(req, timeout=120) as resp, open(target, "wb") as out:
                out.write(resp.read())
            if target.read_bytes()[:2] != b"\x1f\x8b":
                msg = target.read_text(encoding="utf-8", errors="replace")[:200]
                sys.exit(f"download failed (not a gzip file): {msg}")
        rows = iter_rows(target, gzipped=True)
    elif args.demo:
        seed = HERE / "towers_telaviv_raw.csv"
        print(f"[1/4] demo mode: seeding cells from {seed.name} (OSM, no token)")
        rows = iter_rows(seed)
    else:
        sys.exit("provide --token TOKEN, --csv PATH, or --demo")

    cells, n_total = [], 0
    for row in rows:
        n_total += 1
        try:
            lat, lon = float(row["lat"]), float(row["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        if in_bbox(lat, lon, bbox):
            cells.append({"id": row.get("cellid") or row.get("osm_id") or row.get("source_id") or str(len(cells)),
                          "lat": lat, "lon": lon})
    if len(cells) < args.sites:
        sys.exit(f"bbox contains only {len(cells)} cells < --sites {args.sites}; "
                 f"widen --bbox or lower --sites")
    print(f"      {len(cells)} cells in bbox (of {n_total} rows)")
    return cells, bbox


def parse_bbox(s):
    parts = tuple(float(x) for x in s.split(","))
    if len(parts) != 4:
        sys.exit("--bbox must be lat_min,lon_min,lat_max,lon_max")
    return parts


def cluster_sites(cells, n_sites, radius_m):
    """Greedy radius clustering; keeps the n_sites largest clusters."""
    clusters, current = [], []
    for c in sorted(cells, key=lambda c: (c["lat"], c["lon"])):
        if current and haversine_m(current[0]["lat"], current[0]["lon"],
                                   c["lat"], c["lon"]) > radius_m:
            clusters.append(current)
            current = []
        current.append(c)
    if current:
        clusters.append(current)
    clusters.sort(key=len, reverse=True)
    return clusters[:n_sites]


def build_instance(clusters):
    """Each site keeps up to 3 cells nearest its centroid as sectors."""
    antennas = []
    for site_id, cluster in enumerate(clusters):
        c_lat = sum(c["lat"] for c in cluster) / len(cluster)
        c_lon = sum(c["lon"] for c in cluster) / len(cluster)
        for sec, cell in enumerate(sorted(cluster, key=lambda c: haversine_m(c_lat, c_lon, c["lat"], c["lon"]))[:3]):
            antennas.append({"site_id": site_id, "sector": sec, "antenna_id": len(antennas),
                             "source_id": cell["id"], "lat": cell["lat"], "lon": cell["lon"],
                             "height_m": 25.0, "azimuth_deg": SECTOR_AZIMUTHS[sec],
                             "tilt_levels": DEFAULT_TILT_LEVELS, "coverage_gain": 1.0})
    # interference + coverage from pairwise distances
    for i, a in enumerate(antennas):
        dists = []
        for j, b in enumerate(antennas):
            if i == j:
                continue
            d = haversine_m(a["lat"], a["lon"], b["lat"], b["lon"])
            dists.append(d)
            same_site = a["site_id"] == b["site_id"]
            coupling = I_MAX if same_site else I_MAX * math.exp(-d / D0_M)
            a.setdefault("I", {})[j] = round(coupling, 4)
        nn = min(dists) if dists else D0_M
        a["coverage_gain"] = round(C_MIN + C_SPAN * (1 - math.exp(-nn / D0_M)), 3)
    return antennas


def write_instance(antennas, prefix, bbox, source_note):
    linear = HERE / f"{prefix}.csv"
    interf = HERE / f"{prefix}_interference.csv"
    meta = HERE / f"{prefix}_meta.json"
    n = len(antennas)

    with open(linear, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in antennas[0].keys() if k != "I"])
        w.writeheader()
        for a in antennas:
            w.writerow({k: v for k, v in a.items() if k != "I"})

    with open(interf, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([f"antenna_{i}" for i in range(n)])
        for i in range(n):
            w.writerow([f"antenna_{i}"] + [0.0 if i == j else antennas[i]["I"][j] for j in range(n)])

    meta_data = {"challenge": "antenna tilt optimization (official spec)",
                 "source": source_note, "license": "see DATA_SOURCES.md",
                 "bbox_lat_min": bbox[0], "bbox_lon_min": bbox[1],
                 "bbox_lat_max": bbox[2], "bbox_lon_max": bbox[3],
                 "tilt_levels": DEFAULT_TILT_LEVELS, "sites": len({a["site_id"] for a in antennas}),
                 "antennas": n, "qubits_coarse_2q": 2 * n,
                 "assumptions": {"I_MAX": I_MAX, "D0_m": D0_M,
                                 "coverage_model": f"{C_MIN}+{C_SPAN}*(1-exp(-d_nn/{D0_M}))"},
                 "site_coords": [{"site_id": s, "lat": a["lat"], "lon": a["lon"]}
                                 for s in sorted({a["site_id"] for a in antennas})
                                 for a in antennas if a["site_id"] == s and a["sector"] == 0]}
    meta.write_text(json.dumps(meta_data, indent=2), encoding="utf-8")
    return linear, interf, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--token", help="OpenCelliD API token (or env OPENCELLID_TOKEN)")
    ap.add_argument("--mcc", default="425", help="country MCC (425 = Israel)")
    ap.add_argument("--csv", help="existing OpenCelliD/OSM csv path (.csv or .csv.gz)")
    ap.add_argument("--demo", action="store_true", help="seed from towers_telaviv_raw.csv, no network")
    ap.add_argument("--bbox", default=",".join(map(str, DEFAULT_BBOX)),
                    help="lat_min,lon_min,lat_max,lon_max")
    ap.add_argument("--sites", type=int, default=3)
    ap.add_argument("--sectors", type=int, default=3)
    ap.add_argument("--radius", type=float, default=500.0, help="site clustering radius (m)")
    ap.add_argument("--out-prefix", default="opencellid_instance")
    args = ap.parse_args()
    args.sectors = len(SECTOR_AZIMUTHS)  # fixed by convention

    cells, bbox = load_raw_cells(args)
    clusters = cluster_sites(cells, args.sites, args.radius)
    antennas = build_instance(clusters)
    note = ("OpenCelliD country export (CC BY-SA 4.0)" if (args.token or args.csv)
            else "OpenStreetMap towers via Overpass (ODbL)")
    linear, interf, meta = write_instance(antennas, args.out_prefix, bbox, note)
    print(f"[4/4] wrote:")
    for p in (linear, interf, meta):
        print(f"      {p}")
    print(f"      {len({a['site_id'] for a in antennas})} sites x 3 sectors = "
          f"{len(antennas)} antennas = {2 * len(antennas)} qubits (coarse 2q/antenna)")


if __name__ == "__main__":
    main()
