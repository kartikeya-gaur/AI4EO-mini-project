# Decisions log

Running log of choices, checks, and negative results. It becomes the Stage 2 write-up.
Newest entries at the bottom. Record the source of every number you rely on.

## 2026-11-02: project and scope
- Building the Stage 1 flood agent described in the README.
- Open: the reservoir-monitoring idea is a separate project and is not started here.

## 2026-11-15: cleanup and findings carried in
- Removed the hidden defaults for `k` and `min_points` in `altimetry_consistency`. Both change the
  verdict, so they are now required arguments and must be logged below with a source or reason.
  A test (`test_no_default_for_k_or_min_points`) enforces this.
- README intro now names the three flag values (reliable / unreliable / unverified), matching `schemas.Flag`.
- `scripts/check_events.py`: the two broad `except Exception` blocks are kept on purpose (one-off
  script, report and continue) and marked `noqa: BLE001`.
- Findings from earlier reading, carried in from the project brief. Not yet re-verified in this repo;
  add the source link when each is checked:
  - Official Prithvi flood checkpoints are optical-only; SAR needs a baseline or another model.
  - Kerala 2018 and Chennai 2015 predate ICESat-2 and SWOT, so they are mask-only events.
  - Reference flood extents per event are unconfirmed.

## 2026-11-15: web checks (segmenter, SAR, reference extents)
Method: web search plus reading pages. Nothing was run or measured. A mirror page is marked as such.

**Prithvi flood checkpoints**
- Both flood cards (2.0-300M-TL-Sen1Floods11, 1.0-100M-sen1floods11) list six Sentinel-2 bands:
  Blue, Green, Red, Narrow NIR, SWIR 1, SWIR 2. So the optical-only finding is now verified for these two.
- Training data per the cards: Sen1Floods11, 446 labelled 512x512 chips, 11 flood events. Split sizes are not on the cards.
- Licence conflict and the IoU numbers are in the Segmenter table above.

**SAR candidates seen (none adopted)**
- `ibm-esa-geospatial/TerraMind-base-Flood` (read via a mirror page, not the original): Apache-2.0 per the page.
  Its usage example takes Sentinel-2 L2A, Sentinel-1 RTC (VV, VH) and a DEM, 4 timesteps, so it is not SAR-only.
  Trained on ImpactMesh-Flood. No metrics on the page. A third-party reproduction (`msradam/...`, "not affiliated")
  measured water IoU 0.3832 for the IBM model and 0.3753 for its own on the ImpactMesh test split. Those are low.
- `ibm-granite/granite-geospatial-uki-flooddetection`: Apache-2.0. Inputs Sentinel-2 (six bands), Sentinel-1 VV/VH
  and a cloud mask. Trained for the UK and Ireland on 69 images from 6 events. No metrics reported.
  Not a fit for India without fine-tuning.
- arXiv:2512.02055 fine-tunes TerraMind on FloodsNet (S1 + S2). The abstract gives no weights link. Not checked further.
- Caution for evaluation: ImpactMesh-Flood labels come from Copernicus EMS, so a model trained on it may have seen
  EMS reference extents. Check overlap before using EMS products as ground truth for such a model.

**Reference extents**
- ImpactMesh: dataset licence CC-BY 4.0, labels from Copernicus EMS, "over 400 events". Whether India is included: not confirmed.
- EMS API documented at `https://rapidmapping.emergency.copernicus.eu/backend/dashboard-api/public-activations-info/`
  (JSON: code, name, countries, category, closed, n_products). Details per activation:
  `.../public-activations/?code={code}`. No country filter is documented, so filter on `countries` client-side.
  Licence, auth and rate limits are not stated on the harvest page. I could NOT fetch the API from here (not on the
  tool allowlist), so the India activation list is still missing. To do on your machine: page through the
  list and keep rows where `countries` includes India.
- India activations I found by search, both useless for this project:
  - EMSR040, Assam flood, activated 2013-04-29: reference maps only, no flood extent listed. Predates Sentinel-1.
  - EMSR049, Uttarakhand flood, activated 2013-06-27: reference maps only, no delineation listed. Predates Sentinel-1.
