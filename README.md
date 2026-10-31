# AI4EO: Shift-Aware Flood Mapping Agent for India

> **Status:** In progress. Planning and Stage 1 setup.

A side project on AI for Earth Observation. Stage 1 builds an end-to-end agent (RAG, tool calling, evaluation) that maps floods from Sentinel-1/2 and explains the result with cited sources. Stage 2 improves the segmenter's robustness under domain shift using representation learning and generative adaptation, and measures whether each technique actually helps.

## Research question

> How much do flood-mapping models degrade when moved from benchmark regions to Indian flood events, and which adaptation techniques (DINO features, contrastive alignment, image translation) recover the most, at what cost, and can an agent use shift awareness to choose the right pipeline?

## Pipeline

```
Query (area, date) -> STAC search -> cloud check -> choose SAR or optical
                                                      |
              segmenter (+ Stage 2 adaptation) -> flood mask
                                                      |
        shift score -> reliability flag -> RAG (NDMA/IMD/CWC/ReliefWeb)
                                                      |
                          cited, uncertainty-aware flood report
```

## Stage 1: RAG, agents, and evaluation (about 5 weeks)

**Goal:** a working, demo-ready agent built around a baseline segmenter treated as a black box.

- [ ] Reproduce a published flood-segmentation baseline on Sen1Floods11 (U-Net and/or Prithvi); record the reported vs. reproduced IoU
- [ ] Tools: STAC imagery search, cloud-cover check, run segmenter, simple shift score
- [ ] RAG pipeline: chunking, embeddings, hybrid (BM25 + vector) search, reranking, region/date metadata filters
- [ ] Agent: tool-calling (LangGraph or similar) with a "reliable / unreliable" flag and cited summaries
- [ ] **Evaluation harness:** 30-50 hand-written questions on Indian flood events with known answers and sources
- [ ] FastAPI backend, Streamlit/Gradio UI, Dockerfile

**Done when:** a question about an Indian flood event returns a mask, a reliability flag, and a cited answer, with a measured evaluation score.

## Stage 2: representation learning and generative adaptation (about 6 weeks)

**Goal:** improve robustness under shift and quantify what each technique buys.

| Order | Technique | Role |
|---|---|---|
| 1 | **DINO** (frozen, LoRA, optional continued pretraining) | Backbone comparison, label-efficiency curve, better shift detector |
| 2 | **Contrastive SAR-optical alignment** | Sensor-invariant features |
| 3 | **pix2pix, then CycleGAN / CUT** | Image-translation baselines |
| 4 | **Diffusion-based translation** (LoRA fine-tune of a pretrained model) | Stretch method |

DINO is self-distillation rather than strictly contrastive; it is reported separately in the write-up.

**Shared evaluation for every method**
- Flood IoU and boundary IoU, in-distribution and on Indian events
- Share of the shift-induced drop each method recovers
- Hallucination check on translated images (false or missing water near shorelines)
- Training time, inference time, and GPU memory

**Integration:** each method that works becomes an agent tool or routing option (SAR directly, translate then segment, or optical), and the Stage 1 harness measures its effect on end-to-end agent quality.

**Cut order if time runs short:** diffusion first, then CycleGAN/CUT. DINO plus one contrastive method with a clean shift result is already a solid section.

## Shift experiments

| Shift | Setup |
|---|---|
| **Spatial** | Benchmark regions to Indian events (e.g., Assam, Bihar, Kerala 2018, Chennai 2015) |
| **Sensor** | Optical to SAR, and SAR translated to optical-like |
| **Temporal (optional)** | Different seasons or events within the same region |

Ground truth for Indian events is the hard part. Check Copernicus EMS and ISRO/NRSC inundation products early, and confirm licences.

## Hypotheses (to test, not claims)

- Foundation-model features (DINO/Prithvi) degrade less under shift than a supervised U-Net trained from scratch.
- Translation helps mainly when optical imagery is cloud-obscured, and may hurt shoreline accuracy.
- A shift score can flag unreliable predictions well enough to improve agent trustworthiness.

## Success criteria

- [ ] Reproduced baseline with a documented gap to the published number
- [ ] Working agent with measured RAG faithfulness, tool-call accuracy, and correct refusal rate
- [ ] Shift results for every Stage 2 method on a shared protocol
- [ ] Public demo (live or recorded) and Docker setup
- [ ] Short write-up including negative findings

## Planned data and corpus (verify access and licences)

- **Imagery and labels:** Sen1Floods11, Sentinel-1/2 via STAC (Planetary Computer or Earth Engine)
- **Foundation models:** Prithvi-EO, DINO/DINOv2/DINOv3 variants (check current model zoo and licences)
- **RAG corpus:** NDMA guidelines, IMD/CWC bulletins, ISRO/NRSC and Bhuvan reports, ReliefWeb situation reports, Copernicus EMS reports, SAR flood-mapping papers

## Repo structure (planned)

```
data/          # gitignored, with download scripts
notebooks/     # exploration only
src/
  segmentation/
  adaptation/  # dino, contrastive, translation
  shift/       # shift scores and detectors
  rag/
  agent/
  eval/        # IoU, boundary IoU, RAG and agent metrics
configs/
app/           # FastAPI + Streamlit
docs/          # results, figures, decisions log
```

## Working notes

Keep `docs/decisions.md` as a running log of choices and negative results; it becomes the write-up. Commit small and often, never commit data or keys.

## License and citation

To be added.
