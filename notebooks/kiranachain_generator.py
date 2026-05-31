
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install",
                       "pyarrow", "scipy", "numpy", "pandas",
                       "--quiet"])

# ── 1. IMPORTS ───────────────────────────────────────────────
import uuid, gc, json, os, warnings, math, time
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.stats import (norm, beta, gamma, truncnorm,
                          multivariate_normal, expon)
from scipy.linalg import cholesky
from sklearn.model_selection import train_test_split
warnings.filterwarnings("ignore")
np.random.seed(42)

# ── 2. GLOBAL CONSTANTS ──────────────────────────────────────
TOTAL_ROWS   = 1_000_000
CHUNK_SIZE   = 50_000
N_CHUNKS     = TOTAL_ROWS // CHUNK_SIZE          # = 20
OUT_FILE     = "kirana_chain_v1_raw.parquet"
TURNS_PER_NEG = 8

# ── 3. STATIC LOOKUP TABLES ──────────────────────────────────
STATES = ["Andhra Pradesh","Telangana","Maharashtra","Uttar Pradesh",
          "Bihar","Tamil Nadu","Rajasthan","West Bengal","Karnataka",
          "Madhya Pradesh","Gujarat","Odisha"]

GEO_TIERS = ["Tier-1 Metro","Tier-2 Urban","Tier-3 Semi-Urban","Rural Village"]
GEO_TIER_W = [0.15, 0.30, 0.35, 0.20]

COMMODITIES = ["Staple Grains","Edible Oils","Spices","Dairy","Packaged FMCG"]
COMMODITY_W = [0.30, 0.20, 0.15, 0.15, 0.20]

PAYMENT_MODES = ["Cash","UPI","Informal Credit","Post-Dated Cheque"]
PAYMENT_W     = [0.30, 0.35, 0.25, 0.10]

TRANSPORT_MODES = ["Tata Ace","Auto Rickshaw","Multi-axle Truck","Handcart"]
TRANSPORT_W     = [0.35, 0.20, 0.25, 0.20]

BOTTLENECK_TYPES = ["None","Fuel Strike","Interstate Border Checkpoint","Local Bandh"]
BOTTLENECK_W     = [0.55, 0.15, 0.20, 0.10]

SETTLEMENT_STATES_FINAL = ["Settled","Walked-Away","Credit-Denied"]

NEGOTIATION_POSTURES = ["Dominant","Defensive","Cooperative","Desperate"]

