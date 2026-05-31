# KiranaChain v1.0.0

### Multi-Agent Decentralized Retail Negotiation Trajectories for the Indian Informal Economy

![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)
![Release](https://img.shields.io/badge/Release-May_2026-green?style=for-the-badge)
![Rows](https://img.shields.io/badge/Rows-1M-orange?style=for-the-badge)
![Trajectories](https://img.shields.io/badge/Trajectories-125K-purple?style=for-the-badge)
![Features](https://img.shields.io/badge/Features-40-red?style=for-the-badge)
![Format](https://img.shields.io/badge/Format-Parquet-yellow?style=for-the-badge)

---

## Dataset Identity

| Attribute                | Value                                                        |
| ------------------------ | ------------------------------------------------------------ |
| Dataset Name             | KiranaChain                                                  |
| Version                  | 1.0.0                                                        |
| Release Date             | May 2026                                                    |
| Dataset Category         | Synthetic Multi-Agent Negotiation Dataset                    |
| Development Organisation | Atlas AI Labs                                                |
| Academic Affiliation     | Vasavi College of Engineering (Autonomous), Hyderabad, India |
| Language Coverage        | Hinglish, Telugu-English, Tamil-English                      |
| Geographic Coverage      | India (12 States)                                            |


---

## Development Team

| Role                                                           | Name                     | Affiliation                                                                                                                |
| -------------------------------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Founder, Principal Investigator & Lead Research Engineer       | Dhadi Sai Praneeth Reddy | Atlas AI Labs; Department of Computer Science and Engineering, Vasavi College of Engineering (Autonomous), Hyderabad       |
| Data Engineering & Dataset Validation Engineer                 | Mididuddi Dhatri         | Atlas AI Labs; Department of Computer Science and Engineering, Vasavi College of Engineering (Autonomous), Hyderabad       |
| Schema Engineering, Documentation & Quality Assurance Engineer | Biradar Amulya           | Atlas AI Labs; Department of Computer Science and Engineering, Vasavi College of Engineering (Autonomous), Hyderabad       |
| Academic Advisor & Faculty Mentor                              | Dr. M. Jithender Reddy   | Assistant Professor, Department of Computer Science and Engineering, Vasavi College of Engineering (Autonomous), Hyderabad |


---

## Dataset Description

| Attribute                      | Value                                                                                                                                        |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Domain                         | Informal Retail Economics, Supply Chain Intelligence, Multi-Agent Negotiation Systems                                                        |
| Geographic Coverage            | India (12 States)                                                                                                                            |
| States Covered                 | Andhra Pradesh, Telangana, Maharashtra, Uttar Pradesh, Bihar, Tamil Nadu, Rajasthan, West Bengal, Karnataka, Madhya Pradesh, Gujarat, Odisha |
| Language Coverage              | Hinglish (Hindi-English), Telugu-English, Tamil-English Code-Switched Dialogue                                                               |
| Dataset Type                   | Synthetic Multi-Agent Negotiation Dataset                                                                                                    |
| Total Rows                     | 1,000,000                                                                                                                                    |
| Total Negotiation Trajectories | 125,000                                                                                                                                      |
| Trajectory Length              | 8 Turns (Fixed)                                                                                                                              |
| Total Features                 | 40                                                                                                                                           |
| Target Variables               | settlement_status, final_settled_price_per_unit, sentiment_intensity_score                                                                   |
| Primary Key                    | transaction_id                                                                                                                               |
| Trajectory Key                 | trajectory_id                                                                                                                                |


---

## Data Format & Storage

| Attribute              | Value                                 |
| ---------------------- | ------------------------------------- |
| Storage Format         | Apache Parquet                        |
| Compression Codec      | Snappy                                |
| Dataset Size           | ~156 MB                               |
| Schema Version         | v1.0                                  |
| Telemetry Format       | JSON (14 fields per negotiation turn) |
| Character Encoding     | UTF-8                                 |
| Row Granularity        | One negotiation turn per row          |
| Trajectory Granularity | Eight turns per negotiation episode   |


---

## Dataset Splits

| Split      | File                            |          Rows | Trajectories | Proportion |
| ---------- | ------------------------------- | ------------: | -----------: | ---------: |
| Train      | `kirana_chain_v1_train.parquet` |       800,000 |      100,000 |        80% |
| Validation | `kirana_chain_v1_val.parquet`   |       100,000 |       12,500 |        10% |
| Test       | `kirana_chain_v1_test.parquet`  |       100,000 |       12,500 |        10% |
| **Total**  | —                               | **1,000,000** |  **125,000** |   **100%** |

### Split Strategy

All dataset partitions are generated at the **trajectory level** rather than the row level. Each negotiation trajectory is assigned exclusively to a single split, ensuring that no `trajectory_id` is shared across the training, validation, or test sets.

### Leakage Prevention

* Trajectory-level partitioning
* Zero overlap of `trajectory_id` values across splits
* Verified disjoint train, validation, and test partitions
* Suitable for trajectory modeling, offline reinforcement learning, sequence forecasting, and multi-agent learning benchmarks

### Reproducibility

Split generation uses a fixed random seed and deterministic trajectory assignment to ensure reproducible experimental results across independent studies.


---

## Data Generation & Quality Assurance

| Attribute                | Description                                                                                                                                                                                                           |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Data Generation Method   | Procedurally generated using a high-fidelity simulation pipeline designed to model negotiation dynamics within India's informal retail supply ecosystem                                                               |
| Core Modeling Components | Gaussian Copula-based dependency modeling, Non-Stationary Markov Negotiation State Machine, Gaussian Process-based stochastic trajectory perturbation                                                                 |
| Trajectory Construction  | 125,000 independent negotiation episodes, each comprising 8 sequential turns, yielding 1,000,000 turn-level observations                                                                                              |
| Dialogue Generation      | Commodity-aware and posture-conditioned multilingual code-switched dialogue templates (Hinglish, Telugu-English, Tamil-English)                                                                                       |
| Credit & Risk Modeling   | Copula-conditioned trust, credit allocation, liquidity stress, repayment velocity, and default-risk generation                                                                                                        |
| Environmental Simulation | Monsoon disruption, inflation, mandi shocks, transportation constraints, and supply-chain bottlenecks                                                                                                                 |
| Validation Procedures    | Dataset shape verification, schema validation, null-value auditing, trajectory integrity checks, correlation consistency verification, Markov state-transition validation, and cross-field logical consistency checks |
| Quality Status           | All validation checks passed successfully during dataset generation and release preparation                                                                                                                           |

---

## Licensing & Access

| Attribute           | Value                                                                                                            |
| ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| License             | MIT License                                                                                                      |
| License File        | `LICENSE`                                                                                                        |
| Official Repository | https://github.com/dspraneeth07/kiranachain                                                                      |
| Dataset Hosting     | Soon                                                                                                             |
| Organisation        | Atlas AI Labs                                                                                                    |
| Contact             | [dspraneeth@atlasailabs.in](mailto:dspraneeth@atlasailabs.in)                                                    |
| Access Level        | Public                                                                                                           |
| Intended Use        | Research, Education, Benchmarking, and Non-Commercial or Commercial Applications permitted under the MIT License |

### License Summary

KiranaChain is released under the MIT License, a permissive open-source license that allows users to use, copy, modify, merge, publish, distribute, sublicense, and commercially utilize the dataset without restriction, subject to the inclusion of the original copyright notice and license text in all copies or substantial portions of the dataset.

The dataset is provided "as is", without warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement.

For the complete license terms and conditions, refer to the accompanying `LICENSE` file included with this release.



---

## Description

KiranaChain is a large-scale synthetic behavioral dataset designed to model negotiation dynamics within India's informal retail supply ecosystem. The dataset captures bilateral interactions between wholesale distributors and Kirana micro-retailers across 12 Indian states, representing a diverse range of geographic, financial, and operational conditions.

Each negotiation episode integrates agent-level financial states, informal credit (Udhar) relationships, environmental and supply-chain externalities, negotiation behavior, settlement outcomes, and multilingual code-switched dialogue. The released version comprises 125,000 complete negotiation trajectories, each containing 8 sequential turns, resulting in a total of 1,000,000 turn-level observations and 40 structured features.

KiranaChain is intended to support research in multi-agent systems, reinforcement learning, behavioral economics, supply-chain intelligence, credit-risk modeling, trajectory forecasting, and multilingual language technologies.

---

## Motivation

India's retail economy is dominated by an estimated 12–14 million Kirana stores, forming one of the world's largest decentralized retail networks. Despite their critical role in food distribution, local commerce, and supply-chain resilience, the operational dynamics of Kirana businesses remain largely underrepresented in publicly available datasets.

In particular, there is a significant lack of structured datasets capturing negotiation behavior, informal credit (Udhar) relationships, distributor–retailer interactions, supply-chain disruptions, and multilingual communication patterns within the Indian informal economy. This data scarcity limits the development and evaluation of AI systems for negotiation, credit-risk assessment, supply-chain intelligence, and decision-making under uncertainty.

KiranaChain was created to address this gap by providing a large-scale, trajectory-based dataset that integrates financial signals, environmental externalities, behavioral negotiation dynamics, settlement outcomes, and code-switched dialogue within a unified framework. The dataset is intended to support research in multi-agent systems, reinforcement learning, behavioral economics, supply-chain analytics, informal credit modeling, and multilingual language technologies.

---

## Key Statistics

| Metric                                             |           Value |
| -------------------------------------------------- | --------------: |
| Total Rows                                         |       1,000,000 |
| Total Trajectories                                 |         125,000 |
| Trajectory Length                                  |         8 Turns |
| Total Features                                     |              40 |
| Settlement Rate                                    |          61.23% |
| Walk-Away Rate                                     |          20.47% |
| Credit-Denial Rate                                 |           2.76% |
| In-Progress Rate                                   |          15.54% |
| Mean Distributor Asking Price                      | ₹85.50 per Unit |
| Mean Initial Kirana Counter Offer                  | ₹64.72 per Unit |
| Mean Negotiated Offer Price                        | ₹75.58 per Unit |
| Mean Settled Price                                 | ₹75.63 per Unit |
| Mean Trust Score                                   |          0.5812 |
| Mean Liquidity Stress Index                        |          0.4183 |
| Mean Default Risk Probability                      |          0.4014 |
| Trust Score ↔ Default Risk Correlation (Pearson r) |         −0.8429 |
| Dataset Size (Compressed)                          |          156 MB |

### Distribution Summary

| Category             | Distribution                                                                                          |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| Settlement Outcomes  | Settled (61.23%), Walked-Away (20.47%), In-Progress (15.54%), Credit-Denied (2.76%)                   |
| Geographic Coverage  | Tier-3 Semi-Urban (35.21%), Tier-2 Urban (29.83%), Rural Village (19.86%), Tier-1 Metro (15.10%)      |
| Commodity Categories | Staple Grains (30.13%), Packaged FMCG (19.85%), Edible Oils (19.85%), Spices (15.09%), Dairy (15.09%) |

### Validation Status

✓ Dataset Shape Verified: 1,000,000 × 40
✓ Zero Unexpected Null Values
✓ Trajectory Integrity Verified
✓ Schema Compliance Verified
✓ Statistical Consistency Verified
✓ Correlation Structure Verified
✓ All Release Validation Checks Passed

---
## Research Applications

| Research Area                     | Representative Tasks                                                                                                |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Multi-Agent Systems               | Bilateral negotiation modeling, strategic decision-making, and agent interaction analysis                           |
| Reinforcement Learning            | Offline RL, trajectory optimization, policy learning, and reward modeling using complete negotiation episodes       |
| Supervised Learning               | Settlement outcome prediction, price forecasting, posture classification, and risk assessment                       |
| Credit Risk Analytics             | Informal credit (Udhar) risk estimation, default prediction, and trust-score modeling                               |
| Supply Chain Intelligence         | Demand-shock forecasting, bottleneck analysis, logistics disruption modeling, and resilience assessment             |
| Behavioral Economics              | Price elasticity analysis, negotiation behavior modeling, and decision-making under uncertainty                     |
| Natural Language Processing       | Dialogue act classification, sentiment modeling, negotiation intent recognition, and multilingual conversational AI |
| Large Language Models (LLMs)      | Fine-tuning, instruction tuning, synthetic negotiation agents, and code-switched dialogue generation                |
| Graph Machine Learning            | Distributor–retailer relationship modeling, trust propagation, and network-level credit analysis                    |
| Time-Series & Trajectory Modeling | Sequential negotiation forecasting, settlement path prediction, and trajectory representation learning              |

---

## Ethical Considerations

### Privacy & Personal Data

* KiranaChain contains no personally identifiable information (PII).
* All agent identifiers (`distributor_id`, `kirana_id`) are synthetically generated pseudonymous identifiers and do not correspond to real individuals, organizations, or businesses.
* No real customer, retailer, distributor, financial, or transactional records were used during dataset generation.

### Synthetic Data Disclaimer

* KiranaChain is a fully synthetic dataset generated through a procedural simulation pipeline.
* Financial relationships, negotiation behaviors, environmental conditions, and settlement outcomes are simulated representations designed for research and benchmarking purposes.
* The dataset should not be interpreted as a direct representation of any specific real-world entity, market, or economic region.

### Responsible Use

* The dataset is intended for research, education, benchmarking, and model development.
* Models trained using KiranaChain should not be deployed for real-world lending, credit approval, pricing, or financial decision-making without additional domain-specific validation and regulatory review.
* Researchers are encouraged to evaluate fairness, robustness, and generalization before applying models derived from this dataset to operational environments.

### Limitations

* Dialogue utterances are template-driven synthetic constructions and do not represent recorded human conversations.
* Statistical relationships are engineered to reflect plausible market dynamics and should not be interpreted as causal economic evidence.
* While designed to approximate realistic negotiation behavior, the dataset cannot capture the full complexity of India's informal retail ecosystem.

---
## Citation

If you use KiranaChain in academic research, publications, benchmarks, or derivative works, please cite the dataset as follows:

```bibtex
@dataset{kiranachain2026,
  title        = {KiranaChain: Multi-Agent Decentralized Retail Negotiation Trajectories},
  author       = {Dhadi, Sai Praneeth Reddy and
                  Mididuddi, Dhatri and
                  Biradar, Amulya and
                  Reddy, M. Jithender},
  year         = {2026},
  version      = {1.0.0},
  publisher    = {To Be Announced},
  doi          = {To Be Announced},
  url          = {To Be Announced}
}
```

### Citation Notes

* Cite the dataset version used in experiments to ensure reproducibility.
* For derivative datasets, benchmark suites, or fine-tuned models, attribution to the original KiranaChain release is recommended.

---

## Publisher Information

**Atlas AI Labs**

Atlas AI Labs is a student-led AI research and engineering lab focused on Artificial Intelligence, Cybersecurity, Artificial General Intelligence (AGI), Agentic AI Systems, Execution-Aware Reasoning, and Practical Intelligence Tools.

Developed by the Atlas AI Labs Team,
a team of undergraduate students from
Vasavi College of Engineering (Autonomous),
Hyderabad, India.

Copyright © 2026 Atlas AI Labs.

Released under the MIT License.

