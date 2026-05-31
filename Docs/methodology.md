# KiranaChain v1.0.0 — Methodology

### Technical Specification of the Data Generation, Simulation, Validation, and Release Pipeline

![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)
![Release](https://img.shields.io/badge/Release-May_2026-green?style=for-the-badge)
![Rows](https://img.shields.io/badge/Rows-1M-orange?style=for-the-badge)
![Trajectories](https://img.shields.io/badge/Trajectories-125K-purple?style=for-the-badge)
![Features](https://img.shields.io/badge/Features-40-red?style=for-the-badge)
![Methodology](https://img.shields.io/badge/Pipeline-Procedural_Simulation-darkgreen?style=for-the-badge)

---

## Document Purpose

This document provides a comprehensive technical description of the KiranaChain v1.0 data-generation pipeline, including simulation design, probabilistic modeling assumptions, trajectory construction procedures, validation protocols, and reproducibility specifications.

The objective of this document is to enable complete transparency, reproducibility, and scientific interpretability of the dataset generation process.

---

## Pipeline Architecture Overview

KiranaChain is generated through a twelve-stage procedural simulation pipeline designed to emulate negotiation behavior within India's informal retail supply ecosystem.

### Generation Workflow

```text
Agent Instantiation
        ↓
Financial Copula Generation
        ↓
Environmental Copula Generation
        ↓
Price Initialization
        ↓
Markov Negotiation Engine
        ↓
Price Concession Walk
        ↓
Gaussian Process Noise Injection
        ↓
Behavioral Posture Assignment
        ↓
Dialogue Generation
        ↓
Sentiment Modeling
        ↓
Parquet Streaming Output
        ↓
Validation & Quality Assurance
```
---
## Notation

| Symbol | Meaning |
|----------|----------|
| τ | Kirana Historical Trust Score |
| σ | Kirana Liquidity Stress Index |
| Σ_fin | Financial Correlation Matrix |
| Σ_env | Environmental Correlation Matrix |
| Φ | Standard Normal CDF |
| GP | Gaussian Process |
| PSD | Positive Semi-Definite |

---
### Release Statistics

| Metric               |                      Value |
| -------------------- | -------------------------: |
| Total Rows           |                  1,000,000 |
| Total Trajectories   |                    125,000 |
| Turns per Trajectory |                          8 |
| Total Features       |                         40 |
| Output Format        |             Apache Parquet |
| Compression          |                     Snappy |
| Dataset Size         |                    ~156 MB |
| Runtime              |               ~128 Seconds |
| Generation Strategy  | Chunked Streaming Pipeline |
| Number of Chunks     |                         20 |
| Rows per Chunk       |                     50,000 |

---

## Computational Characteristics

| Property | Value |
|----------|--------|
| Generation Runtime | ~128 seconds |
| Dataset Size | ~156 MB |
| Peak Memory Usage | ~1.2 GB |
| Generation Mode | Chunked Streaming |
| Parallelism | Single Process |
| Output Format | Apache Parquet |

---

## Stage 1 — Agent Instantiation

**Objective:** Define the population of distributor and Kirana agents for each chunk.

The dataset is generated in 20 chunks of 50,000 rows each (6,250 trajectories per chunk × 8 turns). For each chunk:

- A unique `numpy.random.default_rng` instance is seeded deterministically: `seed = chunk_idx × 9973 + 17`. This ensures full reproducibility while preventing cross-chunk correlation artifacts.
- **Distributor agents** are assigned pseudonymous 4-digit IDs (`DIST_XXXX`), sampled uniformly from the range 1000–9999.
- **Kirana agents** are assigned pseudonymous 5-digit IDs (`KIR_XXXXX`), sampled uniformly from 10000–99999.
- **Geographic tier** is assigned from the distribution: Tier-3 Semi-Urban 35%, Tier-2 Urban 30%, Rural Village 20%, Tier-1 Metro 15%.
- **State context** is sampled uniformly from 12 Indian states.
- **Commodity type** is assigned from: Staple Grains 30%, Packaged FMCG 20%, Edible Oils 20%, Spices 15%, Dairy 15%.

All agent-level attributes are assigned once per trajectory and repeated across all 8 turn-rows to reflect the invariance of agent identity within a single negotiation episode.

---

## Stage 2 — Financial Block Generation via Gaussian Copula

**Objective:** Generate 10 correlated financial variables that reflect realistic Udhar credit dynamics.

A 10×10 structured correlation matrix **Σ_fin** is defined with theoretically grounded inter-variable Pearson correlations:

| Pair | ρ | Rationale |
|------|---|-----------|
| trust_score ↔ credit_limit | +0.82 | Credit allocation tracks repayment track record |
| trust_score ↔ liquidity_stress | −0.73 | Financially stressed agents accumulate lower trust |
| trust_score ↔ default_risk | −0.78 | High-trust agents pose low default probability |
| liquidity_stress ↔ default_risk | +0.85 | Cash crunch is the primary default precursor |
| default_risk ↔ interest_rate | +0.72 | Informal interest priced as a risk premium |
| outstanding_udhar ↔ liquidity_stress | +0.69 | Debt accumulation amplifies cash pressure |
| outstanding_udhar ↔ repayment_velocity | +0.58 | Slow payers carry larger balances |

The matrix is projected to the nearest Positive Semi-Definite (PSD) matrix via eigenvalue clamping, then Cholesky-decomposed: **L_fin = chol(Σ_fin)**.

For each chunk of `n_traj` trajectories:
1. Draw `Z ~ N(0, I)` of shape `(n_traj, 10)`.
2. Apply Cholesky: `Z_corr = (L_fin @ Z.T).T`.
3. Apply standard normal CDF: `U = Φ(Z_corr)` — yields uniform marginals with the target correlation structure.
4. Apply inverse CDFs to transform to target marginal distributions:
   - `trust_score` → `Beta.ppf(U[:,0], a=2.5, b=1.8)` (right-skewed)
   - `credit_limit` → linear function of trust + `Gamma.ppf(U[:,1], a=2, scale=15000)` + offset
   - `outstanding_udhar` → fraction of credit limit conditioned on `U[:,2]`
   - `liquidity_stress` → `Beta.ppf(U[:,4], a=1.8, b=2.5)`
   - `default_risk` → explicit weighted formula with measurement noise
   - `interest_rate` → monotone function of default_risk and trust

All financial variables are computed once per trajectory and broadcast to all 8 turn-rows.

---

## Stage 3 — Environmental Block Generation via Gaussian Copula

**Objective:** Generate 10 correlated environmental and supply chain externality variables.

An analogous 10×10 correlation matrix **Σ_env** captures physical causal dependencies:

| Pair | ρ | Rationale |
|------|---|-----------|
| monsoon_index ↔ perishability | +0.66 | High humidity accelerates decay |
| ambient_temp ↔ perishability | +0.71 | Temperature is primary decay driver |
| fuel_volatility ↔ bottleneck | +0.61 | Supply disruptions drive fuel price spikes |
| mandi_shock ↔ local_inflation | +0.57 | Supply compression transmits to retail prices |
| festival_proximity ↔ mandi_shock | −0.38 | Pre-festival stockpiling increases arrivals |

The same Cholesky copula procedure as Stage 2 is applied. Marginal distributions:
- `monsoon_disruption_index` → `Beta(1.5, 3.0)` — right-skewed, most observations low
- `festival_proximity_coefficient` → linear transform of `U[:,1]` to integer range 1–365
- `perishability_decay_rate` → `Beta(2.0, 2.5)` — approximately symmetric
- `fuel_price_volatility_delta` → `TruncatedNormal(0, 3.5, a=−2, b=2)` clipped to [−8, +10]
- `mandi_arrival_volume_shocks` → `TruncatedNormal(0, 0.18)` clipped to [−0.40, +0.40]
- `ambient_warehouse_temperature` → linear transform to [18°C, 42°C]
- `competitor_density_radius` → Uniform(0,15) + Poisson(λ=3), clipped to [0, 20]

---

## Stage 4 — Price Path Initialisation

**Objective:** Set realistic opening ask and counter-offer prices per trajectory.

For each trajectory:

1. **Base price** is drawn uniformly from the commodity-specific INR range, then modulated:
   - Festival effect: `×(1 + 0.10 × max(0, (60 − festival_days)/60))` — prices spike close to festivals
   - Monsoon effect: `×(1 + 0.08 × monsoon_index)` — logistics stress inflates prices

2. **Distributor ask** = `base_price × (1 + margin_floor + Uniform(0.02, 0.08))` — margin floor plus stochastic upward bias

3. **Kirana counter-offer** = `dist_ask × Uniform(0.70, 0.88) × (1 − 0.10 × liquidity_stress)` — aggressive discount further reduced by cash-crunch state

---

## Stage 5 — Non-Stationary Markov Negotiation State Machine

**Objective:** Simulate realistic negotiation resolution dynamics across 8 turns.

The negotiation state space is **S = {0: In-Progress, 1: Settled, 2: Walked-Away, 3: Credit-Denied}**. Terminal states are absorbing.

At each turn `t`, for In-Progress trajectories, the transition vector is computed as:

```
P(Settled | t, τ, σ)      = min(0.08 + 0.09t + 0.12τ, 0.72)
P(Walked-Away | t, σ)      = min(0.03 + 0.06(t/8) + 0.15σ, 0.35)
P(Credit-Denied | σ)       = min(0.01 + 0.08×max(0, σ−0.5), 0.20)
P(In-Progress)             = max(1 − above, 0.05)
```

where τ = `kirana_historical_trust_score` and σ = `kirana_liquidity_stress_index`.

At turn 8, any remaining In-Progress trajectory is forced to terminal resolution: Settled 55%, Walked-Away 30%, Credit-Denied 15%.

**Non-stationarity** is encoded by the turn-index terms: settlement probability increases linearly with turn, walk-away probability escalates with both turn and stress, credit denial is stress-gated with a 0.5 threshold.

---

## Stage 6 — Price Concession Walk

**Objective:** Model realistic convergence of ask and bid prices over turns.

At each turn, both sides make a fractional concession toward the midpoint:

```
concession_distributor = (ask_walk − bid_walk) × Uniform(0.05, 0.18)
concession_kirana      = (ask_walk − bid_walk) × Uniform(0.06, 0.20)
ask_walk  -= concession_distributor    (floored at 88% of original ask)
bid_walk  += concession_kirana         (capped at 102% of original ask)
current_offer = (ask_walk + bid_walk) / 2 + GP_noise[turn]
```

The asymmetric concession ranges (Kirana concedes slightly faster) encode the mild power asymmetry of distributor-over-retailer in Indian informal trade. The GP noise term (Stage 7) adds realistic turn-to-turn price path irregularity.

---

## Stage 7 — Gaussian Process Noise Injection

**Objective:** Reproduce human irrationality, measurement error, and unobserved micro-market friction.

For each trajectory, an 8-dimensional noise vector is sampled from a zero-mean Gaussian Process with squared-exponential kernel:

```
k(tᵢ, tⱼ) = exp(−‖tᵢ − tⱼ‖² / (2 × 5.0²))
```

The kernel matrix `K` (8×8) is Cholesky-decomposed and multiplied by a standard Normal draw, then scaled by 0.12. This temporal correlation structure ensures noise artifacts exhibit within-episode autocorrelation consistent with real human decision sequences, rather than i.i.d. white noise.

The GP sample serves dual purpose: added to `current_turn_offer_price` as a price path perturbation, and stored directly as `statistical_noise_artifact`.

---

## Stage 8 — Posture Classification

**Objective:** Assign a categorical negotiation posture to each turn conditioned on agent state.

```
if mc_state ≠ In-Progress:
    posture = "Cooperative" (Settled) or "Defensive" (terminal failure)
elif liquidity_stress > 0.75:
    posture = Desperate (60%) or Defensive (40%)
elif trust_score > 0.75:
    posture = Dominant (50%) or Cooperative (50%)
elif turn >= 6:
    posture = Cooperative (55%) or Defensive (45%)
else:
    posture = Dominant/Defensive/Cooperative/Desperate at [0.25, 0.25, 0.30, 0.20]
```

---

## Stage 9 — Dialogue Generation

**Objective:** Generate realistic code-switched negotiation utterances per turn.

A lookup table of 60 dialogue templates (3 per posture×commodity combination, 20 combinations) covers all `(negotiation_posture, commodity_type)` pairs across Hinglish, Telugu-English, and Tamil-English registers. Each template contains a `{p}` placeholder substituted with the current turn's formatted price string (e.g., `₹52.24`). A fallback generic template handles any uncovered combination.

Template selection is uniform random within the posture×commodity group, producing natural variation across turns.

---

## Stage 10 — Sentiment Scoring

**Objective:** Compute a continuous sentiment polarity score for each turn.

```
gap_ratio  = (ask_walk − bid_walk) / (original_ask + ε)
base_sent  = −gap_ratio × 2.0
adjustments:
    Dominant    → +0.20
    Cooperative → +0.15
    Desperate   → −0.30
final_sentiment = clip(base_sent + N(0, 0.10), −1.0, +1.0)
```

Large price gaps produce negative sentiment; cooperative postures and price convergence produce positive sentiment.

---

## Stage 11 — Parquet Streaming Output

**Objective:** Write 1,000,000 rows across 20 chunks without exceeding Colab RAM limits.

A `pyarrow.ParquetWriter` is initialised on the first chunk and kept open across all 20 iterations. Each chunk DataFrame is converted to a `pyarrow.Table` with a fixed schema inferred from chunk 0, written as a Snappy-compressed row group, then deleted with `gc.collect()` to release memory. Peak RAM usage per chunk is approximately 800MB–1.2GB, well within Colab standard limits.



---


## Stage 12 — Validation

**Objective:** Verify structural integrity of the output file.

Post-generation validation checks:
1. **Shape assertion** — `(1,000,000, 40)` exact
2. **Null audit** — zero nulls in all 39 non-terminal-price columns
3. **Settlement integrity** — all rows with `settlement_status == "Settled"` carry non-null `final_settled_price_per_unit`
4. **Copula correlation spot-check** — realized Pearson r between trust_score and default_risk verified against design target (realized: −0.8429, target: −0.70 to −0.80, result: within acceptable range)
5. **Distribution report** — settlement, geographic, and commodity distributions printed and verified against design weights

---


## Dataset Partitioning Strategy

### Train / Validation / Test Construction


Splits are partitioned strictly at the **trajectory level** using `sklearn.model_selection.train_test_split` with `random_state=42`:

1. Extract all 125,000 unique `trajectory_id` values.
2. 80% (100,000 trajectories, 800,000 rows) → train.
3. Remaining 20% split 50/50 → validation (12,500 trajectories, 100,000 rows) and test (12,500 trajectories, 100,000 rows).

Disjoint-set assertions confirm zero trajectory leakage across all three splits.

**Why trajectory-level split matters:** Splitting at the row level would leak turn-sequence information — a model could observe turns 1–5 in training and predict turn 6 in test for the same negotiation episode. Trajectory-level splitting ensures the model has never seen any turn from a test-set episode during training.

---


## Reproducibility

| Component              | Specification           |
| ---------------------- | ----------------------- |
| Global Seed            | 42                      |
| Per-Chunk Seed Formula | `chunk_idx × 9973 + 17` |
| Python Version         | 3.10+                   |
| NumPy Version          | ≥1.24                   |
| SciPy Version          | ≥1.10                   |
| Pandas Version         | ≥2.0                    |
| PyArrow Version        | ≥12.0                   |
| Execution Environment  | Google Colab            |
| Expected Runtime       | ~128 Seconds            |
| Hardware Requirement   | CPU-only                |

### Reproduction Procedure

To reproduce the complete KiranaChain v1.0 release:

1. Install all required dependencies.
2. Execute `kiranachain_generator.py`.
3. Allow all 20 generation chunks to complete.
4. Run validation procedures.
5. Execute trajectory-level split generation.
6. Export train, validation, and test partitions.

The generation pipeline is deterministic and will produce identical outputs when executed under the same software environment and random seed configuration.

---

## Methodological Limitations

The simulation framework intentionally prioritizes structural realism, reproducibility, and controllable statistical behavior over exact replication of real-world economic systems.

Researchers are encouraged to consult `limitations.md` for a detailed discussion of modeling assumptions, abstraction choices, and deployment considerations.

---

## Related Documentation

| Document                      | Purpose                             |
| ----------------------------- | ----------------------------------- |
| `dataset_card.md`             | Dataset overview and usage guidance |
| `data_dictionary.md`          | Field-level schema documentation    |
| `methodology.md`              | Data generation methodology         |
| `limitations.md`              | Known limitations and assumptions   |
| `kirana_chain_v1_schema.json` | JSON telemetry schema               |
| `LICENSE`                     | Licensing information               |

---

## Conclusion

KiranaChain v1.0 combines probabilistic dependency modeling, trajectory-based negotiation simulation, stochastic behavioral perturbation, multilingual dialogue synthesis, and rigorous validation into a unified dataset generation framework.

The resulting dataset provides a reproducible benchmark for research in multi-agent systems, reinforcement learning, supply-chain intelligence, behavioral economics, informal credit modeling, and multilingual conversational AI.

---

## Document Metadata

| Field | Value |
|---------|---------|
| Document | methodology.md |
| Dataset Version | v1.0.0 |
| Methodology Version | v1.0.0 |
| Release Date | May 2026 |
| Maintained By | Atlas AI Labs |

---

**Atlas AI Labs**

Atlas AI Labs is a student-led AI research and engineering lab focused on Artificial Intelligence, Cybersecurity, Artificial General Intelligence (AGI), Agentic AI Systems, Execution-Aware Reasoning, and Practical Intelligence Tools.

Developed by the Atlas AI Labs Team,
a team of undergraduate students from
Vasavi College of Engineering (Autonomous),
Hyderabad, India.

Copyright © 2026 Atlas AI Labs.

Released under the MIT License.
