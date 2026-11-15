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

## Open checks (fill in as they are done)

### Segmenter
| Item | Result | Source / date |
|---|---|---|
| Licence of the Prithvi-EO checkpoint used (README says sources disagree) | TODO | official repo LICENSE file |
| Published IoU for that checkpoint | TODO | model card |
| IoU measured on my sample | TODO | |
| SAR approach (found checkpoint / Otsu baseline / small U-Net) | TODO | Hugging Face search |

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
