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

- [ ] Reproduce a published flood-segmentation baseline on Sen1Floods11 [1] (U-Net [2] and/or Prithvi-EO-2.0 [3]); record the reported vs. reproduced IoU
- [ ] Tools: STAC imagery search, cloud-cover check, run segmenter, simple shift score
- [ ] RAG pipeline [4]: chunking, embeddings, hybrid (BM25 + vector) search, reranking, region/date metadata filters
- [ ] Agent: tool-calling (LangGraph or similar; ReAct-style loop [5]) with a "reliable / unreliable" flag and cited summaries
- [ ] **Evaluation harness:** 30-50 hand-written questions on Indian flood events with known answers and sources; RAG metrics via RAGAs [6]
- [ ] FastAPI backend, Streamlit/Gradio UI, Dockerfile

**Done when:** a question about an Indian flood event returns a mask, a reliability flag, and a cited answer, with a measured evaluation score.

## Stage 2: representation learning and generative adaptation (about 6 weeks)

**Goal:** improve robustness under shift and quantify what each technique buys.

| Order | Technique | Role |
|---|---|---|
| 1 | **DINO** [7] / DINOv2 [8] / DINOv3 [9] (frozen, LoRA [10], optional continued pretraining) | Backbone comparison, label-efficiency curve, better shift detector |
| 2 | **Contrastive SAR-optical alignment** (SimCLR [11], SeCo [12], CROMA [13]) | Sensor-invariant features |
| 3 | **pix2pix [14], then CycleGAN [15] / CUT [16]** | Image-translation baselines |
| 4 | **Diffusion-based translation** (DDPM [17], latent diffusion [18], ControlNet-style conditioning [19], LoRA fine-tune) | Stretch method |

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

## References

Numbering follows first use above. Entries marked (v) were checked against the source while writing this README; the rest are from memory, so confirm venue and arXiv ID before citing them in the write-up.

**Datasets and models**

1. (v) Bonafilia, D., Tellman, B., Anderson, T., Issenberg, E. (2020). Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1. *CVPR Workshops*, pp. 210-211. Code and data: https://github.com/cloudtostreet/Sen1Floods11
2. Ronneberger, O., Fischer, P., Brox, T. (2015). U-Net: Convolutional networks for biomedical image segmentation. *MICCAI*. arXiv:1505.04597
3. (v) Szwarcman, D., Roy, S., Fraccaro, P., et al. (2024). Prithvi-EO-2.0: A versatile multi-temporal foundation model for Earth observation applications. arXiv:2412.02732. Model: https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-2.0 (TerraTorch: https://github.com/IBM/terratorch)

**RAG, agents, evaluation**

4. Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*. arXiv:2005.11401
5. Yao, S., et al. (2023). ReAct: Synergizing reasoning and acting in language models. *ICLR*. arXiv:2210.03629
6. (v) Es, S., James, J., Espinosa Anke, L., Schockaert, S. (2024). RAGAs: Automated evaluation of retrieval augmented generation. *EACL 2024 System Demonstrations*, pp. 150-158. https://aclanthology.org/2024.eacl-demo.16

**Self-supervised and contrastive representation learning**

7. Caron, M., et al. (2021). Emerging properties in self-supervised vision transformers (DINO). *ICCV*. arXiv:2104.14294
8. Oquab, M., et al. (2024). DINOv2: Learning robust visual features without supervision. *TMLR*. arXiv:2304.07193
9. (v) Siméoni, O., et al. (2025). DINOv3. arXiv:2508.10104. Code: https://github.com/facebookresearch/dinov3
10. Hu, E. J., et al. (2022). LoRA: Low-rank adaptation of large language models. *ICLR*. arXiv:2106.09685
11. Chen, T., et al. (2020). A simple framework for contrastive learning of visual representations (SimCLR). *ICML*. arXiv:2002.05709
12. Mañas, O., et al. (2021). Seasonal contrast: Unsupervised pre-training from uncurated remote sensing data (SeCo). *ICCV*. arXiv:2103.16607
13. (v) Fuller, A., Millard, K., Green, J. R. (2023). CROMA: Remote sensing representations with contrastive radar-optical masked autoencoders. *NeurIPS 36*. arXiv:2311.00566

**Image translation and diffusion**

14. Isola, P., Zhu, J.-Y., Zhou, T., Efros, A. A. (2017). Image-to-image translation with conditional adversarial networks (pix2pix). *CVPR*. arXiv:1611.07004
15. Zhu, J.-Y., Park, T., Isola, P., Efros, A. A. (2017). Unpaired image-to-image translation using cycle-consistent adversarial networks (CycleGAN). *ICCV*. arXiv:1703.10593
16. Park, T., Efros, A. A., Zhang, R., Zhu, J.-Y. (2020). Contrastive learning for unpaired image-to-image translation (CUT). *ECCV*. arXiv:2007.15651
17. Ho, J., Jain, A., Abbeel, P. (2020). Denoising diffusion probabilistic models. *NeurIPS*. arXiv:2006.11239
18. Rombach, R., et al. (2022). High-resolution image synthesis with latent diffusion models. *CVPR*. arXiv:2112.10752
19. Zhang, L., Rao, A., Agrawala, M. (2023). Adding conditional control to text-to-image diffusion models (ControlNet). *ICCV*. arXiv:2302.05543

**Caveats from checking the sources**

- DINOv3 includes satellite-pretrained weights (SAT-493M), but they were trained on Maxar RGB imagery at about 0.6 m resolution, and the weights are distributed under the DINOv3 License. That differs from 10 m multi-band Sentinel data, so test the fit before relying on them.
- CROMA already provides pretrained Sentinel-1/2 encoders, so you can use them directly rather than training your own alignment model first.
- Prithvi-EO-2.0 was pretrained on Harmonized Landsat Sentinel-2 data at 30 m, and the weights are released with a permissive licence.

## License and citation

To be added.