# Hinglish / regional code-switched dialogue templates keyed by posture+commodity
DIALOGUE_TEMPLATES = {
    ("Dominant",   "Staple Grains"):  ["Aaj market mein wheat ka rate teen saal ka high hai, aapko {p} se kam nahi dunga bhai.",
                                        "Mandi se confirm hai — floor {p} hai, isse neeche toh mera margin khatam.",
                                        "Rate fix hai {p}, aur zyada discount nahi chalega is hafte."],
    ("Defensive",  "Staple Grains"):  ["Bhaiya last month aapne {p} liya था, ab itna kyun badha diya?",
                                        "Mere paas abhi udhar bhi chal raha hai, thoda adjust karo — {p} se upar afford nahi hoga.",
                                        "Stock toh le lunga lekin {p} pe hi possible hai, bhai."],
    ("Cooperative","Staple Grains"):  ["Dekho {p} pe settle karte hain, dono ka kuch toh banega.",
                                        "Aapka purana customer hoon, {p} fix karo aur kal delivery karo.",
                                        "Theek hai {p} maan lete hain, UPI kar deta hoon abhi."],
    ("Desperate",  "Staple Grains"):  ["Bhai stock khatam ho gaya, {p} pe bhi le lunga, kal tak chahiye.",
                                        "Customer roj aa raha hai, {p} pe pakka karo bas — udhar baad mein settle karenge.",
                                        "Koi bhi rate dedo {p} tak, khali shelf nahi rakh sakta."],
    ("Dominant",   "Edible Oils"):    ["Sunflower oil ka C&F {p} hai, iske neeche possible hi nahi.",
                                        "Refinery se rate aaya hai {p}, margin already tight hai.",
                                        "GST aur freight jodoge toh {p} toh banta hi hai bhai."],
    ("Defensive",  "Edible Oils"):    ["Itna mehnga toh customer UPI nahi cash bhi nahi dega, {p} pe adjust karo.",
                                        "Pados ki dukaan mein {p} se sasta aa raha hai, kyun loon aapse?",
                                        "Last consignment mein quality issue tha, {p} toh dena padega compensation mein."],
    ("Cooperative","Edible Oils"):    ["Ek kaam karo {p} pe do, aur agle order mein volume badhata hoon.",
                                        "NEFT kal tak kar deta hoon {p} ke hisaab se, deal pakki.",
                                        "Theek hai {p} final — lekin delivery Friday ko karni padegi."],
    ("Desperate",  "Edible Oils"):    ["Diwali stock nahi hai bhai, {p} pe bhi okk hai, bas aaj bhejna.",
                                        "Koi bhi brand dedo {p} mein, shelf empty pad raha hai.",
                                        "{p} de do please — udhar wala baad mein clear kar deta hoon pura."],
    ("Dominant",   "Spices"):         ["Red chilli ka arrivals kam hai mandi mein, {p} toh fixed hai.",
                                        "Seasonal scarcity hai, {p} se neeche negotiation nahi chalegi.",
                                        "Aapne quote maanga, mera best price {p} hai, final."],
    ("Defensive",  "Spices"):         ["Itne mein toh last season mila tha — ab {p} pe kaisa maan loon?",
                                        "Quality same hai toh {p} pe hi lunga, zyada nahi de sakta.",
                                        "Thoda humidity zyada hai godown mein, {p} pe hi risk le sakta hoon."],
    ("Cooperative","Spices"):         ["Barabar {p} pe deal karte hain, dono ka fayda.",
                                        "Sample dena pehle, agar theek nikla toh {p} pe full order.",
                                        "{p} confirm — agle hafte phir baat karte hain next consignment."],
    ("Desperate",  "Spices"):         ["Festival aane wala hai bhai, {p} pe bhi le lunga, aaj hi bhejo.",
                                        "Koi bhi rate {p} tak okk hai — customer demand bahut hai abhi.",
                                        "Credit nahi hai account mein lekin {p} pe zaroor lena hai aaj."],
    ("Dominant",   "Dairy"):          ["Cold chain cost alag hai, {p} minimum hai fresh stock ke liye.",
                                        "Expiry 3 din hai, {p} se kam mein margin zero ho jayega.",
                                        "Aaj ka allocation limited hai, {p} pe abhi book karo warna kal nahi milega."],
    ("Defensive",  "Dairy"):          ["3 din ka shelf life hai, {p} pe liya toh wastage ka risk mujhpe.",
                                        "Temperature control nahi hai mere paas, {p} se neeche do toh consider karunga.",
                                        "Pehle return policy batao, phir {p} pe baat karte hain."],
    ("Cooperative","Dairy"):          ["Roz ka order rahunga, {p} pe pakka karo aur cold van bhejte rehna.",
                                        "{p} theek hai — daily delivery pe monthly settle karte hain.",
                                        "Subscription model banaate hain, {p} per litre fixed."],
    ("Desperate",  "Dairy"):          ["Subah se milk khatam hai, {p} pe bhi chalega, abhi bhejna bhai.",
                                        "Customer return aa raha hai, {p} pe instant deal karo.",
                                        "{p} dedo, quality baad mein check karta hoon, delivery priority hai."],
    ("Dominant",   "Packaged FMCG"):  ["Company MRP fixed hai, mera trade margin {p} pe capped hai.",
                                        "Distributor agreement mein {p} floor price hai, neeche possible nahi.",
                                        "Scheme wala stock khatam, regular price {p} hai abhi."],
    ("Defensive",  "Packaged FMCG"): ["Online pe {p} se sasta dikh raha hai — offline mein kyun zyada doon?",
                                        "Scheme kab aayegi? Tabtak {p} pe hold karta hoon order.",
                                        "Margin squeeze ho rahi hai, {p} pe hi possible hai mujhse."],
    ("Cooperative","Packaged FMCG"): ["Display lagata hoon shop mein, {p} pe order confirm karo.",
                                        "Combo pack doge toh {p} pe full truck lene ko tayaar hoon.",
                                        "{p} pe settle — aur credit 15 din ka dena."],
    ("Desperate",  "Packaged FMCG"): ["Festival offer miss ho raha hai, {p} pe bhi le lunga aaj.",
                                        "Shelf empty pad rahi hai, {p} pe bhi okk — bas aaj evening delivery.",
                                        "Koi bhi SKU {p} mein dedo, customer wait nahi karega."],
}

# Fallback for any key not explicitly defined
def _get_dialogue(posture, commodity, price_str):
    key = (posture, commodity)
    if key not in DIALOGUE_TEMPLATES:
        # Use a generic fallback
        return (f"Bhaiya {price_str} pe adjust karo, dono ka kuch toh banega "
                f"— {commodity.lower()} ka demand abhi high hai market mein.")
    templates = DIALOGUE_TEMPLATES[key]
    tmpl = templates[np.random.randint(len(templates))]
    return tmpl.replace("{p}", price_str)

# ── 4. GAUSSIAN COPULA CORRELATION MATRIX (40×40) ───────────
#  We define a structured correlation matrix for the financial/
#  environmental block then embed it via Cholesky.  Full 40-col
#  copula is expensive; we apply block copulas per group.

