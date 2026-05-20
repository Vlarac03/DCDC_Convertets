# DC/DC Converter Study Tool

> **Note: The app is entirely in Catalan 🇨🇦**

A Streamlit web app for studying and designing DC/DC power converters (Buck, Boost, Buck-Boost) in both continuous (CCM) and discontinuous (DCM) conduction modes.

---

## Features


- **Interactive circuit diagrams** for each topology
- **8 input modes** — classic (Vi, D, L, C, R, f), by power, by resistance, by ripple %, Ton/Toff, minimum f, minimum L over a range, and full range design
- **Input validation** with warnings for impossible operating points
- **Numerical results** — Vo, Io, ΔIL, IL_max/min, ΔVo, critical L and C
- **Simulated waveforms** — 8 signals over 2 switching periods
- **Symbolic waveforms** — standard shapes with variable labels (Vi, Vo, IL_med, ΔIL/2...)
- **Step-by-step resolution** with formulas and numeric substitution, tailored to each problem type
- **Full theoretical derivations** for CCM and DCM
---

## Run locally

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
pip install -r requirements.txt
streamlit run app.py