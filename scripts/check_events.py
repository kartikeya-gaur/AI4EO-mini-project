"""Week 1 event feasibility check.

For each event in configs/events.yaml, count Sentinel-1 and Sentinel-2 scenes
(Planetary Computer STAC) and ICESat-2 ATL13 / SWOT granules (NASA Earthdata).

NOT RUN YET: written without network access. Before trusting it, verify the STAC
collection ids, the Earthdata short names, and run it once by hand. Needs:
    pip install -e ".[data]"
    EARTHDATA_USERNAME / EARTHDATA_PASSWORD in the environment (see .env.example)

Copernicus EMS reference extents are NOT checked here. Query the EMS activations API
for India by hand and record the result in docs/decisions.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
S1_COLLECTION = "sentinel-1-grd"
S2_COLLECTION = "sentinel-2-l2a"


def stac_counts(bbox, start, end):
    import planetary_computer
    import pystac_client

    catalog = pystac_client.Client.open(STAC_URL, modifier=planetary_computer.sign_inplace)
    dates = f"{start}/{end}"
    s1 = list(catalog.search(collections=[S1_COLLECTION], bbox=bbox, datetime=dates).items())
    s2 = list(catalog.search(collections=[S2_COLLECTION], bbox=bbox, datetime=dates).items())
    clouds = [i.properties.get("eo:cloud_cover") for i in s2]
    clouds = [c for c in clouds if c is not None]
    return len(s1), len(s2), (min(clouds) if clouds else None)


def altimetry_counts(bbox, start, end, swot_short_name):
    import earthaccess

    earthaccess.login(strategy="environment")
    window = (start, end)
    icesat2 = earthaccess.search_data(short_name="ATL13", bounding_box=tuple(bbox), temporal=window)
    swot = None
    if swot_short_name:
        swot = earthaccess.search_data(
            short_name=swot_short_name, bounding_box=tuple(bbox), temporal=window
        )
    return len(icesat2), (len(swot) if swot is not None else None)


def main(path: str = "configs/events.yaml") -> int:
    cfg = yaml.safe_load(Path(path).read_text())
    swot_name = cfg.get("swot_short_name")
    print(f"{'event':24} {'S1':>4} {'S2':>4} {'minCloud%':>10} {'ATL13':>6} {'SWOT':>6}")
    for ev in cfg.get("events", []):
        if not all(ev.get(k) for k in ("name", "bbox", "start", "end")):
            print("skipping incomplete event entry")
            continue
        try:
            n1, n2, cloud = stac_counts(ev["bbox"], ev["start"], ev["end"])
        except Exception as exc:  # report and continue; network or collection issues
            n1 = n2 = cloud = None
            print(f"  STAC error for {ev['name']}: {exc}")
        try:
            ice, swot = altimetry_counts(ev["bbox"], ev["start"], ev["end"], swot_name)
        except Exception as exc:
            ice = swot = None
            print(f"  Earthdata error for {ev['name']}: {exc}")
        print(f"{ev['name']:24} {n1!s:>4} {n2!s:>4} {cloud!s:>10} {ice!s:>6} {swot!s:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))