def _make_financial_corr():
    """10×10 correlation matrix for financial block (cols 9-18)."""
    C = np.eye(10)
    # trust_score ↔ credit_limit:  +0.82
    C[0,1] = C[1,0] = 0.82
    # trust_score ↔ outstanding_udhar: -0.61
    C[0,2] = C[2,0] = -0.61
    # trust_score ↔ repayment_velocity: -0.55
    C[0,3] = C[3,0] = -0.55
    # trust_score ↔ liquidity_stress: -0.73
    C[0,4] = C[4,0] = -0.73
    # trust_score ↔ default_risk: -0.78
    C[0,6] = C[6,0] = -0.78
    # liquidity_stress ↔ outstanding_udhar: +0.69
    C[4,2] = C[2,4] = 0.69
    # liquidity_stress ↔ default_risk: +0.85
    C[4,6] = C[6,4] = 0.85
    # default_risk ↔ interest_rate_informal: +0.72
    C[6,7] = C[7,6] = 0.72
    # outstanding_udhar ↔ repayment_velocity: +0.58
    C[2,3] = C[3,2] = 0.58
    # credit_limit ↔ order_frequency: +0.47
    C[1,5] = C[5,1] = 0.47
    # distributor_margin_floor ↔ default_risk: +0.41
    C[5,6] = C[6,5] = 0.41
    # Ensure PSD via nearest PSD
    eigvals, eigvecs = np.linalg.eigh(C)
    eigvals = np.maximum(eigvals, 1e-6)
    C = eigvecs @ np.diag(eigvals) @ eigvecs.T
    # Normalise diagonal
    d = np.sqrt(np.diag(C))
    C = C / np.outer(d, d)
    return C

def _make_env_corr():
    """10×10 correlation matrix for environmental block (cols 19-28)."""
    C = np.eye(10)
    # monsoon ↔ perishability: +0.66
    C[0,2] = C[2,0] = 0.66
    # monsoon ↔ bottleneck (encoded): +0.44
    C[0,9] = C[9,0] = 0.44
    # fuel_volatility ↔ bottleneck: +0.61
    C[3,9] = C[9,3] = 0.61
    # mandi_shock ↔ local_inflation: +0.57
    C[4,5] = C[5,4] = 0.57
    # ambient_temp ↔ perishability: +0.71
    C[6,2] = C[2,6] = 0.71
    # festival_proximity ↔ mandi_shock: -0.38 (pre-festival stockpiling)
    C[1,4] = C[4,1] = -0.38
    # competitor_density ↔ price_elasticity (cross-block — we apply separately)
    eigvals, eigvecs = np.linalg.eigh(C)
    eigvals = np.maximum(eigvals, 1e-6)
    C = eigvecs @ np.diag(eigvals) @ eigvecs.T
    d = np.sqrt(np.diag(C))
    C = C / np.outer(d, d)
    return C

FIN_CORR = _make_financial_corr()
FIN_CHOL = cholesky(FIN_CORR, lower=True)

ENV_CORR = _make_env_corr()
ENV_CHOL = cholesky(ENV_CORR, lower=True)

# ── 5. NON-STATIONARY MARKOV CHAIN FOR NEGOTIATION TURNS ─────
#  State space: 0=In-Progress, 1=Settled, 2=Walked-Away, 3=Credit-Denied
#  Transition probabilities shift with turn_number (non-stationary)

def _markov_transitions(turn: int, stress: float, trust: float) -> np.ndarray:
    """Return 4×4 transition matrix conditioned on turn & agent states."""
    # Base escalation of settlement probability with turn number
    settle_prob  = min(0.08 + 0.09 * turn + 0.12 * trust, 0.72)
    walkaway_p   = min(0.03 + 0.06 * (turn / 8) + 0.15 * stress, 0.35)
    credit_deny  = min(0.01 + 0.08 * max(0, stress - 0.5), 0.20)
    in_prog_p    = max(1.0 - settle_prob - walkaway_p - credit_deny, 0.05)

    # Normalise
    total = in_prog_p + settle_prob + walkaway_p + credit_deny
    row_ip = np.array([in_prog_p, settle_prob, walkaway_p, credit_deny]) / total

    # Once terminal — absorbing
    T = np.array([
        row_ip,
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])
    return T

# ── 6. BASE PRICE TABLE PER COMMODITY (INR/unit) ─────────────
COMMODITY_BASE_PRICE = {
    "Staple Grains" : (28.0,  55.0),
    "Edible Oils"   : (95.0, 145.0),
    "Spices"        : (60.0, 220.0),
    "Dairy"         : (22.0,  55.0),
    "Packaged FMCG" : (18.0,  85.0),
}

# ── 7. CHUNK GENERATOR ───────────────────────────────────────