- Licence: the JRC catalogue entry for EMSR040 says reuse is authorised if the source is acknowledged (EC reuse notice).
  The EMS activation pages themselves state no licence. Treat licence as unconfirmed for newer products.
- Candidate event, not an EMS activation: International Charter activation 907, floods on the Krishna River
  (Vijayawada, Khammam), activated 2024-09-03, nine products listed, no usage licence stated on the page.
  Not checked: Sentinel scenes, altimetry coverage on this reach.
- Sen1Floods11: the GitHub page does not list the events or say whether India is one, and states no licence.
  The event list is in `Sen1Floods11_Metadata.geojson`. Check it before designing the Stage 2 held-out set.

## Open checks (fill in as they are done)

### Segmenter
| Item | Result | Source / date |
|---|---|---|
| Licence of the Prithvi-EO checkpoint used (README says sources disagree) | UNRESOLVED. Hugging Face metadata says Apache-2.0 for `Prithvi-EO-2.0-300M-TL-Sen1Floods11` and `Prithvi-EO-1.0-100M-sen1floods11`. The `Prithvi-EO-2.0-300M-TL` file list has no LICENSE file. The GitHub repo `NASA-IMPACT/Prithvi-EO-2.0` shows MIT, but I only saw that on a mirror page and did not read the LICENSE text. | HF cards, 2026-11-15. Still TODO: open the LICENSE on github.com directly |
| Published IoU for that checkpoint | Checkpoint not chosen yet. 2.0-300M-TL: water IoU 82.6 (std 0.3), mIoU 90.0, test set, 10 seeds. 1.0-100M: paper says water IoU 79.6 (std 0.5), but its HF card says 80.46 (test) and 77.95 (Bolivia holdout). The two 1.0-100M numbers differ, so the protocols differ. The 2.0-300M-TL-Sen1Floods11 HF card reports no IoU. | arXiv:2412.02732 Table IV; HF cards; 2026-11-15 |
| IoU measured on my sample | TODO | |
| SAR approach (found checkpoint / Otsu baseline / small U-Net) | No ready SAR-only flood checkpoint confirmed. Both Prithvi flood cards take six Sentinel-2 bands (optical only). Candidates seen are in the 2026-11-15 entry below. Plan stays: Otsu baseline first. | HF search, 2026-11-15 (not exhaustive) |

### Uncertainty parameters for the altimetry check (no defaults in code)
| Parameter | Value | Source |
|---|---|---|
| DEM vertical sigma (m) | TODO | DEM product spec |
| Altimetry sigma (m) | TODO | product spec |
| Datum offset DEM -> altimetry datum (m) | TODO | geoid/ellipsoid computation |
| Max pass gap (days) | TODO | |
| Stage change rate (m/day) | TODO | gauge data or literature |
| Coverage factor `k` on the tolerance | TODO | choose by experiment against reference extents; record why |
| Min valid boundary samples (`min_points`) | TODO | depends on boundary length at a real reach; record why |
| Shift-score threshold (`shift_threshold`, policy.py) | TODO | depends on the shift score; set after the score exists |
| Number-match tolerance (`rel_tol`, verify.py) | TODO | depends on tool output precision and rounding in reports |

### Events
| Event | Sentinel-1 | Sentinel-2 usable | Reference extent + licence | ICESat-2 pass | SWOT pass | Group |
|---|---|---|---|---|---|---|
| TODO | | | | | | altimetry-checked / mask-only |

Also record here: Copernicus EMS API query for India, NDMA atlas per-event masks (yes/no).
Status on 2026-11-15: full India list from the EMS API NOT obtained (see entry below). NDMA atlas not checked.

### RAG choices (record after the first retrieval evals)
| Item | Value | Why |
|---|---|---|
| Embedding model name and dimension | TODO | Embeddings from different models are not comparable; put the name in the collection name |
| Chunk size / overlap | TODO | Chosen by recall@k and MRR on the retrieval questions, not by default |
| Retrieval variant kept (dense / hybrid / hybrid + rerank) | TODO | Keep a stage only if it improves recall@k or faithfulness |
| Query transformation kept (none / rewrite / multi-query + RRF / HyDE) | TODO | Same rule: measure against the untransformed query |
| RRF constant k | TODO | Tune on the retrieval questions |

### Dependency versions
Pin exact versions after the first working install: TODO.
