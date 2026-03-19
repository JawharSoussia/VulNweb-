# UNSW-NB15 EDA Summary Report

**Date:** 19/03/2026
**Dataset:** UNSW-NB15 from Kaggle
**Source:** https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15

## Overview

### Dataset Statistics
- **Total Samples:** 2,797,931 network flows
- **Features:** 47 network and traffic features
- **Time Period:** Captured in controlled laboratory environment
- **Class Label:** 0 = Benign, 1 = Attack

### Class Distribution
- **Benign Flows (Label=0):** [2218764] samples ([87.3%])
- **Attack Flows (Label=1):** [321283] samples ([12.7%])
- **Imbalance Ratio:** [0.14] (⚠️  if < 0.3 - requires SMOTE 1 = balanced)

### Attack Categories
Generic             215481
Exploits             44525
 Fuzzers             19195
DoS                  16353
 Reconnaissance      12228
 Fuzzers              5051
Analysis              2677
Backdoor              1795
Reconnaissance        1759
 Shellcode            1288
Backdoors              534
Shellcode              223
Worms                  174


## Key Findings

### Data Quality
Missing values detected:
 sport: 258188 (9.23%)
 dstip: 209 (0.01%)
 dstp: 2540258 (90.79%)
 state: 209 (0.01%)
 dur: 211 (0.01%)
 sbytes: 211 (0.01%)
 dbytes: 211 (0.01%)
 sttl: 211 (0.01%)
 dttl: 211 (0.01%)
 sloss: 2540258 (90.79%)
 dloss: 211 (0.01%)
 service: 209 (0.01%)
 sload: 211 (0.01%)
 dload: 211 (0.01%)
 spkts: 211 (0.01%)
 dpkts: 211 (0.01%)
 swin: 211 (0.01%)
 dwin: 211 (0.01%)
 stcpb: 211 (0.01%)
 dtcpb: 211 (0.01%)
 smeansz: 211 (0.01%)
 dmeansz: 211 (0.01%)
 sjit: 211 (0.01%)
 djit: 211 (0.01%)
 stime: 211 (0.01%)
 ltime: 211 (0.01%)
 sintpkt: 211 (0.01%)
 dintpkt: 211 (0.01%)
 tcprtt: 211 (0.01%)
 synack: 211 (0.01%)
 ackdat: 211 (0.01%)
 is_sm_ips_ports: 211 (0.01%)
 ct_state_ttl: 211 (0.01%)
 ct_flw_http_mthd: 1348356 (48.19%)
 is_ftp_login: 1430090 (51.11%)
 ct_ftp_cmd: 1430090 (51.11%)
 ct_srv_src: 211 (0.01%)
 ct_srv_dst: 211 (0.01%)
 ct_dst_ltm: 211 (0.01%)
 ct_src_ltm: 257884 (9.22%)
 ct_src_dport_ltm: 211 (0.01%)
 ct_dst_sport_ltm: 257884 (9.22%)
 ct_dst_src_ltm: 257884 (9.22%)
 attack: 2476648 (88.52%)
 label: 257884 (9.22%)
===========================
- Duplicates: [585513] (20.93%)
============================
Column Names & Types:
Column Names & Types:
srcip                object
sport               float64
dstip                object
dstp                float64
proto                object
state                object
dur                 float64
sbytes              float64
dbytes              float64
sttl                float64
dttl                float64
sloss               float64
dloss               float64
service              object
sload               float64
dload               float64
spkts               float64
dpkts               float64
swin                float64
dwin                float64
stcpb               float64
dtcpb               float64
smeansz             float64
dmeansz             float64
sjit                float64
djit                float64
stime               float64
ltime               float64
sintpkt             float64
dintpkt             float64
tcprtt              float64
synack              float64
ackdat              float64
is_sm_ips_ports     float64
ct_state_ttl        float64
ct_flw_http_mthd    float64
is_ftp_login        float64
ct_ftp_cmd          float64
ct_srv_src          float64
ct_srv_dst          float64
ct_dst_ltm          float64
ct_src_ltm          float64
ct_src_dport_ltm    float64
ct_dst_sport_ltm    float64
ct_dst_src_ltm      float64
attack               object
label               float64
dtype: object


### Outliers Detected
- Total Outliers (IQR Method): [11.48%] (321283 samples)
- Columns with outliers: 
 dbytes: 30623 (30.62%)
sjit: 22569 (22.57%)
ct_state_ttl: 22188 (22.19%)
dloss: 20337 (20.34%)
ct_dst_sport_ltm: 20213 (20.21%)
sintpkt: 19493 (19.49%)
ct_src_dport_ltm: 18909 (18.91%)
sbytes: 17574 (17.57%)
dintpkt: 17146 (17.15%)
djit: 15131 (15.13%)

### Feature Statistics
              sport           dstp           dur  ...  ct_dst_sport_ltm  ct_dst_src_ltm         label
count  2.539743e+06  257673.000000  2.797720e+06  ...      2.540047e+06    2.540047e+06  2.540047e+06
mean   1.123510e+04      19.777144  3.439766e+04  ...      3.592729e+00    6.845886e+00  1.264870e-01
std    1.843821e+04     135.947152  1.599091e+05  ...      6.174445e+00    1.125828e+01  3.323975e-01
min    0.000000e+00       1.000000  0.000000e+00  ...      1.000000e+00    1.000000e+00  0.000000e+00
25%    5.300000e+01       2.000000  1.620000e+02  ...      1.000000e+00    1.000000e+00  0.000000e+00
50%    8.000000e+01       4.000000  1.644000e+03  ...      1.000000e+00    2.000000e+00  0.000000e+00
75%    1.497000e+04      12.000000  1.036700e+04  ...      1.000000e+00    5.000000e+00  0.000000e+00
max    6.553500e+04   10646.000000  1.465753e+07  ...      6.000000e+01    6.700000e+01  1.000000e+00



### Correlation Insights
- Highly correlated features (>0.8): [list pairs]
- Recommendation: Consider removing one from highly correlated pairs

## Protocol Distribution
TCP: 19,726 (0.71%)
UDP: 6 (0.00%)
ICMP: 15 (0.00%)
Other: 2,778,184 (99.29%)

## Next Steps (Phase 1.3)
1. Handle class imbalance using SMOTE (if ratio < 0.3)
2. Engineer domain-specific features from UNSW-NB15
3. Normalize/scale numeric features
4. Remove low-variance features
5. Verify feature compatibility with XGBoost model
```

---

## 📊 Expected Outputs

```
data/
├── raw/
│   ├── UNSW-NB15_1.CSV
│   ├── UNSW-NB15_2.CSV
│   └── ... (additional UNSW-NB15 files)
├── processed/
│   ├── label_distribution.png
│   ├── protocol_distribution.png
│   ├── correlation_matrix.png
│   └── feature_distributions.png
├── train/
│   ├── train.csv
│   └── val.csv
└── test/
    └── test.csv