def generate_chunk(chunk_idx: int, chunk_size: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed=chunk_idx * 9973 + 17)

    n = chunk_size

    # ── 7A. AGENT PROFILE & GEOGRAPHICS ─────────────────────
    transaction_ids  = [str(uuid.uuid4()) for _ in range(n)]
    # Each 8 turns share a trajectory_id
    n_traj = n // TURNS_PER_NEG
    traj_base = [str(uuid.uuid4()) for _ in range(n_traj)]
    trajectory_ids = np.repeat(traj_base, TURNS_PER_NEG)
    turn_numbers   = np.tile(np.arange(1, TURNS_PER_NEG + 1), n_traj)

    distributor_ids = [f"DIST_{rng.integers(1000,9999)}" for _ in range(n_traj)]
    distributor_ids = np.repeat(distributor_ids, TURNS_PER_NEG)
    kirana_ids      = [f"KIR_{rng.integers(10000,99999)}" for _ in range(n_traj)]
    kirana_ids      = np.repeat(kirana_ids, TURNS_PER_NEG)

    geo_tiers   = rng.choice(GEO_TIERS,   size=n_traj, p=GEO_TIER_W)
    geo_tiers   = np.repeat(geo_tiers, TURNS_PER_NEG)
    states      = rng.choice(STATES,      size=n_traj)
    states      = np.repeat(states, TURNS_PER_NEG)
    commodities = rng.choice(COMMODITIES, size=n_traj, p=COMMODITY_W)
    commodities = np.repeat(commodities, TURNS_PER_NEG)

    # ── 7B. FINANCIAL BLOCK VIA GAUSSIAN COPULA ─────────────
    # Draw correlated normals, convert to uniform, then to marginals
    Z_fin = rng.standard_normal((n_traj, 10))
    Z_fin = (FIN_CHOL @ Z_fin.T).T          # apply Cholesky correlation
    U_fin = norm.cdf(Z_fin)                  # → [0,1] uniform marginals

    # Per-trajectory financials
    trust_score_traj      = U_fin[:, 0]                          # Beta(2,2) margins via uniform
    trust_score_traj      = beta.ppf(U_fin[:, 0], a=2.5, b=1.8) # skew right

    credit_limit_traj     = (trust_score_traj * 180_000
                              + gamma.ppf(U_fin[:, 1], a=2, scale=15000)
                              + 5_000).clip(5_000, 500_000)

    outstanding_udhar_traj= (credit_limit_traj * U_fin[:, 2] * 0.75
                              ).clip(0, credit_limit_traj)

    repayment_vel_traj    = (7 + 45 * U_fin[:, 3] +
                              10 * (1 - trust_score_traj)).clip(7, 90)

    liquidity_stress_traj = beta.ppf(U_fin[:, 4], a=1.8, b=2.5).clip(0,1)

    margin_floor_traj     = (0.03 + 0.09 * U_fin[:, 5]).clip(0.03, 0.12)

    payment_mode_traj     = rng.choice(PAYMENT_MODES, size=n_traj, p=PAYMENT_W)

    order_freq_traj       = (1 + 12 * U_fin[:, 7]).astype(int).clip(1, 12)

    default_risk_traj     = (0.05
                              + 0.45 * liquidity_stress_traj
                              + 0.30 * (1 - trust_score_traj)
                              + 0.10 * (outstanding_udhar_traj /
                                        (credit_limit_traj + 1e-9))
                              + rng.uniform(-0.03, 0.03, n_traj)
                             ).clip(0, 1)

    interest_rate_traj    = (0.015
                              + 0.06 * default_risk_traj
                              + 0.02 * (1 - trust_score_traj)
                             ).clip(0.01, 0.08)

    # Expand to all turns
    trust_score        = np.repeat(trust_score_traj,        TURNS_PER_NEG)
    credit_limit       = np.repeat(credit_limit_traj,       TURNS_PER_NEG)
    outstanding_udhar  = np.repeat(outstanding_udhar_traj,  TURNS_PER_NEG)
    repayment_vel      = np.repeat(repayment_vel_traj,      TURNS_PER_NEG)
    liquidity_stress   = np.repeat(liquidity_stress_traj,   TURNS_PER_NEG)
    margin_floor       = np.repeat(margin_floor_traj,       TURNS_PER_NEG)
    payment_mode       = np.repeat(payment_mode_traj,       TURNS_PER_NEG)
    order_freq         = np.repeat(order_freq_traj,         TURNS_PER_NEG)
    default_risk       = np.repeat(default_risk_traj,       TURNS_PER_NEG)
    interest_rate      = np.repeat(interest_rate_traj,      TURNS_PER_NEG)

    # ── 7C. ENVIRONMENTAL BLOCK VIA GAUSSIAN COPULA ──────────
    Z_env = rng.standard_normal((n_traj, 10))
    Z_env = (ENV_CHOL @ Z_env.T).T
    U_env = norm.cdf(Z_env)

    monsoon_traj     = beta.ppf(U_env[:, 0], a=1.5, b=3.0).clip(0, 1)
    festival_traj    = (1 + 364 * U_env[:, 1]).astype(int).clip(1, 365)
    perishability_traj = beta.ppf(U_env[:, 2], a=2.0, b=2.5).clip(0, 1)
    fuel_delta_traj  = (truncnorm.ppf(U_env[:, 3],
                                      a=-2, b=2,
                                      loc=0, scale=3.5)).clip(-8, 10)
    mandi_shock_traj = (truncnorm.ppf(U_env[:, 4],
                                      a=-2, b=2,
                                      loc=0, scale=0.18)).clip(-0.40, 0.40)
    inflation_traj   = (4.0 + 6.0 * U_env[:, 5]).clip(3.5, 12.0)
    ambient_temp_traj= (18 + 22 * U_env[:, 6]).clip(18, 42)
    competitor_d_traj= (rng.integers(0, 15, size=n_traj) +
                         rng.poisson(lam=3, size=n_traj)).clip(0, 20)
    transport_traj   = rng.choice(TRANSPORT_MODES, size=n_traj, p=TRANSPORT_W)
    bottleneck_traj  = rng.choice(BOTTLENECK_TYPES, size=n_traj, p=BOTTLENECK_W)

    monsoon          = np.repeat(monsoon_traj,      TURNS_PER_NEG)
    festival_prox    = np.repeat(festival_traj,     TURNS_PER_NEG)
    perishability    = np.repeat(perishability_traj,TURNS_PER_NEG)
    fuel_delta       = np.repeat(fuel_delta_traj,   TURNS_PER_NEG)
    mandi_shock      = np.repeat(mandi_shock_traj,  TURNS_PER_NEG)
    inflation_idx    = np.repeat(inflation_traj,    TURNS_PER_NEG)
    ambient_temp     = np.repeat(ambient_temp_traj, TURNS_PER_NEG)
    competitor_d     = np.repeat(competitor_d_traj, TURNS_PER_NEG)
    transport_mode   = np.repeat(transport_traj,    TURNS_PER_NEG)
    bottleneck_type  = np.repeat(bottleneck_traj,   TURNS_PER_NEG)

    # ── 7D. NEGOTIATION TRAJECTORY (Markov + price paths) ────
    # Per-trajectory: base prices
    ask_prices   = np.zeros(n)
    counter_offer= np.zeros(n)
    curr_offers  = np.zeros(n)
    elasticities = np.zeros(n)
    postures_arr = np.empty(n, dtype=object)
    statuses_arr = np.empty(n, dtype=object)
    final_prices = np.full(n, np.nan)
    total_vals   = np.full(n, np.nan)
    sentiments   = np.zeros(n)
    dialogues    = np.empty(n, dtype=object)
    json_logs    = np.empty(n, dtype=object)
    gp_noises    = np.zeros(n)

    ORDER_VOL_RANGE = {"Staple Grains":(200,2000),"Edible Oils":(100,800),
                       "Spices":(50,500),"Dairy":(100,1000),"Packaged FMCG":(100,1500)}

    # GP noise kernel (squared exponential) for statistical_noise_artifact
    gp_length_scale = 5.0
    def gp_sample(length, ls=gp_length_scale):
        x   = np.arange(length, dtype=float)
        K   = np.exp(-0.5 * ((x[:,None]-x[None,:])/ls)**2) + 1e-6 * np.eye(length)
        L   = np.linalg.cholesky(K)
        z   = rng.standard_normal(length)
        return (L @ z) * 0.12

    for t_idx in range(n_traj):
        row_start = t_idx * TURNS_PER_NEG
        comm      = commodities[row_start]
        lo, hi    = COMMODITY_BASE_PRICE[comm]
        # Seasonally modulated base price
        festival_effect = 1.0 + 0.10 * max(0, (60 - festival_traj[t_idx]) / 60)
        monsoon_effect  = 1.0 + 0.08 * monsoon_traj[t_idx]
        base_price = rng.uniform(lo, hi) * festival_effect * monsoon_effect

        dist_ask   = base_price * (1.0 + margin_floor_traj[t_idx]
                                    + rng.uniform(0.02, 0.08))
        kir_bid    = dist_ask * rng.uniform(0.70, 0.88)

        # Liquidity-stress shifts initial bid down
        kir_bid   *= (1.0 - 0.10 * liquidity_stress_traj[t_idx])

        # Per-trajectory GP noise
        gp_noise_vec = gp_sample(TURNS_PER_NEG)

        # Markov state initialisation
        mc_state = 0  # In-Progress

        # Convergence parameters: ask & bid move toward midpoint
        ask_walk = dist_ask
        bid_walk = kir_bid

        for turn in range(1, TURNS_PER_NEG + 1):
            r = row_start + (turn - 1)

            ask_prices[r]    = dist_ask
            counter_offer[r] = kir_bid

            # Non-linear concession: each side concedes with diminishing step
            concession_d = (ask_walk - bid_walk) * rng.uniform(0.05, 0.18)
            concession_k = (ask_walk - bid_walk) * rng.uniform(0.06, 0.20)
            ask_walk  -= concession_d
            bid_walk  += concession_k
            ask_walk   = max(ask_walk, dist_ask * 0.88)
            bid_walk   = min(bid_walk, dist_ask * 1.02)
            curr_price = (ask_walk + bid_walk) / 2.0 + gp_noise_vec[turn-1]

            curr_offers[r]   = round(curr_price, 2)

            # Price elasticity: higher stress → higher elasticity
            elast = (1.5 + 2.5 * liquidity_stress_traj[t_idx]
                     + rng.normal(0, 0.2))
            elasticities[r] = round(abs(elast), 4)

            # Posture: conditioned on turn & stress
            if mc_state != 0:
                posture = "Cooperative" if mc_state == 1 else "Defensive"
            elif liquidity_stress_traj[t_idx] > 0.75:
                posture = rng.choice(["Desperate","Defensive"], p=[0.6,0.4])
            elif trust_score_traj[t_idx] > 0.75:
                posture = rng.choice(["Dominant","Cooperative"], p=[0.5,0.5])
            elif turn >= 6:
                posture = rng.choice(["Cooperative","Defensive"], p=[0.55,0.45])
            else:
                posture = rng.choice(NEGOTIATION_POSTURES,
                                      p=[0.25,0.25,0.30,0.20])
            postures_arr[r] = posture

            # Markov state transition
            if mc_state == 0:
                T = _markov_transitions(turn,
                                        float(liquidity_stress_traj[t_idx]),
                                        float(trust_score_traj[t_idx]))
                mc_state = int(rng.choice([0,1,2,3], p=T[0]))
            # Force terminal at turn 8
            if turn == TURNS_PER_NEG and mc_state == 0:
                mc_state = int(rng.choice([1,2,3], p=[0.55,0.30,0.15]))

            # Status label
            status_map = {0:"In-Progress", 1:"Settled",
                          2:"Walked-Away",  3:"Credit-Denied"}
            statuses_arr[r] = status_map[mc_state]

            # Final price & transaction value
            if mc_state == 1:
                fp = round(curr_price, 2)
                final_prices[r] = fp
                vol_lo, vol_hi  = ORDER_VOL_RANGE[comm]
                order_vol       = rng.integers(vol_lo, vol_hi)
                total_vals[r]   = round(fp * order_vol, 2)
            elif mc_state in (2, 3):
                final_prices[r] = np.nan
                total_vals[r]   = 0.0
            else: # mc_state == 0 (In-Progress)
                final_prices[r] = np.nan
                total_vals[r]   = 0.0

            # Sentiment: correlated with posture and convergence gap
            gap_ratio = (ask_walk - bid_walk) / (dist_ask + 1e-9)
            base_sent = -gap_ratio * 2.0
            if posture == "Dominant":   base_sent += 0.20
            elif posture == "Desperate":base_sent -= 0.30
            elif posture == "Cooperative":base_sent += 0.15
            sentiments[r] = round(float(np.clip(
                base_sent + rng.normal(0, 0.10), -1.0, 1.0)), 4)

            # Dialogue
            price_str = f"₹{curr_price:.2f}"
            dialogues[r] = _get_dialogue(posture, comm, price_str)

            # GP noise artifact
            gp_noises[r] = round(float(gp_noise_vec[turn-1]), 6)

            # JSON telemetry log (llguidance_constrained)
            log_obj = {
                "turn": turn,
                "trajectory_id": traj_base[t_idx],
                "settlement_state": status_map[mc_state],
                "ask_price": round(dist_ask, 4),
                "bid_price": round(kir_bid, 4),
                "current_offer": round(curr_price, 4),
                "elasticity": round(abs(elast), 4),
                "posture": posture,
                "liquidity_stress": round(float(liquidity_stress_traj[t_idx]), 4),
                "trust_score": round(float(trust_score_traj[t_idx]), 4),
                "monsoon_idx": round(float(monsoon_traj[t_idx]), 4),
                "festival_days_remaining": int(festival_traj[t_idx]),
                "sentiment": round(float(sentiments[r]), 4),
                "gp_noise": round(float(gp_noises[r]), 6),
            }
            json_logs[r] = json.dumps(log_obj, ensure_ascii=False)

    # ── 7E. ASSEMBLE DATAFRAME ────────────────────────────────
    df = pd.DataFrame({
        # Agent & Geographic (8)
        "transaction_id"                   : transaction_ids,
        "trajectory_id"                    : trajectory_ids,
        "turn_number"                      : turn_numbers.astype(np.int8),
        "distributor_id"                   : distributor_ids,
        "kirana_id"                        : kirana_ids,
        "geographic_tier"                  : geo_tiers,
        "state_context"                    : states,
        "commodity_type"                   : commodities,
        # Financial & Credit (10)
        "kirana_historical_trust_score"    : trust_score.round(4).astype(np.float32),
        "distributor_credit_limit_allocated": credit_limit.round(2).astype(np.float32),
        "current_outstanding_udhar"        : outstanding_udhar.round(2).astype(np.float32),
        "repayment_cycle_velocity"         : repayment_vel.round(2).astype(np.float32),
        "kirana_liquidity_stress_index"    : liquidity_stress.round(4).astype(np.float32),
        "distributor_margin_floor"         : margin_floor.round(4).astype(np.float32),
        "payment_modality_preference"      : payment_mode,
        "historical_order_volume_frequency": order_freq.astype(np.int8),
        "default_risk_probability"         : default_risk.round(4).astype(np.float32),
        "interest_rate_informal"           : interest_rate.round(4).astype(np.float32),
        # Environmental (10)
        "monsoon_disruption_index"         : monsoon.round(4).astype(np.float32),
        "festival_proximity_coefficient"   : festival_prox.astype(np.int16),
        "perishability_decay_rate"         : perishability.round(4).astype(np.float32),
        "fuel_price_volatility_delta"      : fuel_delta.round(4).astype(np.float32),
        "mandi_arrival_volume_shocks"      : mandi_shock.round(4).astype(np.float32),
        "local_inflation_index_fmcg"       : inflation_idx.round(4).astype(np.float32),
        "ambient_warehouse_temperature"    : ambient_temp.round(2).astype(np.float32),
        "competitor_density_radius"        : competitor_d.astype(np.int8),
        "transportation_mode"              : transport_mode,
        "supply_chain_bottleneck_type"     : bottleneck_type,
        # Negotiation Trajectory (12)
        "distributor_initial_asking_price_per_unit": ask_prices.round(4).astype(np.float32),
        "kirana_initial_counter_offer_per_unit"    : counter_offer.round(4).astype(np.float32),
        "current_turn_offer_price"                 : curr_offers.astype(np.float32),
        "price_elasticity_demanded"                : elasticities.astype(np.float32),
        "negotiation_posture"                      : postures_arr,
        "settlement_status"                        : statuses_arr,
        "final_settled_price_per_unit"             : final_prices.astype(np.float32),
        "total_transaction_value_inr"              : total_vals.astype(np.float32),
        "llguidance_constrained_json_log"          : json_logs,
        "code_switched_dialogue_raw"               : dialogues,
        "sentiment_intensity_score"                : sentiments.astype(np.float32),
        "statistical_noise_artifact"               : gp_noises.astype(np.float32),
    })

    assert df.shape[1] == 40, f"Column count mismatch: {df.shape[1]}"
    return df

