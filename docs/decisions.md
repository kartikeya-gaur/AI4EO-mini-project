# Decisions log

Running log of choices, checks, and negative results. It becomes the Stage 2 write-up.
Newest entries at the bottom. Record the source of every number you rely on.

## 2026-11-02: project and scope
- Building the Stage 1 flood agent described in the README.
- Open: the reservoir-monitoring idea is a separate project and is not started here.

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
