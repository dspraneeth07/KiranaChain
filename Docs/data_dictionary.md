# KiranaChain v1.0 - Data Dictionary

![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)
![Release Date](https://img.shields.io/badge/Release-May_2026-green?style=for-the-badge)
![Rows](https://img.shields.io/badge/Rows-1M-orange?style=for-the-badge)
![Trajectories](https://img.shields.io/badge/Trajectories-125K-purple?style=for-the-badge)
![Features](https://img.shields.io/badge/Features-40-red?style=for-the-badge)
![Format](https://img.shields.io/badge/Format-Parquet-yellow?style=for-the-badge)

Complete field-level reference for all 40 columns in `kirana_chain_v1_raw.parquet`.                                                              

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Total Rows | 1,000,000 |
| Total Trajectories | 125,000 |
| Trajectory Length | 8 Turns (fixed) |
| Total Features | 40 |
| File Format | Apache Parquet |
| Compression | Snappy |
| Dataset Type | Procedurally Generated Multi-Agent Negotiation Dataset |

---

## Dataset Keys

| Key | Column | Description |
|-----|--------|-------------|
| Primary Row Key | `transaction_id` | Unique identifier for every individual turn row |
| Trajectory Key | `trajectory_id` | Groups all 8 turns of a single negotiation episode |
| Trajectory Length | 8 turns | Fixed turns per trajectory across all 125,000 episodes |
| Recommended Grouping Column | `trajectory_id` | Use this to reconstruct full negotiation sequences |

---

## Null Value Policy

| Column | Null Allowed | Condition |
|--------|-------------|-----------|
| `final_settled_price_per_unit` | Yes | `NaN` when `settlement_status ≠ "Settled"` |
| All other 39 columns | No | Zero nulls enforced by validation pipeline |

---

## Correlation Notation

All inter-variable correlations in this document are reported as **Pearson r** values.
- Valid range: −1.00 to +1.00
- Positive values indicate co-directional relationship
- Negative values indicate inverse relationship
- All values are computed on the full 1,000,000-row released dataset unless stated otherwise

---

## Block A — Agent Profiles & Geographics (Columns 1–8)

| # | Column Name | Data Type | Valid Range | Observed Range | Example Value | Description |
|---|-------------|-----------|-------------|----------------|---------------|-------------|
| 1 | `transaction_id` | `string` (UUIDv4) | Globally unique | — | `7ac5c867-0902-4eed-ad49-8cee50a86f89` | Universally unique identifier for each individual negotiation turn row. Every row has a distinct UUID regardless of trajectory grouping. Used for row-level deduplication and distributed pipeline traceability. |
| 2 | `trajectory_id` | `string` (UUIDv4) | Shared across 8 rows | — | `3f21b44a-11cc-4e7a-b839-92d1cafe3301` | Group key shared by all 8 turn-rows belonging to the same bilateral negotiation episode. Group by this field to reconstruct full negotiation sequences. Primary episode identifier for RL trajectory construction. |
| 3 | `turn_number` | `int8` | 1 – 8 | 1 – 8 | `3` | Sequential position of this row within its parent negotiation trajectory. Turn 1 is the opening exchange; turn 8 is the final forced-resolution turn. Governs Markov transition probabilities — settlement likelihood increases monotonically with turn index. |
| 4 | `distributor_id` | `string` | `DIST_{1000–9999}` | — | `DIST_4821` | Pseudonymous 4-digit hash identifier for the wholesale distributor agent. Consistent across multiple trajectories, enabling multi-episode distributor behavior profiling. Does not map to any real business entity. |
| 5 | `kirana_id` | `string` | `KIR_{10000–99999}` | — | `KIR_73402` | Pseudonymous 5-digit hash identifier for the Kirana micro-retailer agent. Anchors the trust score and Udhar ledger state to a specific retail node. Consistent across trajectories for the same agent. |
| 6 | `geographic_tier` | `string` | Tier-1 Metro, Tier-2 Urban, Tier-3 Semi-Urban, Rural Village | 4 categories | `Tier-3 Semi-Urban` | Administrative and infrastructural stratification of the transaction locale. Conditions logistics constraints, competitor density priors, and payment modality availability. Distribution: Semi-Urban 35.21%, Urban 29.83%, Rural 19.86%, Metro 15.10%. |
| 7 | `state_context` | `string` | 12 Indian states | 12 states | `Telangana` | Indian state jurisdiction of the transaction. Encodes regional regulatory context, linguistic register selection for dialogue templates, mandi price-discovery environment, and local inflation baseline differences. States: AP, Telangana, Maharashtra, UP, Bihar, Tamil Nadu, Rajasthan, WB, Karnataka, MP, Gujarat, Odisha. |
| 8 | `commodity_type` | `string` | Staple Grains, Edible Oils, Spices, Dairy, Packaged FMCG | 5 categories | `Staple Grains` | Product category of the negotiated consignment. Governs baseline INR price range, perishability decay coefficient, posture prior probabilities, and the regional dialogue template applied to `code_switched_dialogue_raw`. Distribution: Grains 30.13%, FMCG 19.85%, Oils 19.85%, Spices 15.09%, Dairy 15.09%. |

---

## Block B — Financial & Credit Matrix / Udhar (Columns 9–18)

| # | Column Name | Data Type | Valid Range | Observed Range | Example Value | Description |
|---|-------------|-----------|-------------|----------------|---------------|-------------|
| 9 | `kirana_historical_trust_score` | `float32` | 0.0000 – 1.0000 | 0.0047 – 0.9989 | `0.7312` | Longitudinal creditworthiness score for the Kirana node derived from historical Udhar repayment consistency. Sampled from Beta(2.5, 1.8) marginal via Gaussian copula. Right-skewed — majority of agents score above 0.5. Mean: 0.5812, Std: 0.2146. |
| 10 | `distributor_credit_limit_allocated` | `float32` | ₹5,000 – ₹500,000 | ₹6,472 – ₹400,917 | `₹142,500.00` | Dynamic INR credit ceiling allocated by the distributor to this Kirana, computed as a function of trust score and a Gamma-distributed baseline. Strong positive copula correlation with trust score (Pearson r ≈ +0.78). Mean: ₹139,520, Std: ₹53,703. |
| 11 | `current_outstanding_udhar` | `float32` | ₹0 – credit limit | ₹1.70 – ₹254,839 | `₹38,200.00` | Active informal debt balance owed by the Kirana to this distributor prior to the current episode. Computed as a copula-conditioned fraction of credit limit. Over-leveraged and under-leveraged states both present. Mean: ₹48,112, Std: ₹32,152. |
| 12 | `repayment_cycle_velocity` | `float32` | 7.00 – 90.00 days | 7.00 – 90.00 days | `24.50` | Average calendar days the Kirana historically requires to clear an informal credit line. Positively correlated with outstanding Udhar (Pearson r ≈ +0.58), negatively correlated with trust score. Slow-paying agents cluster above 45 days. |
| 13 | `kirana_liquidity_stress_index` | `float32` | 0.0000 – 1.0000 | 0.0001 – 0.9984 | `0.6618` | Composite daily cash-flow pressure index at the time of negotiation. Sampled from Beta(1.8, 2.5). Strongly negatively correlated with trust score (Pearson r ≈ −0.73) and positively correlated with default risk (Pearson r ≈ +0.85). Primary driver of negotiation posture. Mean: 0.4183. |
| 14 | `distributor_margin_floor` | `float32` | 0.0300 – 0.1200 | 0.0300 – 0.1200 | `0.0712` | Minimum gross margin fraction below which the distributor will not transact. Encodes operational cost floor including freight, spoilage buffer, and GST overhead. Directly sets the lower bound on ask price modulation per trajectory. |
| 15 | `payment_modality_preference` | `string` | Cash, UPI, Informal Credit, Post-Dated Cheque | 4 categories | `UPI` | Preferred settlement instrument of the Kirana. Distribution: UPI 35%, Cash 30%, Informal Credit 25%, Post-Dated Cheque 10%. UPI signals digital infrastructure access; Informal Credit triggers Udhar ledger update logic. |
| 16 | `historical_order_volume_frequency` | `int8` | 1 – 12 orders/month | 1 – 12 | `5` | Average monthly order count between this specific distributor-Kirana pair. Encodes relational embeddedness and bilateral information asymmetry reduction. Positively correlated with credit limit allocation (Pearson r ≈ +0.47). |
| 17 | `default_risk_probability` | `float32` | 0.0000 – 1.0000 | 0.0278 – 0.8963 | `0.3241` | Dynamically computed probability of Udhar default. Calculated as: `0.05 + 0.45×liquidity_stress + 0.30×(1−trust) + 0.10×(udhar/credit_limit) + ε`. Strongly correlated with interest rate (Pearson r ≈ +0.72). Mean: 0.4014, Std: 0.1603. |
| 18 | `interest_rate_informal` | `float32` | 0.0100 – 0.0800 (1%–8%) | 0.0100 – 0.0800 | `0.0423` | Penalty interest rate on overdue Udhar balances. Computed as: `0.015 + 0.06×default_risk + 0.02×(1−trust)`. Reflects the informal money-market risk premium embedded in distributor-Kirana credit arrangements. |

---

## Block C — Environmental & Supply Chain Externalities (Columns 19–28)

| # | Column Name | Data Type | Valid Range | Observed Range | Example Value | Description |
|---|-------------|-----------|-------------|----------------|---------------|-------------|
| 19 | `monsoon_disruption_index` | `float32` | 0.0000 – 1.0000 | 0.0001 – 0.9950 | `0.4199` | Composite logistics disruption coefficient from monsoon precipitation. Sampled from Beta(1.5, 3.0) — emphasises low-moderate disruption with fat-tail high-disruption events. Causally linked to `perishability_decay_rate` (Pearson r ≈ +0.66) and bottleneck probability. |
| 20 | `festival_proximity_coefficient` | `int16` | 1 – 365 days | 1 – 365 | `176` | Calendar days remaining to the nearest major regional festival (Diwali, Sankranti, Eid, Pongal, Navratri). Values below 30 trigger demand-surge price escalation and shift distributor posture toward Dominant. |
| 21 | `perishability_decay_rate` | `float32` | 0.0000 – 1.0000 | 0.0002 – 0.9980 | `0.5831` | Instantaneous fractional value-decay coefficient under current temperature and humidity. Sampled from Beta(2.0, 2.5). Strongly correlated with ambient temperature (Pearson r ≈ +0.71) and monsoon index (Pearson r ≈ +0.66). High values compress viable negotiation window. |
| 22 | `fuel_price_volatility_delta` | `float32` | −10.0000 – +12.0000 INR/litre | −8.0000 – +10.0000 | `+2.3400` | Session-level diesel price deviation from the regional 30-day moving average. Positive values directly inflate distributor asking price floors through freight cost pass-through. Sampled from truncated Normal(0, 3.5). |
| 23 | `mandi_arrival_volume_shocks` | `float32` | −0.5000 – +0.5000 | −0.4000 – +0.4000 | `−0.1240` | Fractional deviation of commodity arrivals at the nearest APMC wholesale hub from the seasonal baseline. Negative values encode supply compression (price-inflationary). Positively correlated with local inflation (Pearson r ≈ +0.57). |
| 24 | `local_inflation_index_fmcg` | `float32` | 3.0000 – 15.0000 (% annualized) | 3.5000 – 12.0000 | `6.8200` | Regional FMCG consumer price inflation rate, modulating the real purchasing-power constraint on the Kirana. Linked to `mandi_arrival_volume_shocks` and `fuel_price_volatility_delta` through supply-cost transmission. |
| 25 | `ambient_warehouse_temperature` | `float32` | 15.00°C – 45.00°C | 18.00°C – 42.00°C | `34.50` | Measured ambient storage temperature at the distributor's warehouse or transit vehicle. Primary physical driver of perishability decay rate. Values above 38°C trigger Dairy and Spice quality-rejection risk in settlement logic. |
| 26 | `competitor_density_radius` | `int8` | 0 – 20 | 0 – 20 | `7` | Count of rival Kirana retailers within a 1 km radius of the negotiating Kirana node. Higher density increases Kirana substitutability leverage and is the primary covariate for `price_elasticity_demanded`. Mean ≈ 5–6 competitors. |
| 27 | `transportation_mode` | `string` | Tata Ace, Auto Rickshaw, Multi-axle Truck, Handcart | 4 categories | `Tata Ace` | Primary freight vehicle for this consignment. Governs cost-per-km and maximum consignment volume. Distribution: Tata Ace 35%, Multi-axle Truck 25%, Auto Rickshaw 20%, Handcart 20%. Correlated with geographic tier. |
| 28 | `supply_chain_bottleneck_type` | `string` | None, Fuel Strike, Interstate Border Checkpoint, Local Bandh | 4 categories | `None` | Active supply chain disruption in the delivery corridor. Distribution: None 55%, Border Checkpoint 20%, Fuel Strike 15%, Local Bandh 10%. Non-None values amplify fuel volatility delta and delay delivery timelines. |

---

## Block D — Negotiation Trajectory & Dialogue Logs (Columns 29–40)

| # | Column Name | Data Type | Valid Range | Observed Range | Example Value | Description |
|---|-------------|-----------|-------------|----------------|---------------|-------------|
| 29 | `distributor_initial_asking_price_per_unit` | `float32` | Commodity-dependent INR | ₹19.39 – ₹288.70 | `₹56.66` | Distributor's opening ask price per unit. Computed as base commodity price × festival effect × monsoon effect × (1 + margin_floor + upward bias). Fixed for all 8 turns of a trajectory. Mean: ₹85.50. |
| 30 | `kirana_initial_counter_offer_per_unit` | `float32` | 70%–88% of ask price | ₹13.02 – ₹236.96 | `₹46.41` | Kirana's aggressive opening bid, set at 70–88% of the distributor ask, further discounted by `kirana_liquidity_stress_index`. Higher stress → lower opening bid (desperation discount effect). Fixed for all 8 turns. Mean: ₹64.72. |
| 31 | `current_turn_offer_price` | `float32` | Between ask and bid | ₹16.15 – ₹259.77 | `₹52.24` | Active negotiated price at this specific turn. Midpoint of concession-adjusted ask and bid walks, plus Gaussian Process noise. Converges toward settlement price under cooperative trajectories. Mean: ₹75.58. |
| 32 | `price_elasticity_demanded` | `float32` | 1.5000 – 6.0000 | 1.5000 – 6.0000 | `2.9965` | Buyer-side price sensitivity coefficient at the current turn. Computed as `1.5 + 2.5×liquidity_stress + N(0, 0.2)`. Higher values indicate price-sensitive, substitution-ready buyer posture in high-competition micro-markets. |
| 33 | `negotiation_posture` | `string` | Dominant, Defensive, Cooperative, Desperate | 4 categories | `Desperate` | Categorical behavioral state of the negotiating agent at the current turn. Conditioned on Markov state, liquidity stress threshold (>0.75 → Desperate/Defensive), trust score (>0.75 → Dominant/Cooperative), and turn index (≥6 → Cooperative/Defensive). Governs dialogue template selection. |
| 34 | `settlement_status` | `string` | In-Progress, Settled, Walked-Away, Credit-Denied | 4 categories | `In-Progress` | Resolution state of the negotiation at this turn. Governed by a non-stationary Markov chain. Terminal states are absorbing. Distribution: Settled 61.23%, Walked-Away 20.47%, In-Progress 15.54%, Credit-Denied 2.76%. |
| 35 | `final_settled_price_per_unit` | `float32` | Commodity-dependent INR or NaN | ₹16.27 – ₹257.11 | `NaN` | Final agreed price per unit if `settlement_status == "Settled"` at this turn; `NaN` for all other states. Populated only at the first settlement turn within a trajectory. Mean (settled rows only): ₹75.63. |
| 36 | `total_transaction_value_inr` | `float32` | ₹0 – ₹300,000+ | ₹0 – ₹300,000+ | `0.0` | Gross INR transaction value = `final_settled_price × order_volume`. Zero for In-Progress, Walked-Away, and Credit-Denied rows. Order volumes by commodity: Staple Grains 200–2000, Edible Oils 100–800, Spices 50–500, Dairy 100–1000, FMCG 100–1500 units. |
| 37 | `llguidance_constrained_json_log` | `string` (JSON) | Valid JSON — 14 fields | — | `{"turn":1,"settlement_state":"In-Progress","ask_price":56.6615,...}` | Structured 14-field telemetry block per turn. Fields: turn, trajectory_id, settlement_state, ask_price, bid_price, current_offer, elasticity, posture, liquidity_stress, trust_score, monsoon_idx, festival_days_remaining, sentiment, gp_noise. Schema: `schema/kirana_chain_v1_schema.json`. |
| 38 | `code_switched_dialogue_raw` | `string` | Hinglish / Telugu-English / Tamil-English | — | `"Koi bhi rate dedo ₹52.24 tak, khali shelf nahi rakh sakta."` | Verbatim negotiation utterance in regionally authentic code-switched register. Templated by `(negotiation_posture, commodity_type)` pair with current turn price substituted. 20 posture×commodity template sets. Suitable for NLP classification, dialogue act tagging, and multilingual LLM fine-tuning. |
| 39 | `sentiment_intensity_score` | `float32` | −1.0000 – +1.0000 | −1.0000 – +0.5884 | `−0.5937` | Continuous sentiment polarity for the current turn. Computed from price convergence gap ratio plus posture adjustment (Dominant +0.20, Cooperative +0.15, Desperate −0.30) and Gaussian noise N(0, 0.10). Negative = adversarial friction, Positive = cooperative convergence. Mean: −0.0758. |
| 40 | `statistical_noise_artifact` | `float32` | Unbounded (GP sample) | −0.35 – +0.35 approx. | `0.047514` | Gaussian Process noise sampled from squared-exponential kernel k(tᵢ,tⱼ) = exp(−‖tᵢ−tⱼ‖²/(2×5²)) across the 8-turn trajectory window, scaled by 0.12. Encodes human irrationality residuals, unobserved micro-market friction, and measurement noise. Temporally autocorrelated within each trajectory. |

---

## Column Block Summary

| Block | Columns | Count | Primary Use |
|-------|---------|-------|-------------|
| Agent Profiles & Geographics | 1–8 | 8 | Identity, location, commodity |
| Financial & Credit Matrix | 9–18 | 10 | Credit risk, Udhar dynamics |
| Environmental & Supply Chain | 19–28 | 10 | Externality shocks, logistics |
| Negotiation Trajectory & Dialogue | 29–40 | 12 | Price paths, posture, NLP, telemetry |
| **Total** | **1–40** | **40** | |

---

## Recommended Research Tasks

| # | Task | Relevant Columns |
|---|------|-----------------|
| 1 | Multi-Agent Negotiation Learning | All 40 columns — full state vector per turn |
| 2 | Offline Reinforcement Learning | `trajectory_id`, `turn_number`, `current_turn_offer_price`, `settlement_status`, `sentiment_intensity_score` |
| 3 | Credit Risk Modeling | Cols 9–18 — full financial & Udhar block |
| 4 | Settlement Outcome Prediction | `settlement_status` as target; cols 9–18, 19–28 as features |
| 5 | Dialogue Policy Learning | `negotiation_posture`, `code_switched_dialogue_raw`, `llguidance_constrained_json_log` |
| 6 | Sentiment-Aware Negotiation Agents | `sentiment_intensity_score`, `negotiation_posture`, `current_turn_offer_price` |
| 7 | Supply Chain Risk Forecasting | Cols 19–28 — full environmental block |
| 8 | Multilingual Negotiation LLM Fine-Tuning | `code_switched_dialogue_raw`, `llguidance_constrained_json_log` |
| 9 | Trajectory Modeling & Price Path Forecasting | `trajectory_id`, `turn_number`, `current_turn_offer_price`, `final_settled_price_per_unit` |
| 10 | Behavioral Economics Simulation | `negotiation_posture`, `price_elasticity_demanded`, `kirana_liquidity_stress_index`, `default_risk_probability` |

---

Copyright © 2026 Atlas AI Labs. All Rights Reserved.

Atlas AI Labs is a student-led AI research and engineering lab focused on
Artificial Intelligence, Cybersecurity, Artificial General Intelligence (AGI),
Agentic AI Systems, Execution-Aware Reasoning, and Practical Intelligence Tools.

Developed by the Atlas AI Labs Team,
a team of undergraduate students from
Vasavi College of Engineering (Autonomous),
Hyderabad, India.

For research, benchmarking, and educational purposes only.