# ── 8. PARQUET WRITER SETUP ───────────────────────────────────
writer = None
schema = None
total_written = 0
t0 = time.time()

print("="*65)
print("  KiranaChain v1.0 — Decentralised Retail Negotiation Engine")
print(f"  Target: {TOTAL_ROWS:,} rows × 40 columns")
print(f"  Strategy: {N_CHUNKS} chunks × {CHUNK_SIZE:,} rows  |  Parquet streaming")
print("="*65)

for chunk_idx in range(N_CHUNKS):
    t_chunk = time.time()
    df_chunk = generate_chunk(chunk_idx, CHUNK_SIZE)

    # Initialise Parquet writer on first chunk
    if writer is None:
        schema = pa.Schema.from_pandas(df_chunk, preserve_index=False)
        writer = pq.ParquetWriter(OUT_FILE, schema,
                                   compression="snappy",
                                   use_dictionary=True)

    table = pa.Table.from_pandas(df_chunk, schema=schema, preserve_index=False)
    writer.write_table(table)
    total_written += len(df_chunk)

    elapsed_chunk = time.time() - t_chunk
    elapsed_total = time.time() - t0
    pct = 100 * total_written / TOTAL_ROWS
    print(f"  Chunk {chunk_idx+1:>2}/{N_CHUNKS}  |  "
          f"{total_written:>9,} rows  |  "
          f"{pct:5.1f}%  |  "
          f"chunk: {elapsed_chunk:.2f}s  |  "
          f"total: {elapsed_total:.1f}s")

    del df_chunk, table
    gc.collect()

