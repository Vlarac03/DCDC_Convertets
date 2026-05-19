# ⚡ Convertidors DC/DC — Eina d'estudi interactiva

Aplicació web interactiva per a l'anàlisi i disseny de convertidors de potència DC/DC (Buck, Boost i Buck-Boost), desenvolupada amb [Streamlit](https://streamlit.io).

🔗 **[Prova l'aplicació en viu →](https://YOUR-APP-NAME.streamlit.app)**

---

## 📸 Captura de pantalla

> *(afegeix aquí una captura un cop desplegada)*

---

## 🚀 Funcionalitats

### Topologies suportades
- **Buck** (reductor de tensió)
- **Boost** (elevador de tensió)
- **Buck-Boost** (reductor-elevador, polaritat invertida)

### Modes de conducció
- **MCC** — Mode de Conducció Contínua
- **MCD** — Mode de Conducció Discontínua

### Tipus d'enunciat
| Tipus | Paràmetres d'entrada |
|-------|---------------------|
| Clàssic | Vi, D, L, C, R, f |
| Per Potència | Vi, Vo, P, ΔIL, f, C |
| Per Resistència | Vi, Vo, R, ΔIL%, f, C |
| Disseny per % | Vi, Vo, P, f, %ΔIL, %ΔVo |

### Contingut de l'aplicació

**🔢 Resultats Numèrics**
- Esquema de circuit SVG interactiu
- Mètriques principals: Vo, Io, ΔIL, IL_max, IL_min, ΔVo...
- Paràmetres crítics: L_crit, Io_crit, C_mín
- Cronogrames simulats de 8 senyals (V_sw, I_sw, V_L, I_L, V_D, I_D, V_C, I_C) per a 2 períodes

**📋 Procediment Pas a Pas**
- Resolució numèrica completa amb els valors actuals
- Cada pas mostra la fórmula, el raonament i el resultat

**📐 Fórmules & Derivacions**
- Derivació teòrica de totes les expressions (MCC i MCD)
- Comparativa de formes d'ona IL entre modes
- Panells expandibles per topologia i mode

---

## 🛠️ Instal·lació local

### Requisits
- Python 3.10 o superior
- pip

### Passos

```bash
# 1. Clona el repositori
git clone https://github.com/EL-TEU-USUARI/EL-TEU-REPO.git
cd EL-TEU-REPO

# 2. (Opcional) Crea un entorn virtual
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

# 3. Instal·la les dependències
pip install -r requirements.txt

# 4. Executa l'aplicació
streamlit run app.py
```

L'aplicació s'obrirà automàticament a `http://localhost:8501`.

---

## ☁️ Desplegament a Streamlit Cloud (gratuït)

1. Fes un **fork** o puja aquest repositori al teu GitHub
2. Ves a [share.streamlit.io](https://share.streamlit.io) i inicia sessió amb GitHub
3. Clica **"New app"** → selecciona el repositori → `app.py` → **Deploy**
4. En 2-3 minuts l'aplicació estarà en línia amb una URL pública

---

## 📦 Dependències

| Paquet | Versió mínima | Ús |
|--------|---------------|----|
| `streamlit` | 1.32.0 | Framework web |
| `numpy` | 1.26.0 | Càlculs numèrics |
| `matplotlib` | 3.8.0 | Generació de gràfiques |

---

## 🎓 Context acadèmic

Eina creada com a suport per a l'estudi de **convertidors de commutació DC/DC** en assignatures d'electrònica de potència. Cobreix el temari habitual de:
- Anàlisi en règim permanent (MCC i MCD)
- Disseny de components (L i C)
- Formes d'ona i cronogrames
- Condicions frontera MCC/MCD

---

## 📄 Llicència

MIT License — lliure per a ús educatiu i personal.
