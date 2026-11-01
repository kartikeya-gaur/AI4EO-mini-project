# Flood Mapping Agentic Workflow for India: Altimetry Cross-Checks and Shift-Aware Adaptation

> **Status:** In progress. Stage 1 (portfolio build) underway. Stage 2 (research) planned.

<!-- TODO: add 60-second demo video or live link here -->
<!-- TODO: add CI badge -->

A two-stage project on AI for Earth Observation.

- **Stage 1 (portfolio):** a multi-agent workflow (LangGraph, LangChain, RAG) that maps floods from Sentinel-1/2, cross-checks the result against satellite-altimetry water-surface height (ICESat-2, SWOT) where a pass exists, and returns a cited report with a **reliable / unreliable** flag. It refuses to answer when it has neither usable imagery nor any sources, omits claims it cannot source, and marks results as unverified when no altimetry pass is available.
- **Stage 2 (research):** measures how flood-mapping models degrade on Indian events and tests whether self-supervised features, contrastive alignment, and generative image translation recover the loss. Methods that help become agent tools.

## Contents

1. [Problem and impact](#problem-and-impact)
2. [Pipeline](#pipeline)
3. [Stage 1: portfolio build](#stage-1-portfolio-build-agentic-workflow-end-to-end)
4. [Stage 2: research](#stage-2-research)
5. [Limitations](#limitations)
6. [Repo structure](#repo-structure)
7. [Data and corpus](#data-and-corpus)
8. [References](#references)

---

## Problem and impact

After a flood, planners and relief analysts need to know *where the water was* and *how much to trust the map*. Optical imagery is often cloud-covered during floods, SAR is harder to interpret, and a confident but wrong mask can misdirect relief or underwrite the wrong risk.

This project gives an analyst a fast first look at a flood event with two things most flood-mapping demos lack:

1. **An independent physical check.** Altimetry gives the water-surface height along the river. If the mapped flood extent is inconsistent with that height, the agent downgrades its own reliability.
2. **Cited, uncertainty-aware reporting.** Every statement links to a retrieved source (NDMA, CWC/IMD, ReliefWeb) or a computed number.

Intended user: an analyst deciding which flood-affected districts to prioritise for ground verification. This is a screening tool, not an operational warning system.

## Pipeline

```
Open question
      |
      v
  Planner (supervisor) <------------------------------+
      |  plan                                          |
      +-----------------------+                        |
      v                       v                        |
  Imagery agent          Context agent                 |
  STAC, cloud check,     hybrid retrieval,             |
  SAR/optical choice,    rerank, filters               |
  segmenter, shift       |                             |
  score -> flood mask    |                             |
      |                  |                             |
      v                  |                             |
  Validation agent       |                             |
  altimetry + DEM check  |                             |
  -> reliability flag    |                             |
      |                  |                             |
      +----------+-------+                             |
                 v                                     |
            Writer agent                               |
  (every claim tagged to a tool result or chunk ID)    |
                 v                                     |
            Critic agent                               |
      reject: back to Writer to fix claims             |
      evidence missing: back to Planner ---------------+
                 | approve
                 v
  Cited, uncertainty-aware report with reliability flag
```

All numbers and masks come from deterministic tools. Agents plan, choose, judge, and write around them.

---

## Stage 1: portfolio build (agentic workflow, end to end)

**Goal:** a deployed, observable, evaluated agentic workflow with a real RAG layer, built on the current LangChain/LangGraph stack, around a pretrained segmenter treated as a black box. About 5 weeks part-time.

### Agents and what each one decides

Each agent owns one job and only its own tools. If an agent never makes a choice a fixed rule could make, it gets merged into a tool.

| Agent | Job | Tools (deterministic) | Decisions it makes |
|---|---|---|---|
| **Planner** | Turns an open question into a plan, decides when evidence is enough | Calls the other agents | Which events, dates, and agents are needed. Replan, or stop and answer. |
| **Imagery** | Gets a flood mask for the area and date | STAC search, cloud check, optical segmenter (Prithvi), SAR baseline, shift score | SAR vs. optical, how far to widen the date window, whether a doubtful mask needs a second scene |
| **Validation** | Decides how far to trust the mask | Altimetry lookup, DEM sampling, consistency check | Which altimetry product to try, whether a borderline mismatch is real or within DEM and datum error, the reliability flag with a stated reason |
| **Context** | Finds what official sources say | Hybrid retrieval, reranker, metadata filters | Rewrites weak queries, decides when "nothing found" is the honest answer |
| **Writer** | Drafts the report, every claim tagged to a tool result or chunk ID | None | What the evidence supports and what to omit |
| **Critic** | Checks the draft claim by claim | ID lookup, number matching, faithfulness check | Approve, or reject with specific objections |

**Baseline to beat:** a single agent holding all the tools. Compare tool-call accuracy, refusal behaviour, and report faithfulness. If the roster doesn't win, report that.

### Tech stack

Versions move quickly. Pin exact versions in `pyproject.toml` when you start and note them in `docs/decisions.md`.

| Layer | Choice | Notes |
|---|---|---|
| Orchestration | **LangGraph 1.x**: typed state (Pydantic), conditional edges, parallel branches, checkpointer | Persist state in SQLite or Postgres so runs can resume and be replayed |
| Agent layer | **LangChain 1.x** `create_agent` with middleware (retries, human-in-the-loop approval, summarisation) | LangChain agents run on the LangGraph runtime |
| Tools | Typed tool functions with Pydantic schemas | Optional stretch: expose the geospatial tools through an MCP server so any MCP client can call them |
| LLM | Provider-swappable (hosted API or local via Ollama) | Keep one config switch; log tokens and latency per agent |
| Embeddings | Open model (e.g., BGE family) or hosted API | Benchmark one of each on your own questions |
| Vector store | **Qdrant** (dense + sparse vectors, metadata filters) | Chroma is fine for local dev |
| Retrieval | Dense baseline, then hybrid (dense + BM25/sparse, fused), then cross-encoder reranker | Add each stage as an experiment and keep it only if recall@k or faithfulness improves |
| Observability and evals | **LangSmith** tracing, datasets, and experiments, plus RAGAS [6] | Langfuse is an open-source alternative |
| Serving | FastAPI with streaming, Streamlit UI showing the agent trace, Docker Compose (api, ui, qdrant) | Deploy to Cloud Run or Render |
| CI/CD | GitHub Actions: lint, unit tests, and an eval regression gate on the golden questions | A failing eval blocks the merge |

### RAG layer

1. **Ingest:** load NDMA, CWC/IMD, ReliefWeb, ISRO/NRSC, and Copernicus EMS documents, parse PDFs, and keep structure (headings, tables) where possible.
2. **Chunk with metadata:** source, document type, region, event, publication date, and a stable chunk ID. Test fixed-size vs. structure-aware chunking.
3. **Retrieve:** metadata filters first (region, date window), then hybrid search, then rerank.
4. **Evaluate retrieval separately from generation:** recall@k and MRR on questions with a known source passage, then faithfulness and relevance on the final answers.
5. **Treat retrieved text as data, not instructions.** Documents can contain text that tries to steer the model, so the Writer's prompt must keep retrieved passages clearly separated and the Critic must check claims against sources, not follow them.

### The altimetry consistency check

Within a reach, the water surface is roughly level at a given moment. So the terrain elevation along the edge of a correct flood mask should be close to the altimetry water-surface height measured nearby and around the same date.

- Sample a DEM (e.g., Copernicus GLO-30) along the mask boundary near the river.
- Compare to the altimetry height, with a tolerance covering DEM error and the time gap between the flood image and the altimetry pass.
- Large disagreement lowers the reliability flag. No pass available means the flag says "no altimetry evidence", not "reliable".

Datum care is part of the work: altimetry heights may be referenced to the ellipsoid or a geoid, and the DEM to another. Document this in `docs/decisions.md`.

### Claim types and citations

The agents never state a fact from memory. Every claim in a report is one of two types:

| Claim type | Example | Must cite |
|---|---|---|
| **Computed** | "About 412 km² appears flooded", "altimetry height is 38.2 m" | A tool result (imagery, mask, altimetry, DEM check) |
| **Contextual** | "The river crossed the danger level", "12,000 people evacuated" | A retrieved document from the corpus |

Rules:

1. Computed claims cite tool outputs. Contextual claims cite retrieved documents.
2. Contextual claims with no supporting source are omitted, and the report says none were found.
3. The Critic checks the draft before release: every cited ID exists, each cited passage supports its sentence, and each number matches the tool output it cites.
4. The system refuses only when it has neither usable imagery nor any sources.

**New event, no reports yet:** the report is computed-only, for example "about 412 km² of probable flooding on 17 Aug (unverified, no altimetry pass); no official reports found yet, so no damage or response information is included." This is a deliberate evaluation case.

Stage 1 runs on cached events, so it is not real time. A live mode would depend on satellite revisit times and on how quickly bulletins are published; check current latencies before stating any numbers.

### Showcase events

Cache 3-4 Indian events so the demo runs in seconds. Pick them in two groups, because altimetry coverage depends on the date:

| Group | Purpose | Date constraint | Candidates |
|---|---|---|---|
| **Altimetry-checked** (2-3 events) | Full pipeline, including the consistency check | After ICESat-2 launched (Sept 2018); after 21 July 2023 if you want SWOT | Assam or Bihar monsoon floods on wide rivers (Brahmaputra, Ganga, Kosi). |
| **Mask-only** (1 event) | Tests the "no altimetry evidence" path | Any date, including before the altimetry missions | Kerala 2018 (a Sentinel-1 and WorldView-3 mapping study exists) |

ICESat-2 inland-water coverage is limited to rivers roughly 100-200 m wide or more, so choose reaches on large rivers.

**Checks before committing to any event** (record results in `docs/decisions.md`):

1. Sentinel-1 and Sentinel-2 scenes exist on the flood dates, and Sentinel-2 is usable (not cloud-covered) if the optical model will be used.
2. A reference flood extent is available and its licence allows reuse. Query the Copernicus EMS public activations API for India. Also check whether NDMA's flood-affected area atlas or the Kerala 2018 study provide downloadable per-event masks. Fallback: the India chip in Sen1Floods11.
3. An ICESat-2 ATL13 or SWOT river pass exists near the flood reach and date (search with `earthaccess`).

### Segmenter

- **Optical:** use an official IBM/NASA Prithvi checkpoint fine-tuned on Sen1Floods11 from Hugging Face (Prithvi-EO-1.0-100M or Prithvi-EO-2.0-300M-TL), run through TerraTorch. These models take six Sentinel-2 bands and are used as a black box in Stage 1.
- **SAR:** the official checkpoints are optical only, and no ready-made SAR checkpoint has been confirmed. The Imagery agent's SAR tool starts as a deterministic baseline (change detection with Otsu thresholding). Before building it, run a dedicated Hugging Face search for a Sentinel-1 flood model; training a small U-Net on the Sen1Floods11 Sentinel-1 chips is the fallback.
- **Licence:** the model cards and third-party cards disagree (Apache 2.0 vs. MIT for Prithvi-EO-2.0), so read the LICENSE in the official repository and record it.
- **Report** published IoU vs. IoU measured on your own sample, per sensor.
- Third-party fine-tunes (for example an India lake model) are Stage 2 comparison points, not Stage 1 defaults.

### Checklist

**Deterministic tools (no LLM yet)**
- [ ] Event checks done (scenes, reference extent and licence, altimetry pass) and 3-4 events chosen
- [ ] Optical segmenter runs on a cached scene; record published vs. measured IoU and the licence
- [ ] SAR baseline tool (or a found checkpoint) running on a cached scene
- [ ] STAC search, cloud check, shift score as typed tools with unit tests
- [ ] Showcase events cached with reference extents
- [ ] Altimetry lookup and DEM consistency check working on at least one event

**RAG**
- [ ] Corpus collected, parsed, chunked with metadata, indexed in Qdrant
- [ ] Dense baseline, then hybrid, then reranker, each measured on recall@k and MRR
- [ ] 15-20 retrieval questions with known source passages

**Agents**
- [ ] LangGraph state schema, Planner, Imagery, and Context agents
- [ ] Writer and Critic with claim-ID tagging and the verification step
- [ ] Checkpointing and LangSmith tracing on every run
- [ ] Single-agent baseline built for comparison

**Evaluation**
- [ ] Eval set of 20-30 questions, including a "new event, no sources yet" case that expects a computed-only report
- [ ] Per-agent metrics (see results table) plus RAGAS faithfulness
- [ ] Critic test: inject unsupported claims into drafts and measure the catch rate
- [ ] Fix the failures the evals reveal

**Polish**
- [ ] Validation agent wired to the altimetry check, with an ablation: reliability-flag quality with vs. without it
- [ ] FastAPI, Streamlit with agent trace, Docker Compose, GitHub Actions with eval gate
- [ ] Deploy, record a 60-second demo, finish the architecture diagram and limitations
- [ ] `docs/decisions.md` cleaned up


**Done when:** an open question about a cached Indian flood event returns a mask, a reliability flag, and a cited report through the deployed app, every run is traced, and the results table below holds measured numbers.

### Stage 1 results

| Area | Metric | Value |
|---|---|---|
| Segmenter | IoU, published vs. measured on my sample (optical and SAR baseline reported separately) | TBD |
| Planner | Plan matches hand-labelled tool sequence | TBD |
| Imagery | Correct sensor and scene choice on known cases | TBD |
| Validation | Flag agreement with reference extents, without altimetry | TBD |
| Validation | Flag agreement with reference extents, with altimetry | TBD |
| Retrieval | Recall@k and MRR: dense, hybrid, hybrid + rerank | TBD |
| Writer | Faithfulness (RAGAS), correct omission of unsourced claims | TBD |
| Critic | Share of injected false claims caught | TBD |
| System | Correct-refusal rate | TBD |
| System | Multi-agent vs. single-agent baseline | TBD |
| Cost | Median latency and tokens per report (cached events) | TBD |

### Skills this project builds

| Skill | Where it shows up |
|---|---|
| Agent orchestration and state design | LangGraph graph, typed state, checkpointing, conditional loops |
| Production RAG | Chunking with metadata, hybrid retrieval, reranking, retrieval evals |
| Evaluation engineering | Golden questions, RAGAS, LangSmith experiments, eval gate in CI |
| LLM observability and cost control | Traces, per-agent tokens and latency |
| Safety and reliability | Claim verification, refusal behaviour, treating retrieved text as data |
| Deployment | FastAPI, Docker Compose, GitHub Actions, cloud hosting |
| Domain depth | Altimetry-based validation of satellite flood maps |

---

## Stage 2: research

**Starts after Stage 1 is deployed and evaluated.** Stage 1 treats the segmenter as a black box. Stage 2 opens it.

### Research question

How much do flood-mapping models degrade when moved from benchmark regions to Indian flood events, which adaptation techniques (DINO features, contrastive SAR-optical alignment, GAN and diffusion image translation) recover the most and at what cost, and can the agent use shift awareness to choose the right pipeline?

### Techniques

| Order | Technique | Role |
|---|---|---|
| 1 | **DINO [7] / DINOv2 [8] / DINOv3 [9]** (frozen, LoRA [10], optional continued pretraining) | Backbone comparison, label-efficiency curve, better shift detector |
| 2 | **Contrastive SAR-optical alignment** (SimCLR [11], SeCo [12], CROMA [13]) | Sensor-invariant features |
| 3 | **pix2pix [14], then CycleGAN [15] / CUT [16]** | Image-translation baselines (SAR to optical-like) |
| 4 | **Diffusion-based translation** (DDPM [17], latent diffusion [18], ControlNet-style conditioning [19], LoRA fine-tune) | Stretch method |

DINO is self-distillation rather than strictly contrastive, and is reported separately in the write-up.

**Cut order if time runs short:** diffusion first, then CycleGAN/CUT. DINO plus one contrastive method with a clean shift result is already a solid section.

### Shift experiments

| Shift | Setup |
|---|---|
| **Spatial** | Benchmark regions to Indian events (e.g., Assam, Bihar, Kerala 2018, Chennai 2015). Check how Sen1Floods11 [1] splits its events, since it may already include an India event, and design the held-out set carefully. |
| **Sensor** | Optical to SAR, and SAR translated to optical-like |
| **Temporal (optional)** | Different seasons or events within the same region |

Ground truth for Indian events is the hard part. Check Copernicus EMS and ISRO/NRSC inundation products early, and confirm licences.

### Shared evaluation for every method

- Flood IoU and boundary IoU, in-distribution and on Indian events
- Share of the shift-induced drop each method recovers
- Hallucination check on translated images (false or missing water near shorelines)
- Training time, inference time, and GPU memory
- End-to-end effect on the Stage 1 agent: reliability-flag agreement, tool-call accuracy, faithfulness

**Integration:** each method that works becomes an agent tool or routing option (SAR directly, translate then segment, or optical).

### Hypotheses (to test, not claims)

- Foundation-model features (DINO, Prithvi [3]) degrade less under shift than a supervised U-Net [2] trained from scratch.
- Translation helps mainly when optical imagery is cloud-obscured, and may hurt shoreline accuracy.
- A shift score built on DINO features flags unreliable predictions well enough to improve agent trustworthiness.
- The altimetry consistency check and the shift score catch different failures.

### Success criteria

- [ ] Reproduced baseline with a documented gap to the published number
- [ ] Shift results for every included method on one shared protocol
- [ ] At least one method integrated as an agent tool with measured end-to-end effect
- [ ] Short write-up including negative findings
- [ ] Public code, configs, and reproduction instructions

### Caveats from checking the sources

- DINOv3 includes satellite-pretrained weights (SAT-493M), but they were trained on Maxar RGB imagery at about 0.6 m resolution and are distributed under the DINOv3 License. That differs from 10 m multi-band Sentinel data, so test the fit before relying on them.
- CROMA already provides pretrained Sentinel-1/2 encoders, so use them directly before training your own alignment model.
- Prithvi-EO-2.0 was pretrained on Harmonized Landsat Sentinel-2 data at 30 m, and the weights are released with a permissive licence.

---

## Limitations

- Altimetry is sparse in space and time. Many flood scenes will have no usable pass, and the agent says so.
- Altimetry works best on wider rivers; narrow channels give noisy or missing returns.
- DEM error and datum differences limit how tight the consistency check can be.
- The official segmentation checkpoints are optical-only, so cloudy scenes rely on a simpler SAR baseline whose accuracy is lower and must be reported separately.
- Altimetry-based checks are only possible for events after ICESat-2 (Sept 2018) or SWOT (science orbit from July 2023) and on wide rivers. Earlier events such as Kerala 2018 are mask-only.
- In Stage 1 the segmenter is used as shipped and is not tuned for Indian conditions. Quantifying that is Stage 2.
- Reference flood extents for Indian events are limited, and reference products have their own errors.
- Multiple LLM-driven agents add latency, cost, and failure points, so the demo uses cached events and the single-agent baseline shows whether the extra agents are worth it.
- The Critic and the faithfulness metric are automated estimates and will miss some errors, which is why the hand-written eval set and injected-error tests matter.
- This is a screening tool and is not suitable for operational flood warning.

## Repo structure

```
data/          # gitignored, with download scripts
notebooks/     # exploration only
src/
  agents/      # planner, imagery, validation, context, writer, critic
  graph/       # LangGraph state schema, edges, checkpointing
  tools/       # stac, cloud check, segmenter, altimetry, dem consistency
  rag/         # ingest, chunking, indexing, retrieval, rerank
  shift/       # shift scores and detectors
  adaptation/  # Stage 2: dino, contrastive, translation
  eval/        # IoU, retrieval metrics, agent and RAG evals, injected-error tests
configs/
app/           # FastAPI + Streamlit
tests/
docker-compose.yml
.github/workflows/   # lint, tests, eval gate
docs/          # decisions.md (running log), results, figures
```

Keep `docs/decisions.md` as a running log of choices and negative results; it becomes the Stage 2 write-up. Commit small and often. Never commit data or keys.

## Data and corpus

Verify access and licences for everything below.

- **Imagery and labels:** Sen1Floods11, Sentinel-1/2 via STAC (Planetary Computer or Earth Engine)
- **Altimetry:** ICESat-2 ATL13 and SWOT river products via NASA Earthdata (free login; `earthaccess`). Check current product versions.
- **Reference flood extents:** Copernicus EMS Rapid Mapping (public activations API), NDMA flood-affected area atlas, published event studies (check licences)
- **DEM:** Copernicus GLO-30
- **Foundation models:** Prithvi-EO, DINO/DINOv2/DINOv3, CROMA encoders (check model zoo and licences)
- **Vector store and tracing:** Qdrant, LangSmith (or Langfuse); check free-tier limits
- **RAG corpus:** NDMA guidelines, IMD/CWC bulletins, ISRO/NRSC and Bhuvan reports, ReliefWeb situation reports, Copernicus EMS reports, SAR flood-mapping papers

## References

**Datasets and models**
1. Bonafilia, D., Tellman, B., Anderson, T., Issenberg, E. (2020). Sen1Floods11. *CVPR Workshops*, pp. 210-211. https://github.com/cloudtostreet/Sen1Floods11
2. Ronneberger, O., Fischer, P., Brox, T. (2015). U-Net. *MICCAI*. arXiv:1505.04597
3. Szwarcman, D., et al. (2024). Prithvi-EO-2.0. arXiv:2412.02732

**RAG, agents, evaluation**
4. Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*. arXiv:2005.11401
5. Yao, S., et al. (2023). ReAct. *ICLR*. arXiv:2210.03629
6. (v) Es, S., et al. (2024). RAGAs. *EACL 2024 System Demonstrations*, pp. 150-158.

**Self-supervised and contrastive representation learning**
7. Caron, M., et al. (2021). DINO. *ICCV*. arXiv:2104.14294
8. Oquab, M., et al. (2024). DINOv2. *TMLR*. arXiv:2304.07193
9. (v) Siméoni, O., et al. (2025). DINOv3. arXiv:2508.10104
10. Hu, E. J., et al. (2022). LoRA. *ICLR*. arXiv:2106.09685
11. Chen, T., et al. (2020). SimCLR. *ICML*. arXiv:2002.05709
12. Mañas, O., et al. (2021). SeCo. *ICCV*. arXiv:2103.16607
13. (v) Fuller, A., Millard, K., Green, J. R. (2023). CROMA. *NeurIPS 36*. arXiv:2311.00566

**Image translation and diffusion**
14. Isola, P., et al. (2017). pix2pix. *CVPR*. arXiv:1611.07004
15. Zhu, J.-Y., et al. (2017). CycleGAN. *ICCV*. arXiv:1703.10593
16. Park, T., et al. (2020). CUT. *ECCV*. arXiv:2007.15651
17. Ho, J., Jain, A., Abbeel, P. (2020). DDPM. *NeurIPS*. arXiv:2006.11239
18. Rombach, R., et al. (2022). Latent diffusion. *CVPR*. arXiv:2112.10752
19. Zhang, L., Rao, A., Agrawala, M. (2023). ControlNet. *ICCV*. arXiv:2302.05543

## License and citation

To be added.
