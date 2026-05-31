# KiranaChain v1.0.0 — Limitations & Known Constraints

### Understanding the Scope, Assumptions, and Boundaries of the Dataset

![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)
![Release](https://img.shields.io/badge/Release-May_2026-green?style=for-the-badge)
![Rows](https://img.shields.io/badge/Rows-1M-orange?style=for-the-badge)
![Trajectories](https://img.shields.io/badge/Trajectories-125K-purple?style=for-the-badge)
![Type](https://img.shields.io/badge/Dataset-Synthetic-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

## Purpose of This Document

This document outlines the known limitations, simplifying assumptions, modeling constraints, and intended scope of KiranaChain v1.0. Understanding these limitations is essential for responsible interpretation of experimental results and for assessing the suitability of the dataset for downstream research tasks.

While KiranaChain has been designed to reproduce many structural characteristics of India's informal retail supply ecosystem, it remains a synthetic research dataset and should not be interpreted as a perfect representation of real-world economic behavior.

---

## 1. Synthetic and Procedurally Generated Data

### Description

KiranaChain is generated using a high-fidelity procedural simulation pipeline rather than direct field collection from real Kirana stores, distributors, or financial institutions.

The generation framework incorporates:

* Gaussian Copula dependency modeling
* Non-Stationary Markov negotiation dynamics
* Gaussian Process stochastic perturbations
* Behavioral posture simulation
* Supply-chain externality modeling
* Informal credit (Udhar) dynamics

Despite these mechanisms, no synthetic generator can fully capture the complete complexity of real-world human decision making.

### Research Impact

Researchers should treat KiranaChain as a simulation-driven benchmark for algorithm development, representation learning, and model evaluation. Models intended for deployment should undergo additional validation using real-world observational data.

---

## 2. Geographic Representation Constraints

### Description

The dataset represents negotiations across 12 Indian states:

* Andhra Pradesh
* Telangana
* Maharashtra
* Uttar Pradesh
* Bihar
* Tamil Nadu
* Rajasthan
* West Bengal
* Karnataka
* Madhya Pradesh
* Gujarat
* Odisha

Several important regional markets remain outside the current release scope.

### Research Impact

Regional economic structures, commodity preferences, logistics networks, and credit behaviors may differ significantly in unrepresented states. Geographic generalization should therefore be evaluated carefully.

---

## 3. Template-Based Dialogue Generation

### Description

The field `code_switched_dialogue_raw` is generated using posture-conditioned and commodity-aware dialogue templates.

Dialogue generation captures:

* Hinglish negotiation patterns
* Telugu-English code switching
* Tamil-English code switching
* Commodity-specific bargaining language
* Price-conditioned utterance construction

However, conversations remain template-driven rather than organically collected.

### Research Impact

Models trained exclusively on KiranaChain dialogues may partially learn template structures rather than naturally occurring conversational variation. Real-world conversational corpora should be incorporated for production-grade NLP systems.

---

## 4. Simplified Negotiation Psychology

### Description

Human negotiation behavior is inherently continuous, contextual, and multi-dimensional.

KiranaChain approximates negotiation behavior using four discrete states:

* Dominant
* Defensive
* Cooperative
* Desperate

These categories provide a tractable representation but cannot fully capture nuanced human behavioral variation.

### Research Impact

The `negotiation_posture` field should be interpreted as a coarse behavioral abstraction rather than a psychological ground-truth label.

---

## 5. Limited Seasonal Representation

### Description

Seasonality is modeled primarily through:

* `festival_proximity_coefficient`
* `monsoon_disruption_index`

The dataset does not explicitly model:

* Rabi crop cycles
* Kharif crop cycles
* Multi-year commodity trends
* Long-term inflation cycles
* Calendar-specific seasonal shocks

### Research Impact

Researchers requiring calendar-aware forecasting or agricultural seasonality analysis should augment the dataset with external temporal information.

---

## 6. Category-Level Commodity Modeling

### Description

Commodity representation is intentionally limited to five macro-categories:

* Staple Grains
* Edible Oils
* Spices
* Dairy
* Packaged FMCG

The dataset does not model:

* Individual SKUs
* Brand-level effects
* Packaging variations
* Product quality tiers
* Shelf-life heterogeneity within categories

### Research Impact

KiranaChain is suitable for category-level economic modeling rather than SKU-level retail analytics.

---

## 7. Simplified Informal Credit Structure

### Description

The informal Udhar ecosystem in reality often consists of complex multi-party credit relationships.

KiranaChain models only:

Distributor ↔ Kirana

credit interactions.

The following structures are not modeled:

* Multi-distributor borrowing
* Supplier-to-distributor credit chains
* Social collateral networks
* Credit guarantees
* Community lending effects

### Research Impact

Network-scale credit propagation studies require additional graph-based augmentation.

---

## 8. Absence of Real Financial Records and PII

### Description

No personally identifiable information (PII) exists within KiranaChain.

All identifiers are synthetically generated and do not correspond to:

* Real people
* Real stores
* Real distributors
* Real transactions
* Real financial accounts

### Research Impact

The dataset is privacy-preserving by design and suitable for open research distribution.

---

## 9. Markovian Negotiation Assumption

### Description

Negotiation progression is governed by a Non-Stationary Markov framework.

As a result, future state transitions primarily depend on the current state and associated features rather than complete historical context.

Real-world negotiations frequently depend on:

* Relationship history
* Trust accumulation
* Historical transaction memory
* Prior negotiation outcomes
* Long-term behavioral adaptation

### Research Impact

History-dependent strategies may be underrepresented relative to real-world negotiation environments.

---

## 10. Fixed Payment Modality Within Episodes

### Description

The variable `payment_modality_preference` remains fixed throughout an individual trajectory.

In practice, payment mechanisms may change dynamically during negotiation due to evolving liquidity conditions.

### Research Impact

Dynamic payment-strategy adaptation is not represented in the current release.

---

## Future Development Roadmap

Future releases of KiranaChain may incorporate:

* Expansion beyond 20 Indian states
* SKU-level commodity representations
* Multi-creditor Udhar networks
* Calendar-aligned economic signals
* Greater dialogue diversity through advanced generation pipelines
* Multi-agent graph interactions
* Richer negotiation psychology models
* Long-horizon retailer-distributor relationship histories

---

## Final Remarks

KiranaChain v1.0.0 is intended as a research and benchmarking resource for studying negotiation, informal credit systems, supply-chain intelligence, reinforcement learning, and multilingual conversational AI within the context of India's informal retail economy.

Researchers are encouraged to interpret results within the scope of the assumptions documented above and to supplement the dataset with real-world evidence when pursuing deployment-oriented applications.

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
Released under the MIT License.