writer.close()
print("\n" + "="*65)
print(f"  ✓  Parquet written  →  {OUT_FILE}")
print(f"  ✓  Total time       →  {time.time()-t0:.1f}s")
print("="*65)

# ── 9. VALIDATION REPORT ─────────────────────────────────────
print("\n── VALIDATION REPORT ───────────────────────────────────────")
df_val = pq.read_table(OUT_FILE).to_pandas()
print(f"\n  Shape          :  {df_val.shape}")
assert df_val.shape == (TOTAL_ROWS, 40), \
    f"SHAPE MISMATCH! Got {df_val.shape}"
print(f"  ✓ Shape verified: ({TOTAL_ROWS:,}, 40)\n")

# Null check
null_counts = df_val.isnull().sum()
non_null_expected = [c for c in df_val.columns if c != "final_settled_price_per_unit"]
critical_nulls = null_counts[non_null_expected]
print("  Null audit (non-final-price columns):")
print(f"    Total nulls in non-price cols : {critical_nulls.sum()}")
assert critical_nulls.sum() == 0, "UNEXPECTED NULLS DETECTED"
print("  ✓ Zero unexpected nulls\n")

# Settlement distribution
print("  Settlement Status Distribution:")
print(df_val["settlement_status"].value_counts(normalize=True)
      .mul(100).round(2).to_string())

