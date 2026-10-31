# AI4EO: Shift-Aware Reservoir Monitoring and Forecasting Agent

> **Status:** In progress. Planning and data pipeline setup.

A side project on AI for Earth Observation: an end-to-end system that monitors Indian reservoirs from satellite data, forecasts their storage, and explains the results through a RAG-based agent. The central question is how well these models **transfer across hydroclimatic regions, years, and sensors**.

## Research question

> How well do water-monitoring and forecasting models trained on one Indian hydroclimatic region transfer to others, and can an agent that detects domain shift and retrieves context make the system more reliable?

## Pipeline

```
Sentinel-1/2 imagery -> water segmentation -> surface-area time series
                                                    |
        altimetry (ICESat-2 / SWOT) + rainfall ---> forecasting ladder
                                                    |
              shift detector -> RAG agent (CWC/IMD reports) -> cited, uncertainty-aware report
```

## Objectives

1. **Vision:** build a water-body segmentation model (Sentinel-1/2) that produces reservoir surface-area time series.
2. **Forecasting:** compare a ladder of forecasters: seasonal naive, SARIMA/ETS, LightGBM, deep models (LSTM/TFT), and foundation models (Chronos, TimesFM).
3. **Domain shift:** quantify performance drops across basins, years, and sensors, then test adaptation methods.
4. **RAG agent:** build a tool-calling agent that retrieves CWC/IMD documents, runs the models, flags unreliable predictions under shift, and writes cited reports.
5. **Deployment:** serve with FastAPI and a simple UI, reproducible via Docker.

## Shift experiments

| Shift type | Setup |
|---|---|
| **Spatial (basin)** | Train on Cauvery + Krishna, test on Godavari/Mahanadi (mild shift), then Himalayan reservoirs such as Bhakra and Tehri (strong shift) |
| **Temporal** | Train on normal monsoon years, test on a deficit year (verify rainfall departures first) |
| **Sensor / mission** | Sentinel-2 to Sentinel-1; ICESat-2 to SWOT |

Starting reservoirs: KRS, Kabini, Hemavathi (Cauvery).

## Learning goals

- Fine-tune a geospatial foundation model (LoRA/PEFT)
- Build and evaluate RAG (hybrid search, reranking, faithfulness metrics)
- Build tool-using agents (e.g., LangGraph)
- Rigorous time-series backtesting and uncertainty calibration
- Ship a complete system, not just notebooks

## Success criteria

- [ ] Working pipeline from imagery to forecast to agent report
- [ ] Rolling-origin backtests with prediction intervals for every forecaster
- [ ] Measured shift results for basin, temporal, and sensor shifts
- [ ] Public demo (live or recorded) and Docker setup
- [ ] Short write-up including negative findings

Hypotheses to test, not claims: for example, whether foundation models degrade less than SARIMA under Himalayan shift, and whether an agent-based reliability check improves trust in forecasts.

## Scope

The core deliverable is the **pipeline plus the shift evaluation**. The agent and additional adaptation methods are layered on top, so the project still yields a solid benchmark if time runs short.

## Roadmap

- [ ] **Weeks 1-2:** data pipeline (Earth Engine/STAC), NDWI baseline mask, first area series
- [ ] **Weeks 3-4:** forecasting ladder and backtesting
- [ ] **Weeks 5-6:** domain shift experiments and adaptation
- [ ] **Weeks 7-8:** RAG corpus and agent with tools
- [ ] **Weeks 9-10:** evaluation, UI, deployment, write-up

## Planned data sources

- **Imagery:** Sentinel-1/2 (Earth Engine or Planetary Computer)
- **Reservoir storage/levels:** India-WRIS, CWC weekly bulletins (check terms of use)
- **Reservoir geometry:** GRanD, GeoDAR, Global Surface Water
- **Altimetry:** ICESat-2, SWOT, Sentinel-3
- **Covariates:** CHIRPS/IMD rainfall, ERA5, MODIS snow cover (Himalayan targets)

## Repo structure (planned)

```
data/          # gitignored, with download scripts
notebooks/     # exploration only
src/           # segmentation, timeseries, shift, rag, agent
configs/
app/           # FastAPI + Streamlit
docs/          # results, figures, decisions log
```

## License and citation

To be added.
