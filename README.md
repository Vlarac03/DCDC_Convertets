# DC/DC Converter Study Tool

> **Note: The app is entirely in Catalan 🇨🇦**

A Streamlit web app for studying and designing DC/DC power converters (Buck, Boost, Buck-Boost) in both continuous (CCM) and discontinuous (DCM) conduction modes.

---

## Features

- **Interactive circuit diagrams** for each topology
- **4 input modes** — classic (Vi, D, L, C, R, f), by power, by resistance, or by ripple %
- **Numerical results** — Vo, Io, ΔIL, IL_max/min, ΔVo, critical L and C
- **Simulated waveforms** — 8 signals over 2 switching periods
- **Step-by-step resolution** with formulas and numeric substitution
- **Full theoretical derivations** for CCM and DCM

---

## Run locally

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
pip install -r requirements.txt
streamlit run app.py