print("\n  Geographic Tier Distribution:")
print(df_val["geographic_tier"].value_counts(normalize=True)
      .mul(100).round(2).to_string())

print("\n  Commodity Type Distribution:")
print(df_val["commodity_type"].value_counts(normalize=True)
      .mul(100).round(2).to_string())

print("\n  Key Financial Statistics:")
fin_cols = ["kirana_historical_trust_score",
            "distributor_credit_limit_allocated",
            "current_outstanding_udhar",
            "kirana_liquidity_stress_index",
            "default_risk_probability"]
print(df_val[fin_cols].describe().round(4).to_string())

print("\n  Negotiation Price Statistics:")
price_cols = ["distributor_initial_asking_price_per_unit",
              "kirana_initial_counter_offer_per_unit",
              "current_turn_offer_price",
              "final_settled_price_per_unit"]
print(df_val[price_cols].describe().round(4).to_string())

print("\n  Sample JSON Telemetry Log (row 0):")
print("  " + df_val["llguidance_constrained_json_log"].iloc[0])

print("\n  Sample Dialogue (row 0):")
print("  " + df_val["code_switched_dialogue_raw"].iloc[0])

print("\n  Sentiment Distribution:")
print(f"    mean  : {df_val['sentiment_intensity_score'].mean():.4f}")
print(f"    std   : {df_val['sentiment_intensity_score'].std():.4f}")
print(f"    min   : {df_val['sentiment_intensity_score'].min():.4f}")
print(f"    max   : {df_val['sentiment_intensity_score'].max():.4f}")

