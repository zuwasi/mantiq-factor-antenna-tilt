# Sample data sources for the antenna tilt demo

Real AT&T data will NOT be provided for the hackathon. These are the
datasets we can legally use, best-first.

## 0. Pipeline (READY - data/oracle_tilt.py + data/opencellid_pipeline.py)
- data/opencellid_pipeline.py: real tower positions -> tilt instance
    py -3.12 data/opencellid_pipeline.py --token TOKEN --sites 10 --out-prefix opencellid_il
    (or --demo for offline OSM seeding, or --csv for a downloaded file)
- data/oracle_tilt.py: exact brute-force optimum + greedy baseline
    py -3.12 data/oracle_tilt.py --prefix opencellid_demo --json-out verification/results/opencellid_demo_oracle.json
- Verified: opencellid_demo (7 antennas, real OSM positions, Tel Aviv bbox)
  -> optimum -20.0205, greedy gap 3.24% (verification/results/opencellid_demo_oracle.json)
- Verified on REAL data (OpenCelliD MCC 425, Tel Aviv bbox, 2026-09-08):
  - opencellid_il2 (6 antennas): exact optimum -8.5320, greedy gap 2.69%
    (verification/results/opencellid_il2_oracle.json)
  - opencellid_il (30 antennas = 10^30 search space): greedy -28.4553,
    exact enumeration intractable BY DESIGN - that number IS the pitch
    headline (verification/results/opencellid_il_greedy.json)
- Downloads cache to data/opencellid_425.csv.gz; OpenCelliD allows
  2 downloads per file per day (RATE_LIMITED otherwise) - the cache
  avoids burning the quota; delete the .gz to force a re-download.
- Token: free at https://opencellid.org/downloads - do NOT commit it;
  reset after the hackathon.

## 1. OpenStreetMap telecom towers (USED - already downloaded)
- File: data/towers_telaviv_raw.csv (17 real structures, Tel Aviv bbox)
- Derived: data/instance_cluster8.csv + instance_cluster8_interference.csv
  (8-antenna demo cluster = 16 qubits, params documented as assumptions)
- Source: Overpass API query on node[man_made=mast/tower][telecom] and
  node[communication:mobile_phone], bbox (32.00,34.70)-(32.15,34.90)
- License: ODbL - credit "OpenStreetMap contributors" in the pitch deck
- To re-extract another area:
  curl -X POST https://overpass-api.de/api/interpreter
       --data-urlencode "data=[out:json];node['man_made'='mast']['tower:type'='communication'](LAT_MIN,LON_MIN,LAT_MAX,LON_MAX);out body;"

## 2. OpenCelliD - world's largest open cell-tower DB (40M+ records)
- What: tower locations + radio type (GSM/LTE/NR) + operator (MCC/MNC)
- Access: free API token after registration at opencellid.org
  -> downloads.php -> country CSV (Israel = MCC 425)
- License: CC BY-SA 4.0 (attribution required)
- Note: locations are approximate (triangulated), no heights/tilts

## 3. OpenCelliD snapshot on ClickHouse (40M rows, free SQL)
- https://sql.clickhouse.com -> sample data "Cell Towers"
- Browser-only (Cloudflare blocks scripted access); query Israel:
  SELECT * FROM cell_towers WHERE mcc = 425
- Same underlying data as option 2, 2021 snapshot

## 4. FCC Antenna Structure Registration (US data - fits AT&T story)
- What: registered US towers/antenna structures with real heights,
  coordinates, owner
- Access: https://www.fcc.gov/wireless/data/public-access-files-database-downloads
  (public zip files, no registration)
- Most "AT&T-realistic" geography if the pitch wants US-flavored data

## 5. DeepSense 6G (research datasets)
- https://www.deepsense6g.net - real measured wireless channels,
  mmWave beam datasets. Overkill for QAOA demo but strong for
  "learned/quantum-ready channel models" narrative.

## What the datasets do NOT contain (and how we cover it)
No public dataset has antenna TILT angles or interference matrices -
these are operator-internal. Our approach: real tower positions from
OSM/OpenCelliD + physically-motivated synthetic parameters
(4 tilt levels, exponential distance-decay interference coupling),
all documented in docs/antenna_tilt_problem.md as assumptions.
This is standard hackathon practice and defensible before judges.