print("\n  Copula Correlation Spot-Check (Trust Score vs Default Risk):")
corr_val = df_val["kirana_historical_trust_score"].corr(
               df_val["default_risk_probability"])
print(f"    Pearson r : {corr_val:.4f}  (expected ≈ -0.70 to -0.80)")

print("\n" + "="*65)
print("  ✓  KiranaChain v1.0 — ALL VALIDATIONS PASSED")
print(f"  ✓  Output: {OUT_FILE}")
print(f"  ✓  Size  : {os.path.getsize(OUT_FILE)/1e6:.1f} MB")
print("="*65)

del df_val
gc.collect()



# INPUT
INPUT_FILE = "kirana_chain_v1_elite.parquet"

TRAIN_OUT = "kirana_chain_v1_train.parquet"
VAL_OUT   = "kirana_chain_v1_val.parquet"
TEST_OUT  = "kirana_chain_v1_test.parquet"

# LOAD
print("Loading parquet...")
df = pd.read_parquet(INPUT_FILE)

print("Rows:", len(df))
print("Trajectories:", df["trajectory_id"].nunique())

# TRAJECTORY LEVEL SPLIT
trajectory_ids = df["trajectory_id"].unique()

# 80% train
train_traj, temp_traj = train_test_split(
    trajectory_ids,
    test_size=0.20,
    random_state=42
)

# remaining 20% -> 10% val + 10% test
val_traj, test_traj = train_test_split(
    temp_traj,
    test_size=0.50,
    random_state=42
)

# FILTER ROWS
train_df = df[df["trajectory_id"].isin(train_traj)]
val_df   = df[df["trajectory_id"].isin(val_traj)]
test_df  = df[df["trajectory_id"].isin(test_traj)]

# SAVE
train_df.to_parquet(TRAIN_OUT, index=False)
val_df.to_parquet(VAL_OUT, index=False)
test_df.to_parquet(TEST_OUT, index=False)

# REPORT
total = len(df)

print("\n===== SPLIT REPORT =====")
print(f"Train : {len(train_df):,} ({100*len(train_df)/total:.2f}%)")
print(f"Val   : {len(val_df):,} ({100*len(val_df)/total:.2f}%)")
print(f"Test  : {len(test_df):,} ({100*len(test_df)/total:.2f}%)")

print("\nTrajectory Counts")
print("Train:", len(train_traj))
print("Val  :", len(val_traj))
print("Test :", len(test_traj))

# Leakage check
assert set(train_traj).isdisjoint(val_traj)
assert set(train_traj).isdisjoint(test_traj)
assert set(val_traj).isdisjoint(test_traj)

print("\n No trajectory leakage detected")
print(" Train/Val/Test files created")
