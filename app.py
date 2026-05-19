import matplotlib
matplotlib.use('Agg')  # non-interactive backend: avoids ScriptRunContext warnings

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# page config
st.set_page_config(
    page_title="Convertidors DC/DC",
    layout="wide",
    page_icon="⚡",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { font-size: 0.95rem; padding: 8px 18px; border-radius: 8px 8px 0 0; }

    /* ── Step-by-step procedure box ── */
    .step-box {
        background: linear-gradient(135deg, #0d1b2a 0%, #112233 100%);
        border: 1px solid #1e3a5f;
        border-left: 4px solid #4c9be8;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
        font-family: 'JetBrains Mono', monospace;
    }
    .step-number {
        color: #4c9be8;
        font-weight: 700;
        font-size: 0.8rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .step-title {
        color: #7ecbff;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 4px;
        font-family: 'Outfit', sans-serif;
    }
    .step-formula {
        color: #c8e6ff;
        font-size: 0.9rem;
        margin: 4px 0;
        padding: 4px 8px;
        background: rgba(76, 155, 232, 0.08);
        border-radius: 4px;
    }
    .step-result {
        color: #64ffb4;
        font-weight: 700;
        font-size: 1rem;
        margin-top: 6px;
        padding: 4px 8px;
        background: rgba(100, 255, 180, 0.08);
        border-radius: 4px;
    }
    .step-note {
        color: #ffcb6b;
        font-size: 0.82rem;
        margin-top: 4px;
        font-style: italic;
    }

    /* ── Crit box ── */
    .crit-box {
        background: linear-gradient(135deg, #1a1030 0%, #22103a 100%);
        border: 1px solid #4a2060;
        border-left: 4px solid #c97de8;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
    }

    /* ── Warning box ── */
    .warn-box {
        background: linear-gradient(135deg, #1e1500 0%, #2a1e00 100%);
        border: 1px solid #604020;
        border-left: 4px solid #f0a020;
        border-radius: 8px;
        padding: 10px 16px;
        margin: 6px 0;
        color: #ffd580;
        font-size: 0.88rem;
    }

    /* ── Section header ── */
    .sec-header {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.05rem;
        color: #ffffff;
        padding: 6px 12px;
        background: rgba(255,255,255,0.04);
        border-radius: 6px;
        margin: 14px 0 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }
</style>
""", unsafe_allow_html=True)

# sidebar
st.sidebar.header("⚙️ Entrada de dades")

topo = st.sidebar.selectbox("Topologia", ["Buck", "Boost", "Buck-Boost"])
mode = st.sidebar.selectbox("Mode de conducció", ["MCC (Continu)", "MCD (Discontinu)"])

tipus = st.sidebar.selectbox(
    "Tipus d'enunciat",
    [
        "Clàssic (Vi, D, L, C, R, f)",
        "Per Potència (Vi, Vo, P, ΔIL, f, C)",
        "Per Resistència (Vi, Vo, R, ΔIL, f, C)",
        "Disseny per ΔIL% i ΔVo% (Vi, Vo, P, f, %ΔIL, %ΔVo)",
    ]
)

st.sidebar.divider()

# dynamic inputs depending on problem type
deduced_info = {}  # stores derived values to display as info banner

if tipus == "Clàssic (Vi, D, L, C, R, f)":
    Vi     = st.sidebar.number_input("Tensió entrada Vᵢ (V)", value=24.0, step=1.0, min_value=0.1)
    D      = st.sidebar.slider("Cicle de treball D", 0.05, 0.95, 0.55, 0.01)
    L_uH   = st.sidebar.number_input("Inductància L (µH)", value=250.0, step=10.0, min_value=0.1)
    C_uF   = st.sidebar.number_input("Capacitat C (µF)", value=75.0, step=5.0, min_value=0.1)
    R      = st.sidebar.number_input("Resistència R (Ω)", value=20.0, step=1.0, min_value=0.01)
    f_kHz  = st.sidebar.number_input("Freqüència f (kHz)", value=40.0, step=1.0, min_value=0.1)
    L, C, f, T = L_uH*1e-6, C_uF*1e-6, f_kHz*1e3, 1/(f_kHz*1e3)

elif tipus == "Per Potència (Vi, Vo, P, ΔIL, f, C)":
    Vi     = st.sidebar.number_input("Tensió entrada Vᵢ (V)", value=10.0, step=1.0, min_value=0.1)
    Vo_t   = st.sidebar.number_input("Tensió sortida Vo (V)", value=50.0, step=1.0, min_value=0.1)
    P      = st.sidebar.number_input("Potència sortida P (W)", value=50.0, step=5.0, min_value=0.1)
    dIL_pc = st.sidebar.number_input("Rizat ΔIL (% de IL_med)", value=50.0, step=5.0, min_value=1.0, max_value=200.0)
    f_kHz  = st.sidebar.number_input("Freqüència f (kHz)", value=40.0, step=1.0, min_value=0.1)
    dVo_pc = st.sidebar.number_input("Rizat ΔVo (% de Vo)", value=2.0, step=0.5, min_value=0.01)
    f, T   = f_kHz*1e3, 1/(f_kHz*1e3)
    Io_t   = P / Vo_t
    R      = Vo_t**2 / P
    if topo == "Buck":
        D = np.clip(Vo_t / Vi, 0.05, 0.95)
        IL_med_t = Io_t
    elif topo == "Boost":
        D = np.clip(1 - Vi/Vo_t, 0.05, 0.95)
        IL_med_t = Io_t / (1-D)
    else:
        D = np.clip(Vo_t / (Vi + Vo_t), 0.05, 0.95)
        IL_med_t = Io_t / (1-D)
    dIL_val = (dIL_pc/100) * IL_med_t
    if topo == "Buck":
        L = (Vi - Vo_t)*D*T / dIL_val
    else:
        L = Vi*D*T / dIL_val
    L_uH   = L*1e6
    if topo == "Buck":
        dVo_val = dIL_val / (8*f)
        C       = dVo_val / (dVo_pc/100 * Vo_t)
    elif topo == "Boost":
        C = Io_t*D / (f * (dVo_pc/100*Vo_t))
    else:
        C = Io_t*D / (f * (dVo_pc/100*Vo_t))
    C_uF   = C*1e6
    deduced_info = {"D": D, "R": R, "L_uH": L_uH, "C_uF": C_uF,
                    "dIL_val": dIL_val, "dVo_val": dVo_pc/100*Vo_t}

elif tipus == "Per Resistència (Vi, Vo, R, ΔIL, f, C)":
    Vi     = st.sidebar.number_input("Tensió entrada Vᵢ (V)", value=24.0, step=1.0, min_value=0.1)
    Vo_t   = st.sidebar.number_input("Tensió sortida Vo (V)", value=36.0, step=1.0, min_value=0.1)
    R      = st.sidebar.number_input("Resistència R (Ω)", value=10.0, step=1.0, min_value=0.01)
    dIL_pc = st.sidebar.number_input("Corrent mínim IL_min (% de IL_med)", value=30.0, step=5.0, min_value=0.0, max_value=99.9)
    f_kHz  = st.sidebar.number_input("Freqüència f (kHz)", value=50.0, step=1.0, min_value=0.1)
    dVo_pc = st.sidebar.number_input("Rizat ΔVo (% de Vo)", value=1.0, step=0.5, min_value=0.01)
    C_uF   = st.sidebar.number_input("Capacitat C (µF) [0=calcular]", value=0.0, step=10.0, min_value=0.0)
    f, T   = f_kHz*1e3, 1/(f_kHz*1e3)
    if topo == "Buck":
        D = np.clip(Vo_t / Vi, 0.05, 0.95)
        IL_med_t = Vo_t / R
    elif topo == "Boost":
        D = np.clip(1 - Vi/Vo_t, 0.05, 0.95)
        IL_med_t = (Vo_t/R) / (1-D)
    else:
        D = np.clip(Vo_t / (Vi + Vo_t), 0.05, 0.95)
        IL_med_t = (Vo_t/R) / (1-D)
    # IL_min = dIL_pc% of IL_med → ΔIL = 2*(IL_med - IL_min) = 2*IL_med*(1 - dIL_pc/100)
    dIL_val = 2 * IL_med_t * (1 - dIL_pc/100)
    if topo == "Buck":
        L = (Vi - Vo_t)*D*T / dIL_val if dIL_val > 0 else 1e-3
    else:
        L = Vi*D*T / dIL_val if dIL_val > 0 else 1e-3
    L_uH   = L*1e6
    Io_t   = Vo_t / R
    if C_uF == 0.0:
        if topo == "Buck":
            C = dIL_val / (8*f*(dVo_pc/100*Vo_t))
        else:
            C = Io_t*D / (f*(dVo_pc/100*Vo_t))
        C_uF = C*1e6
    else:
        C = C_uF * 1e-6
    deduced_info = {"D": D, "L_uH": L_uH, "C_uF": C_uF,
                    "dIL_val": dIL_val, "IL_med_t": IL_med_t,
                    "IL_min_t": IL_med_t*(dIL_pc/100)}

else:  # design by ripple percentages
    Vi     = st.sidebar.number_input("Tensió entrada Vᵢ (V)", value=24.0, step=1.0, min_value=0.1)
    Vo_t   = st.sidebar.number_input("Tensió sortida Vo (V)", value=12.0, step=1.0, min_value=0.1)
    P      = st.sidebar.number_input("Potència sortida P (W)", value=60.0, step=5.0, min_value=0.1)
    dIL_pc = st.sidebar.number_input("Rizat màx ΔIL (% de IL_med)", value=20.0, step=5.0, min_value=1.0)
    dVo_pc = st.sidebar.number_input("Rizat màx ΔVo (% de Vo)", value=2.0, step=0.5, min_value=0.01)
    f_kHz  = st.sidebar.number_input("Freqüència f (kHz)", value=40.0, step=1.0, min_value=0.1)
    f, T   = f_kHz*1e3, 1/(f_kHz*1e3)
    R      = Vo_t**2 / P
    Io_t   = P / Vo_t
    if topo == "Buck":
        D = np.clip(Vo_t / Vi, 0.05, 0.95)
        IL_med_t = Io_t
        dIL_val  = (dIL_pc/100)*IL_med_t
        L = (Vi - Vo_t)*D*T / dIL_val
        C = dIL_val / (8*f*(dVo_pc/100*Vo_t))
    elif topo == "Boost":
        D = np.clip(1 - Vi/Vo_t, 0.05, 0.95)
        IL_med_t = Io_t/(1-D)
        dIL_val  = (dIL_pc/100)*IL_med_t
        L = Vi*D*T / dIL_val
        C = Io_t*D / (f*(dVo_pc/100*Vo_t))
    else:
        D = np.clip(Vo_t/(Vi+Vo_t), 0.05, 0.95)
        IL_med_t = Io_t/(1-D)
        dIL_val  = (dIL_pc/100)*IL_med_t
        L = Vi*D*T / dIL_val
        C = Io_t*D / (f*(dVo_pc/100*Vo_t))
    L_uH, C_uF = L*1e6, C*1e6
    deduced_info = {"D": D, "R": R, "L_uH": L_uH, "C_uF": C_uF, "dIL_val": dIL_val}

# main calculation function
def calcular(topo, mode, Vi, D, L, C, R, f):
    T = 1/f
    if topo == "Buck":
        if "MCC" in mode:
            Vo = D * Vi
            Io = Vo / R
            IL_med = Io
            dIL = (Vi - Vo) * D * T / L
        else:
            K  = 2*L*f/R
            Vo = Vi * (2 / (1 + np.sqrt(1 + 4*D**2/K)))
            Io = Vo / R
            dIL    = (Vi - Vo) * D * T / L
            IL_med = dIL * D / 2  # average current in DCM
        Lcrit  = (1-D)*R / (2*f)
        Io_crit = Vo*(1-D) / (2*L*f)
        dVo    = dIL / (8*f*C) if C > 0 else 0
        Ccrit  = dIL / (8*f*(Vo*0.02)) if Vo > 0 else 0

    elif topo == "Boost":
        if "MCC" in mode:
            Vo = Vi / (1-D)
            Io = Vo / R
            IL_med = Io / (1-D)
            dIL = Vi * D * T / L
        else:
            K  = 2*L*f/R
            Vo = Vi * (1 + np.sqrt(1 + 4*D**2/K)) / 2
            Io = Vo / R
            dIL    = Vi * D * T / L
            IL_med = dIL * D / 2
        Lcrit   = D*(1-D)**2*R / (2*f)
        Io_crit = Vi*D*(1-D) / (2*L*f)
        dVo     = Io*D / (f*C) if C > 0 else 0
        Ccrit   = Io*D / (f*(Vo*0.02)) if Vo > 0 else 0

    else:  # Buck-Boost
        if "MCC" in mode:
            Vo = Vi * D / (1-D)
            Io = Vo / R
            IL_med = Io / (1-D)
            dIL = Vi * D * T / L
        else:
            K  = 2*L*f/R
            Vo = Vi * D / np.sqrt(K)
            Io = Vo / R
            dIL    = Vi * D * T / L
            IL_med = dIL * D / 2
        Lcrit   = (1-D)**2*R / (2*f)
        Io_crit = Vi*D / (2*L*f) * (1-D)**2
        dVo     = Io*D / (f*C) if C > 0 else 0
        Ccrit   = Io*D / (f*(Vo*0.01)) if Vo > 0 else 0

    IL_max = IL_med + dIL/2
    IL_min = max(0.0, IL_med - dIL/2) if "MCC" in mode else 0.0

    Vsw_max = Vi if topo=="Buck" else (Vo if topo=="Boost" else Vi+Vo)
    VD_max  = Vsw_max

    return dict(Vo=Vo, Io=Io, IL_med=IL_med, dIL=dIL,
                IL_max=IL_max, IL_min=IL_min,
                Vsw_max=Vsw_max, VD_max=VD_max,
                Lcrit=Lcrit*1e6, Io_crit=Io_crit,
                Ccrit=Ccrit*1e6, dVo=dVo, T=T)

V = calcular(topo, mode, Vi, D, L, C, R, f)
real_mode  = "MCC" if L_uH > V['Lcrit'] else "MCD"
color_mode = "🟢" if real_mode == "MCC" else "🟡"

# page title and mode indicator
st.title(f"⚡ Convertidor {topo}  —  {mode}")
st.caption(f"{color_mode} Mode real: **{real_mode}**  |  L_crit = {V['Lcrit']:.1f} µH  |  "
           f"f = {f_kHz:.0f} kHz  |  D = {D:.3f}  |  Vo = {V['Vo']:.3f} V")

if deduced_info:
    parts = []
    if "D"    in deduced_info: parts.append(f"D = **{deduced_info['D']:.3f}**")
    if "R"    in deduced_info: parts.append(f"R = **{deduced_info['R']:.2f} Ω**")
    if "L_uH" in deduced_info: parts.append(f"L = **{deduced_info['L_uH']:.2f} µH**")
    if "C_uF" in deduced_info: parts.append(f"C = **{deduced_info['C_uF']:.2f} µF**")
    st.info("ℹ️ **Valors deduïts de l'enunciat:** " + "  |  ".join(parts))

# SVG circuit diagrams
def esquema_buck():
    return """
<svg viewBox="0 0 560 210" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:560px;display:block;margin:auto">
  <style>
    .w{stroke:#4c9be8;stroke-width:2;fill:none}
    .c{stroke:#ccc;stroke-width:1.8;fill:none}
    .l{font:12px 'JetBrains Mono',monospace;fill:#aaa;text-anchor:middle}
    .n{font:11px 'JetBrains Mono',monospace;fill:#7ecbff;text-anchor:middle}
  </style>
  <!-- Font Vi -->
  <circle cx="45" cy="105" r="24" class="c"/>
  <text x="45" y="100" class="l">+</text><text x="45" y="116" class="l">−</text>
  <text x="45" y="170" class="n">Vᵢ</text>
  <!-- Fil superior esquerra -->
  <line x1="45" y1="81" x2="45" y2="45" class="w"/>
  <line x1="45" y1="45" x2="155" y2="45" class="w"/>
  <!-- Switch -->
  <circle cx="158" cy="45" r="4" fill="#f0a020"/>
  <line x1="158" y1="45" x2="190" y2="22" stroke="#f0a020" stroke-width="2.2"/>
  <circle cx="205" cy="45" r="4" fill="#f0a020" fill-opacity="0.4"/>
  <text x="175" y="16" class="n" style="fill:#f0a020">S</text>
  <!-- Fil post-switch -->
  <line x1="205" y1="45" x2="245" y2="45" class="w"/>
  <!-- Díode freewheeling: càtode a dalt (node del switch), ànode a baix (GND) -->
  <line x1="245" y1="45" x2="245" y2="75" class="w"/>
  <line x1="225" y1="75" x2="265" y2="75" stroke="#e05050" stroke-width="2.5"/>
  <polygon points="225,105 265,105 245,75" fill="#e05050" stroke="#e05050" stroke-width="1.2"/>
  <line x1="245" y1="105" x2="245" y2="165" class="w"/>
  <text x="278" y="95" class="n" style="fill:#e05050;text-anchor:start">D</text>
  <!-- Bobina -->
  <line x1="245" y1="45" x2="300" y2="45" class="w"/>
  <path d="M300,45 q10,-18 20,0 q10,-18 20,0 q10,-18 20,0" class="c" stroke="#4caf50"/>
  <line x1="360" y1="45" x2="400" y2="45" class="w"/>
  <text x="330" y="25" class="n" style="fill:#4caf50">L</text>
  <!-- Nodo de sortida -->
  <circle cx="400" cy="45" r="3" fill="#4c9be8"/>
  <!-- Condensador -->
  <line x1="400" y1="45" x2="400" y2="80" class="w"/>
  <line x1="378" y1="80" x2="422" y2="80" stroke="#c897e8" stroke-width="2.8"/>
  <line x1="378" y1="90" x2="422" y2="90" stroke="#c897e8" stroke-width="2.8"/>
  <line x1="400" y1="90" x2="400" y2="165" class="w"/>
  <text x="432" y="90" class="n" style="fill:#c897e8;text-anchor:start">C</text>
  <!-- Resistència -->
  <line x1="480" y1="45" x2="480" y2="75" class="w"/>
  <rect x="462" y="75" width="36" height="55" rx="4" class="c" stroke="#e8c060"/>
  <line x1="480" y1="130" x2="480" y2="165" class="w"/>
  <text x="510" y="107" class="n" style="fill:#e8c060;text-anchor:start">R</text>
  <!-- Connexió Vo -->
  <line x1="400" y1="45" x2="480" y2="45" class="w"/>
  <text x="480" y="32" class="n" style="fill:#64ffb4">+Vo</text>
  <!-- GND -->
  <line x1="45" y1="129" x2="45" y2="165" class="w"/>
  <line x1="45" y1="165" x2="480" y2="165" class="w"/>
  <line x1="245" y1="165" x2="400" y2="165" class="w"/>
</svg>"""

def esquema_boost():
    return """
<svg viewBox="0 0 560 210" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:560px;display:block;margin:auto">
  <style>
    .w{stroke:#4c9be8;stroke-width:2;fill:none}
    .c{stroke:#ccc;stroke-width:1.8;fill:none}
    .l{font:12px 'JetBrains Mono',monospace;fill:#aaa;text-anchor:middle}
    .n{font:11px 'JetBrains Mono',monospace;fill:#7ecbff;text-anchor:middle}
  </style>
  <!-- Font Vi -->
  <circle cx="45" cy="105" r="24" class="c"/>
  <text x="45" y="100" class="l">+</text><text x="45" y="116" class="l">−</text>
  <text x="45" y="170" class="n">Vᵢ</text>
  <!-- Fil superior -->
  <line x1="45" y1="81" x2="45" y2="45" class="w"/>
  <line x1="45" y1="45" x2="90" y2="45" class="w"/>
  <!-- Bobina -->
  <path d="M90,45 q10,-18 20,0 q10,-18 20,0 q10,-18 20,0" class="c" stroke="#4caf50"/>
  <line x1="150" y1="45" x2="220" y2="45" class="w"/>
  <text x="120" y="25" class="n" style="fill:#4caf50">L</text>
  <!-- Node mig -->
  <circle cx="220" cy="45" r="3" fill="#4c9be8"/>
  <!-- Switch (vertical, entre node mig i GND) -->
  <line x1="220" y1="45" x2="220" y2="80" class="w"/>
  <circle cx="220" cy="83" r="4" fill="#f0a020"/>
  <line x1="220" y1="83" x2="244" y2="115" stroke="#f0a020" stroke-width="2.2"/>
  <circle cx="220" cy="128" r="4" fill="#f0a020" fill-opacity="0.4"/>
  <line x1="220" y1="128" x2="220" y2="165" class="w"/>
  <text x="252" y="108" class="n" style="fill:#f0a020;text-anchor:start">S</text>
  <!-- Díode (horitzontal, cap a la dreta) -->
  <line x1="220" y1="45" x2="265" y2="45" class="w"/>
  <polygon points="265,28 265,62 290,45" fill="#e05050" stroke="#e05050"/>
  <line x1="290" y1="28" x2="290" y2="62" stroke="#e05050" stroke-width="2"/>
  <line x1="290" y1="45" x2="360" y2="45" class="w"/>
  <text x="278" y="22" class="n" style="fill:#e05050">D</text>
  <!-- Node sortida -->
  <circle cx="360" cy="45" r="3" fill="#4c9be8"/>
  <!-- Condensador -->
  <line x1="360" y1="45" x2="360" y2="80" class="w"/>
  <line x1="338" y1="80" x2="382" y2="80" stroke="#c897e8" stroke-width="2.8"/>
  <line x1="338" y1="90" x2="382" y2="90" stroke="#c897e8" stroke-width="2.8"/>
  <line x1="360" y1="90" x2="360" y2="165" class="w"/>
  <text x="390" y="90" class="n" style="fill:#c897e8;text-anchor:start">C</text>
  <!-- Resistència -->
  <line x1="480" y1="45" x2="480" y2="75" class="w"/>
  <rect x="462" y="75" width="36" height="55" rx="4" class="c" stroke="#e8c060"/>
  <line x1="480" y1="130" x2="480" y2="165" class="w"/>
  <text x="510" y="107" class="n" style="fill:#e8c060;text-anchor:start">R</text>
  <!-- Connexió Vo -->
  <line x1="360" y1="45" x2="480" y2="45" class="w"/>
  <text x="480" y="32" class="n" style="fill:#64ffb4">+Vo</text>
  <!-- GND -->
  <line x1="45" y1="129" x2="45" y2="165" class="w"/>
  <line x1="45" y1="165" x2="480" y2="165" class="w"/>
</svg>"""

def esquema_buckboost():
    # correct topology: Vi — S — L — node(D→) — Vo (inverted polarity)
    return """
<svg viewBox="0 0 580 220" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:580px;display:block;margin:auto">
  <style>
    .w{stroke:#4c9be8;stroke-width:2;fill:none}
    .c{stroke:#ccc;stroke-width:1.8;fill:none}
    .l{font:12px 'JetBrains Mono',monospace;fill:#aaa;text-anchor:middle}
    .n{font:11px 'JetBrains Mono',monospace;fill:#7ecbff;text-anchor:middle}
  </style>
  <!-- Font Vi -->
  <circle cx="45" cy="110" r="24" class="c"/>
  <text x="45" y="105" class="l">+</text><text x="45" y="121" class="l">−</text>
  <text x="45" y="175" class="n">Vᵢ</text>
  <!-- Fil superior des de Vi -->
  <line x1="45" y1="86" x2="45" y2="50" class="w"/>
  <line x1="45" y1="50" x2="80" y2="50" class="w"/>
  <!-- Switch (sèrie, a la branca superior) -->
  <circle cx="83" cy="50" r="4" fill="#f0a020"/>
  <line x1="83" y1="50" x2="112" y2="28" stroke="#f0a020" stroke-width="2.2"/>
  <circle cx="127" cy="50" r="4" fill="#f0a020" fill-opacity="0.4"/>
  <text x="100" y="20" class="n" style="fill:#f0a020">S</text>
  <line x1="127" y1="50" x2="160" y2="50" class="w"/>
  <!-- Bobina (en sèrie després del switch) -->
  <path d="M160,50 q10,-18 20,0 q10,-18 20,0 q10,-18 20,0" class="c" stroke="#4caf50"/>
  <line x1="220" y1="50" x2="260" y2="50" class="w"/>
  <text x="190" y="28" class="n" style="fill:#4caf50">L</text>
  <!-- Node central (unió L, D, GND per switch) -->
  <circle cx="260" cy="50" r="3" fill="#4c9be8"/>
  <!-- Connexió node central a GND (retorn switch) -->
  <line x1="260" y1="50" x2="260" y2="175" class="w"/>
  <!-- Díode (del node central cap a la sortida, polaritat invertida → Vo negatiu) -->
  <!-- Corrent flueix de GND cap al node de sortida quan S obert -->
  <line x1="260" y1="50" x2="340" y2="50" class="w"/>
  <polygon points="340,33 340,67 365,50" fill="#e05050" stroke="#e05050"/>
  <line x1="365" y1="33" x2="365" y2="67" stroke="#e05050" stroke-width="2"/>
  <line x1="365" y1="50" x2="420" y2="50" class="w"/>
  <text x="352" y="25" class="n" style="fill:#e05050">D</text>
  <!-- Node sortida -->
  <circle cx="420" cy="50" r="3" fill="#4c9be8"/>
  <!-- Condensador (entre node sortida i GND) -->
  <line x1="420" y1="50" x2="420" y2="85" class="w"/>
  <line x1="398" y1="85" x2="442" y2="85" stroke="#c897e8" stroke-width="2.8"/>
  <line x1="398" y1="95" x2="442" y2="95" stroke="#c897e8" stroke-width="2.8"/>
  <line x1="420" y1="95" x2="420" y2="175" class="w"/>
  <text x="452" y="93" class="n" style="fill:#c897e8;text-anchor:start">C</text>
  <!-- Resistència (entre node sortida i GND) -->
  <line x1="510" y1="50" x2="510" y2="80" class="w"/>
  <rect x="492" y="80" width="36" height="55" rx="4" class="c" stroke="#e8c060"/>
  <line x1="510" y1="135" x2="510" y2="175" class="w"/>
  <text x="540" y="112" class="n" style="fill:#e8c060;text-anchor:start">R</text>
  <!-- Connexió node sortida a R -->
  <line x1="420" y1="50" x2="510" y2="50" class="w"/>
  <!-- Etiqueta Vo (node sortida és negatiu respecte GND) -->
  <text x="510" y="37" class="n" style="fill:#ff8080">−Vo</text>
  <!-- GND comú -->
  <line x1="45" y1="134" x2="45" y2="175" class="w"/>
  <line x1="45" y1="175" x2="510" y2="175" class="w"/>
  <!-- Nota polaritat -->
  <text x="290" y="195" class="n" style="fill:#ffcb6b;font-size:10px">⚠ Vo té polaritat invertida respecte Vᵢ</text>
</svg>"""

esquemes = {"Buck": esquema_buck, "Boost": esquema_boost, "Buck-Boost": esquema_buckboost}

# tabs
tab_vals, tab_proc, tab_vars = st.tabs([
    "🔢 Resultats Numèrics",
    "📋 Procediment Pas a Pas",
    "📐 Fórmules & Cronogrames"
])

# tab 1: numerical results and waveforms
with tab_vals:
    col_s, col_r = st.columns([1, 1.2])

    with col_s:
        st.subheader(f"Esquema: {topo}")
        st.markdown(esquemes[topo](), unsafe_allow_html=True)
        st.caption("🟠 Switch  ·  🔴 Díode  ·  🟢 Bobina  ·  🟣 Condensador  ·  🟡 Resistència")

    with col_r:
        st.subheader("Resultats numèrics")
        c1, c2, c3 = st.columns(3)
        c1.metric("Vo (V)",       f"{V['Vo']:.3f}")
        c2.metric("Io (A)",       f"{V['Io']:.3f}")
        c3.metric("ΔI_L (A)",     f"{V['dIL']:.4f}")
        c1.metric("I_L med (A)",  f"{V['IL_med']:.4f}")
        c2.metric("I_L màx (A)",  f"{V['IL_max']:.4f}")
        c3.metric("I_L mín (A)",  f"{V['IL_min']:.4f}")
        c1.metric("V_sw màx (V)", f"{V['Vsw_max']:.3f}")
        c2.metric("V_D màx (V)",  f"{V['VD_max']:.3f}")
        c3.metric("ΔVo (V)",      f"{V['dVo']:.5f}")

        st.divider()
        st.subheader("Paràmetres crítics MCC ↔ MCD")
        cc1, cc2, cc3 = st.columns(3)
        delta_L = L_uH - V['Lcrit']
        cc1.metric("L_crit (µH)", f"{V['Lcrit']:.2f}",
                   delta=f"{delta_L:+.2f} µH vs actual",
                   delta_color="normal")
        cc2.metric("Io_crit (A)", f"{V['Io_crit']:.4f}")
        cc3.metric("C_mín (µF)",  f"{V['Ccrit']:.2f}")

    st.divider()
    st.subheader("📊 Cronogrames simulats — 2 períodes")

    N = 1400
    T_val = V['T']
    t_arr = np.linspace(0, 2*T_val, N)
    dt = t_arr % T_val
    Vo_v, Io_v = V['Vo'], V['Io']
    IL_med_v, dIL_v = V['IL_med'], V['dIL']
    IL_max_v, IL_min_v = V['IL_max'], V['IL_min']

    D2_raw = (2*IL_med_v/dIL_v) - D if ("MCD" in mode and dIL_v > 0 and IL_med_v > 0) else (1-D)
    D2 = float(np.clip(D2_raw, 0, 1-D))

    v_L = np.zeros(N); i_L = np.zeros(N)
    v_sw = np.zeros(N); i_sw = np.zeros(N)
    v_D  = np.zeros(N); i_D  = np.zeros(N); i_C = np.zeros(N)

    for i, ti in enumerate(dt):
        on   = ti <= D*T_val
        off1 = (not on) and (ti <= (D+D2)*T_val)

        if topo == "Buck":
            if on:
                i_L[i] = IL_min_v + dIL_v*(ti/(D*T_val))
                v_L[i]=Vi-Vo_v; v_sw[i]=0; i_sw[i]=i_L[i]; v_D[i]=-Vi; i_D[i]=0
            elif off1:
                i_L[i] = IL_max_v - dIL_v*((ti-D*T_val)/(D2*T_val)) if D2>0 else IL_min_v
                v_L[i]=-Vo_v; v_sw[i]=Vi; i_sw[i]=0; v_D[i]=0; i_D[i]=i_L[i]
            else:
                i_L[i]=0; v_L[i]=0; v_sw[i]=Vi-Vo_v; i_sw[i]=0; v_D[i]=-Vo_v; i_D[i]=0
            i_C[i] = i_L[i] - Io_v

        elif topo == "Boost":
            if on:
                i_L[i] = IL_min_v + dIL_v*(ti/(D*T_val))
                v_L[i]=Vi; v_sw[i]=0; i_sw[i]=i_L[i]; v_D[i]=-Vo_v; i_D[i]=0; i_C[i]=-Io_v
            elif off1:
                i_L[i] = IL_max_v - dIL_v*((ti-D*T_val)/(D2*T_val)) if D2>0 else IL_min_v
                v_L[i]=Vi-Vo_v; v_sw[i]=Vo_v; i_sw[i]=0; v_D[i]=0; i_D[i]=i_L[i]; i_C[i]=i_L[i]-Io_v
            else:
                i_L[i]=0; v_L[i]=0; v_sw[i]=Vi; i_sw[i]=0; v_D[i]=Vi-Vo_v; i_D[i]=0; i_C[i]=-Io_v

        else:  # Buck-Boost
            if on:
                i_L[i] = IL_min_v + dIL_v*(ti/(D*T_val))
                v_L[i]=Vi; v_sw[i]=0; i_sw[i]=i_L[i]; v_D[i]=-(Vi+Vo_v); i_D[i]=0; i_C[i]=-Io_v
            elif off1:
                i_L[i] = IL_max_v - dIL_v*((ti-D*T_val)/(D2*T_val)) if D2>0 else IL_min_v
                v_L[i]=-Vo_v; v_sw[i]=Vi+Vo_v; i_sw[i]=0; v_D[i]=0; i_D[i]=i_L[i]; i_C[i]=i_L[i]-Io_v
            else:
                i_L[i]=0; v_L[i]=0; v_sw[i]=Vi; i_sw[i]=0; v_D[i]=-Vo_v; i_D[i]=0; i_C[i]=-Io_v

    t_us = t_arr * 1e6

    def graf(ax, t, y, color, title, ylabel, hlines=None):
        ax.plot(t, y, color=color, lw=1.8)
        ax.set_title(title, fontsize=10, pad=3, color='#ddd')
        ax.set_ylabel(ylabel, fontsize=8, color='#aaa')
        ax.set_xlabel("Temps (µs)", fontsize=8, color='#aaa')
        ax.grid(True, alpha=0.25, linestyle='--')
        ax.axhline(0, color='#555', lw=0.8)
        if hlines:
            for hv, lbl, hc in hlines:
                ax.axhline(hv, color=hc, lw=1.2, ls='--', alpha=0.8)
                ax.annotate(f"{lbl}={hv:.3f}", xy=(t[-1]*0.02, hv),
                            fontsize=7.5, color=hc, va='bottom')
        for k in [1, 2]:
            ax.axvline(k*T_val*1e6, color='#667', lw=0.9, ls=':', alpha=0.6)

    fig, axs = plt.subplots(4, 2, figsize=(14, 14), facecolor='#0e1117')
    for ax in axs.flat:
        ax.set_facecolor('#131825')
        ax.tick_params(colors='#888', labelsize=7.5)
        for sp in ax.spines.values(): sp.set_color('#2a2a3a')

    graf(axs[0,0], t_us, v_sw, '#f0a020', "V_sw — Tensió interruptor", "V")
    graf(axs[0,1], t_us, i_sw, '#f0a020', "I_sw — Corrent interruptor", "A",
         hlines=[(IL_max_v,'IL_max','#ff6060')])
    graf(axs[1,0], t_us, v_L,  '#4caf50', "V_L — Tensió bobina", "V")
    graf(axs[1,1], t_us, i_L,  '#4caf50', "I_L — Corrent bobina", "A",
         hlines=[(IL_max_v,'IL_max','#ff8080'),
                 (IL_min_v,'IL_min','#80a0ff'),
                 (IL_med_v,'IL_med','#ffff60')])
    graf(axs[2,0], t_us, v_D,  '#e05050', "V_D — Tensió díode", "V")
    graf(axs[2,1], t_us, i_D,  '#e05050', "I_D — Corrent díode", "A")
    graf(axs[3,0], t_us, np.full(N, Vo_v), '#c897e8', "V_C = Vo — Tensió sortida", "V")
    graf(axs[3,1], t_us, i_C, '#c897e8', "I_C — Corrent condensador", "A",
         hlines=[(0,'0','#666')])

    plt.tight_layout(pad=1.8)
    st.pyplot(fig)
    plt.close()


# tab 2: step-by-step resolution
with tab_proc:
    st.subheader(f"📋 Resolució pas a pas — {topo} en {mode}")
    st.markdown("Cada pas mostra la fórmula aplicada i el resultat numèric amb els valors actuals.")

    def step(n, title, formulas, result, note=None):
        html = f"""<div class="step-box">
<div class="step-number">PAS {n}</div>
<div class="step-title">{title}</div>"""
        for f_txt in formulas:
            html += f'<div class="step-formula">📐 {f_txt}</div>'
        html += f'<div class="step-result">✅ {result}</div>'
        if note:
            html += f'<div class="step-note">💡 {note}</div>'
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    # step 1: duty cycle and output voltage
    if topo == "Buck":
        step(1, "Cicle de treball i tensió de sortida",
             ["Origen: igualtat volt·segon a la bobina en règim permanent",
              "∫VL·dt = 0  →  (Vi−Vo)·D·T + (−Vo)·(1−D)·T = 0",
              "Vo = D · Vi   →   D = Vo / Vi",
              f"D = {V['Vo']:.3f} / {Vi:.1f} = {D:.3f}   |   Vo = {D:.3f} × {Vi:.1f} = {V['Vo']:.3f} V"],
             f"D = {D:.3f}   →   Vo = {V['Vo']:.3f} V",
             "En MCC ideal: Vo depèn únicament de D i Vi" if "MCC" in mode else
             "En MCD: Vo depèn també de K = 2Lf/R, no és fix per D")
    elif topo == "Boost":
        step(1, "Cicle de treball i tensió de sortida",
             ["Origen: igualtat volt·segon a la bobina en règim permanent",
              "∫VL·dt = 0  →  Vi·D·T + (Vi−Vo)·(1−D)·T = 0",
              "Vo = Vi / (1−D)   →   D = 1 − Vi/Vo",
              f"D = 1 − {Vi:.1f}/{V['Vo']:.3f} = {D:.3f}   |   Vo = {Vi:.1f}/(1−{D:.3f}) = {V['Vo']:.3f} V"],
             f"D = {D:.3f}   →   Vo = {V['Vo']:.3f} V",
             "En MCC: Vo > Vi sempre. Si D→1, Vo→∞ (en teoria)")
    else:
        step(1, "Cicle de treball i tensió de sortida",
             ["Origen: igualtat volt·segon a la bobina en règim permanent",
              "∫VL·dt = 0  →  Vi·D·T + (−Vo)·(1−D)·T = 0  (Vo és negatiu)",
              "|Vo| = Vi·D/(1−D)   →   D = |Vo|/(Vi+|Vo|)",
              f"D = {V['Vo']:.3f}/({Vi:.1f}+{V['Vo']:.3f}) = {D:.3f}   |   |Vo| = {Vi:.1f}·{D:.3f}/(1−{D:.3f}) = {V['Vo']:.3f} V"],
             f"D = {D:.3f}   →   |Vo| = {V['Vo']:.3f} V  (polaritat invertida)",
             "En Buck-Boost: si D < 0.5 → |Vo| < Vi; si D > 0.5 → |Vo| > Vi")

    # step 2: output current and power
    step(2, "Corrent de sortida i potència",
         ["Llei d'Ohm a la resistència de càrrega:",
          "Io = Vo / R",
          f"Io = {V['Vo']:.3f} V / {R:.2f} Ω = {V['Io']:.4f} A",
          f"Verificació potència: P = Vo·Io = Vo²/R = {V['Vo']:.3f}²/{R:.2f} = {V['Vo']**2/R:.2f} W"],
         f"Io = {V['Io']:.4f} A   |   P = {V['Vo']**2/R:.2f} W",
         "La potència de sortida s'obté com P = Vo·Io = Vo²/R = Io²·R")

    # step 3: average inductor current
    if topo == "Buck":
        step(3, "Corrent mig de la bobina",
             ["En Buck: el condensador no porta corrent DC en règim permanent",
              "→ tot el corrent de sortida passa per la bobina",
              "IL_med = Io   (per conservació de càrrega al condensador)",
              f"IL_med = Io = {V['Io']:.4f} A"],
             f"IL_med = {V['IL_med']:.4f} A",
             "Diferent del Boost/Buck-Boost on la bobina és a l'entrada")
    else:
        denom = f"(1−D) = (1−{D:.3f}) = {1-D:.3f}"
        step(3, "Corrent mig de la bobina",
             [f"En {topo}: la bobina és a l'entrada, porta tot el corrent d'entrada",
              "Per conservació d'energia (η=1): Pi = Po  →  Vi·IL_med = Vo·Io",
              "IL_med = Io / (1−D)   [també: IL_med = Vi·Io / (Vi·(1−D)) ]",
              f"IL_med = {V['Io']:.4f} / {denom} = {V['IL_med']:.4f} A"],
             f"IL_med = {V['IL_med']:.4f} A",
             f"El corrent mig de la bobina és {1/(1-D):.2f}× el corrent de sortida")

    # step 4: current ripple
    if topo == "Buck":
        step(4, "Rizat de corrent de la bobina ΔIL",
             ["Origen: equació de la bobina v_L = L·(diL/dt)  →  ΔiL = v_L·Δt/L",
              "Fase ON (S tancat): v_L = Vi−Vo, durada = D·T",
              "ΔIL = (Vi−Vo)·D·T / L  =  (Vi−Vo)·D / (L·f)",
              "Equivalent: ΔIL = Vo·(1−D) / (L·f)  [substituint Vo=D·Vi]",
              f"ΔIL = ({Vi:.1f}−{V['Vo']:.3f})·{D:.3f} / ({L_uH:.1f}×10⁻⁶·{f_kHz:.0f}×10³)",
              f"     = {Vi-V['Vo']:.3f}·{D:.3f} / {L*f:.2f} = {V['dIL']:.4f} A"],
             f"ΔIL = {V['dIL']:.4f} A  ({V['dIL']/V['IL_med']*100:.1f}% de IL_med)" if V['IL_med']>0 else f"ΔIL = {V['dIL']:.4f} A",
             "Fase OFF (S obert): ΔIL = Vo·(1−D)/(L·f) — ha de donar el mateix valor")
    else:
        step(4, "Rizat de corrent de la bobina ΔIL",
             ["Origen: equació de la bobina v_L = L·(diL/dt)  →  ΔiL = v_L·Δt/L",
              f"Fase ON (S tancat): v_L = Vi = {Vi:.1f} V, durada = D·T",
              "ΔIL = Vi·D·T / L  =  Vi·D / (L·f)",
              f"ΔIL = {Vi:.1f}·{D:.3f} / ({L_uH:.2f}×10⁻⁶·{f_kHz:.0f}×10³)",
              f"     = {Vi*D:.4f} / {L*f:.4f} = {V['dIL']:.4f} A"],
             f"ΔIL = {V['dIL']:.4f} A  ({V['dIL']/V['IL_med']*100:.1f}% de IL_med)" if V['IL_med']>0 else f"ΔIL = {V['dIL']:.4f} A",
             "Com més gran és L o f, menor és el rizat → disseny MCC més fàcil")

    # step 5: IL max and min
    step(5, "Corrents màxim i mínim de la bobina",
         ["La forma d'ona de IL és triangular (MCC) centrada en IL_med:",
          "IL_max = IL_med + ΔIL/2   (pic quan S es tanca o obre)",
          "IL_min = IL_med − ΔIL/2   (vall; ha de ser ≥0 per garantir MCC)",
          f"IL_max = {V['IL_med']:.4f} + {V['dIL']/2:.4f} = {V['IL_max']:.4f} A",
          f"IL_min = {V['IL_med']:.4f} − {V['dIL']/2:.4f} = {V['IL_min']:.4f} A"],
         f"IL_max = {V['IL_max']:.4f} A  |  IL_min = {V['IL_min']:.4f} A",
         "⚠️ IL_min ≈ 0 → al límit MCC/MCD. Augmenta L per assegurar MCC" if V['IL_min'] < 0.001 else
         f"IL_min = {V['IL_min']:.4f} A > 0  ✅ confirma MCC")

    # step 6: critical inductance
    if topo == "Buck":
        step(6, "Inductància crítica — frontera MCC/MCD",
             ["Condició MCC: IL_min ≥ 0  →  IL_med ≥ ΔIL/2",
              "Io ≥ Vo(1−D)/(2·L·f)  →  L ≥ (1−D)·R/(2·f)  =  L_crit",
              "L_crit = (1−D)·R / (2·f)",
              f"L_crit = (1−{D:.3f})·{R:.1f} / (2·{f_kHz:.0f}×10³) = {V['Lcrit']:.2f} µH"],
             f"L = {L_uH:.2f} µH {'>' if L_uH >= V['Lcrit'] else '<'} L_crit = {V['Lcrit']:.2f} µH → {'MCC ✅' if real_mode=='MCC' else 'MCD ⚠️'}",
             "Si L > L_crit: MCC. Si L < L_crit: MCD (corrent es fa zero durant la fase OFF)")
    elif topo == "Boost":
        step(6, "Inductància crítica — frontera MCC/MCD",
             ["Condició MCC: IL_min ≥ 0  →  IL_med ≥ ΔIL/2",
              "Io/(1−D) ≥ Vi·D/(2·L·f)  →  L ≥ D·(1−D)²·R/(2·f)  =  L_crit",
              "L_crit = D·(1−D)²·R / (2·f)",
              f"L_crit = {D:.3f}·(1−{D:.3f})²·{R:.1f} / (2·{f_kHz:.0f}×10³) = {V['Lcrit']:.2f} µH"],
             f"L = {L_uH:.2f} µH {'>' if L_uH >= V['Lcrit'] else '<'} L_crit = {V['Lcrit']:.2f} µH → {'MCC ✅' if real_mode=='MCC' else 'MCD ⚠️'}",
             "En Boost, L_crit depèn de D·(1−D)²: màxim a D≈0.33")
    else:
        step(6, "Inductància crítica — frontera MCC/MCD",
             ["Condició MCC: IL_min ≥ 0  →  L_crit = (1−D)²·R / (2·f)",
              "L_crit = (1−D)²·R / (2·f)",
              f"L_crit = (1−{D:.3f})²·{R:.1f} / (2·{f_kHz:.0f}×10³) = {V['Lcrit']:.2f} µH"],
             f"L = {L_uH:.2f} µH {'>' if L_uH >= V['Lcrit'] else '<'} L_crit = {V['Lcrit']:.2f} µH → {'MCC ✅' if real_mode=='MCC' else 'MCD ⚠️'}",
             "En Buck-Boost, L_crit = (1−D)²·R/(2f): cau molt ràpid amb D alt")

    # step 7: output voltage ripple
    if topo == "Buck":
        step(7, "Rizat de la tensió de sortida ΔVo",
             ["Origen: el condensador integra la part AC del corrent de la bobina",
              "iC = iL − Io  →  el condensador absorbeix el triangle de ΔIL",
              "Carrega/descarrega durant T/2: ΔVo = ΔQ/C = (ΔIL/2·T/2) / (2C)",
              "ΔVo = ΔIL / (8·f·C)  =  Vo·(1−D) / (8·L·C·f²)",
              f"ΔVo = {V['dIL']:.4f} / (8·{f_kHz:.0f}×10³·{C_uF:.1f}×10⁻⁶)",
              f"     = {V['dIL']:.4f} / {8*f*C:.6f} = {V['dVo']*1000:.4f} mV"],
             f"ΔVo = {V['dVo']*1000:.4f} mV  =  {V['dVo']/V['Vo']*100:.3f}% de Vo" if V['Vo']>0 else f"ΔVo = {V['dVo']:.5f} V",
             "Per reduir ΔVo: augmenta C (×2 → ΔVo/2), f (×2 → ΔVo/4!), o L")
    else:
        step(7, "Rizat de la tensió de sortida ΔVo",
             ["Origen: durant la fase ON (S tancat), el díode no condueix",
              "→ tot el corrent de sortida Io el subministra el condensador",
              "ΔVo = ΔQ/C = Io·D·T / C = Io·D / (f·C)",
              f"ΔVo = {V['Io']:.4f}·{D:.3f} / ({f_kHz:.0f}×10³·{C_uF:.2f}×10⁻⁶)",
              f"     = {V['Io']*D:.5f} / {f*C:.6f} = {V['dVo']*1000:.4f} mV"],
             f"ΔVo = {V['dVo']*1000:.4f} mV  =  {V['dVo']/V['Vo']*100:.3f}% de Vo" if V['Vo']>0 else f"ΔVo = {V['dVo']:.5f} V",
             "En Boost/Buck-Boost: ΔVo ∝ D, per tant empitjora amb D alt")

    # step 8: max voltages on switch and diode
    if topo == "Buck":
        step(8, "Tensions màximes sobre switch i díode",
             ["Quan S és OBERT: tot Vi cau al switch (díode condueix, Vo≈0 al switch)",
              "V_sw,max = Vi",
              "Quan S és TANCAT: díode en inversa, bloqueja Vi",
              "V_D,max = Vi  (tensió de ruptura mínima necessària)",
              f"V_sw,max = Vi = {Vi:.1f} V",
              f"V_D,max  = Vi = {Vi:.1f} V"],
             f"V_sw,max = {V['Vsw_max']:.2f} V  |  V_D,max = {V['VD_max']:.2f} V",
             f"Escollir components amb V_ruptura ≥ {V['Vsw_max']*1.5:.0f}–{V['Vsw_max']*2:.0f} V (marge ×1.5–2)")
    elif topo == "Boost":
        step(8, "Tensions màximes sobre switch i díode",
             ["Quan S és OBERT: díode condueix, node entre L i D està a Vo",
              "V_sw,max = Vo  (el switch ha de suportar la tensió de sortida)",
              "Quan S és TANCAT: díode en inversa, bloqueja Vo",
              "V_D,max = Vo",
              f"V_sw,max = Vo = {V['Vo']:.3f} V",
              f"V_D,max  = Vo = {V['Vo']:.3f} V"],
             f"V_sw,max = {V['Vsw_max']:.2f} V  |  V_D,max = {V['VD_max']:.2f} V",
             f"En Boost: els components han de suportar Vo (> Vi!). Marge ×1.5–2 → {V['Vsw_max']*1.5:.0f} V")
    else:
        step(8, "Tensions màximes sobre switch i díode",
             ["Quan S és OBERT: bobina empeny corrent cap al díode",
              "El node entre S i L va a −|Vo| (polaritat invertida)",
              "V_sw,max = Vi + |Vo|  (suma de les dues fonts)",
              "V_D,max  = Vi + |Vo|  (igual per simetria del circuit)",
              f"V_sw,max = {Vi:.1f} + {V['Vo']:.3f} = {V['Vsw_max']:.2f} V",
              f"V_D,max  = {Vi:.1f} + {V['Vo']:.3f} = {V['VD_max']:.2f} V"],
             f"V_sw,max = {V['Vsw_max']:.2f} V  |  V_D,max = {V['VD_max']:.2f} V",
             f"Buck-Boost té els requeriments de tensió MÉS ALTS. Marge ×1.5 → {V['Vsw_max']*1.5:.0f} V")

    # step 9: DCM output voltage (optional)
    if "MCD" in mode:
        if topo == "Buck":
            mcd_f = ["K = 2·L·f/R", "Vo_mcd = Vi · 2 / (1 + √(1 + 4·D²/K))"]
            K_val = 2*L*f/R
            mcd_r = f"K = {K_val:.4f}  →  Vo_mcd = {V['Vo']:.3f} V"
        elif topo == "Boost":
            mcd_f = ["K = 2·L·f/R", "Vo_mcd = Vi · (1 + √(1 + 4·D²/K)) / 2"]
            K_val = 2*L*f/R
            mcd_r = f"K = {K_val:.4f}  →  Vo_mcd = {V['Vo']:.3f} V"
        else:
            mcd_f = ["K = 2·L·f/R", "Vo_mcd = Vi · D / √K"]
            K_val = 2*L*f/R
            mcd_r = f"K = {K_val:.4f}  →  Vo_mcd = {V['Vo']:.3f} V"

        step(9, "Càlcul de Vo en MCD (conducció discontínua)",
             mcd_f, mcd_r,
             "En MCD la tensió de sortida depèn de la càrrega (R), no és constant per a D fix")

    st.divider()
    # summary table
    st.subheader("📊 Taula resum")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**Tensions**")
        st.write(f"Vo = {V['Vo']:.3f} V")
        st.write(f"V_sw,max = {V['Vsw_max']:.2f} V")
        st.write(f"V_D,max = {V['VD_max']:.2f} V")
        st.write(f"ΔVo = {V['dVo']*1000:.3f} mV ({V['dVo']/V['Vo']*100:.3f}%)" if V['Vo']>0 else "")
    with col_b:
        st.markdown("**Corrents**")
        st.write(f"Io = {V['Io']:.4f} A")
        st.write(f"IL_med = {V['IL_med']:.4f} A")
        st.write(f"IL_max = {V['IL_max']:.4f} A")
        st.write(f"IL_min = {V['IL_min']:.4f} A")
        st.write(f"ΔIL = {V['dIL']:.4f} A")
    with col_c:
        st.markdown("**Disseny / Crítics**")
        st.write(f"D = {D:.4f}")
        st.write(f"L = {L_uH:.2f} µH")
        st.write(f"C = {C_uF:.2f} µF")
        st.write(f"L_crit = {V['Lcrit']:.2f} µH → {real_mode}")
        st.write(f"C_mín = {V['Ccrit']:.2f} µF")


# tab 3: formulas and symbolic waveforms
with tab_vars:
    col_sv, col_fv = st.columns([1, 1.5])

    with col_sv:
        st.subheader(f"Esquema: {topo}")
        st.markdown(esquemes[topo](), unsafe_allow_html=True)

    with col_fv:
        st.subheader(f"Xuletari — {topo}")

        def show_formula_block(title, items, color="#4c9be8"):
            st.markdown(f"<div style='color:{color};font-weight:700;margin-top:12px;font-size:1rem'>{title}</div>",
                        unsafe_allow_html=True)
            for nom, latex_str in items:
                st.markdown(f"**{nom}**")
                st.latex(latex_str)

        def deriv_block(title, items, color="#4c9be8"):
            """items: list of (name, latex_formula, derivation_html)"""
            st.markdown(f"<div style='color:{color};font-weight:700;margin-top:14px;font-size:1rem'>{title}</div>",
                        unsafe_allow_html=True)
            for nom, latex_str, deriv in items:
                with st.expander(f"📐 {nom}"):
                    st.markdown(f"<div style='color:#ffcb6b;font-size:0.85rem;margin-bottom:6px'>{deriv}</div>",
                                unsafe_allow_html=True)
                    st.latex(latex_str)

        if topo == "Buck":
            deriv_block("🟦 MCC — Tensió i corrents", [
                ("Vo = D·Vi",
                 r"V_o = D \cdot V_i",
                 "⚙️ Origen: Volt·segon nuls a la bobina en règim permanent (∫v_L dt = 0 per període)<br>"
                 "ON → v_L = Vi−Vo durant D·T &nbsp;|&nbsp; OFF → v_L = −Vo durant (1−D)·T<br>"
                 "(Vi−Vo)·D·T + (−Vo)·(1−D)·T = 0 &nbsp;→&nbsp; Vi·D − Vo·D − Vo + Vo·D = 0 &nbsp;→&nbsp; <b>Vo = D·Vi</b>"),
                ("Io = Vo/R",
                 r"I_o = \frac{V_o}{R}",
                 "⚙️ Llei d'Ohm directa sobre la resistència de càrrega. Vo és constant en règim permanent (condensador gran)."),
                ("IL_med = Io",
                 r"I_{L,med} = I_o",
                 "⚙️ Conservació de càrrega al condensador: en règim permanent i_C,med = 0<br>"
                 "→ tot el corrent mig de la bobina va a la càrrega: I_L,med = I_o"),
                ("ΔIL (rizat de corrent)",
                 r"\Delta I_L = \frac{(V_i - V_o)\,D}{L\,f} = \frac{V_o\,(1-D)}{L\,f}",
                 "⚙️ Origen: equació de la bobina v_L = L·(di_L/dt) → Δi_L = v_L·Δt / L<br>"
                 "Durant la fase ON: v_L = Vi−Vo, Δt = D·T = D/f<br>"
                 "ΔI_L = (Vi−Vo)·D / (L·f) &nbsp;|&nbsp; Substituint Vo=D·Vi → ΔI_L = Vo·(1−D)/(L·f)"),
                ("IL_max i IL_min",
                 r"I_{L,max/min} = I_o \pm \frac{\Delta I_L}{2}",
                 "⚙️ La forma d'ona de i_L és triangular simètrica al voltant de IL_med = Io<br>"
                 "Pic (IL_max) al final de la fase ON &nbsp;|&nbsp; Vall (IL_min) al final de la fase OFF"),
                ("ΔVo (rizat de tensió)",
                 r"\Delta V_o = \frac{\Delta I_L}{8\,f\,C} = \frac{V_o(1-D)}{8\,L\,C\,f^2}",
                 "⚙️ El condensador integra la part AC de i_L: i_C = i_L − I_o (triangle d'amplitud ΔI_L/2)<br>"
                 "ΔVo = ΔQ/C &nbsp;|&nbsp; ΔQ = àrea del semitriangle = (ΔI_L/2)·(T/2)/2 = ΔI_L·T/8<br>"
                 "→ ΔVo = ΔI_L / (8·f·C)"),
                ("Vsw_max i VD_max",
                 r"V_{sw,max} = V_{D,max} = V_i",
                 "⚙️ Switch OBERT: el díode condueix → node entre S i L queda a 0 V → tot Vi cau al switch<br>"
                 "Switch TANCAT: el díode queda en inversa bloquejant Vi → VD,max = Vi"),
            ], "#4c9be8")

            deriv_block("🟣 Paràmetres crítics MCC ↔ MCD", [
                ("Lcrit — frontera MCC/MCD",
                 r"L_{crit} = \frac{(1-D)\,R}{2\,f}",
                 "⚙️ Condició MCC: IL_min ≥ 0 → IL_med ≥ ΔI_L/2<br>"
                 "I_o ≥ ΔI_L/2 = Vo·(1−D)/(2·L·f) = D·Vi·(1−D)/(2·L·f)<br>"
                 "Com Io = Vo/R → Vo/R ≥ Vo·(1−D)/(2·L·f) → <b>L ≥ (1−D)·R/(2·f)</b>"),
                ("Io_crit",
                 r"I_{o,crit} = \frac{V_o(1-D)}{2\,L\,f}",
                 "⚙️ Corrent de sortida just al límit MCC/MCD: IL_min = 0 → Io = ΔI_L/2<br>"
                 "Io,crit = Vo·(1−D) / (2·L·f)"),
                ("Cmin",
                 r"C_{min} = \frac{\Delta I_L}{8\,f\,\Delta V_{o,max}}",
                 "⚙️ Despejant C de la fórmula de ΔVo: ΔVo = ΔI_L/(8·f·C) → <b>C = ΔI_L/(8·f·ΔVo,max)</b>"),
            ], "#c897e8")

            deriv_block("🟧 MCD — Mode conducció discontínua", [
                ("Paràmetre K",
                 r"K = \frac{2\,L\,f}{R}",
                 "⚙️ Paràmetre adimensional que caracteritza el grau de discontinuïtat.<br>"
                 "K > K_crit(D) → MCC &nbsp;|&nbsp; K < K_crit(D) → MCD<br>"
                 "En Buck: K_crit = (1−D) → MCC si K > (1−D) → L > (1−D)·R/(2f)"),
                ("Vo en MCD",
                 r"V_o = \frac{2\,V_i}{1 + \sqrt{1 + 4D^2/K}}",
                 "⚙️ En MCD: Vo depèn de la càrrega (R), no és fix per D.<br>"
                 "Derivació: balanç amp·segon al condensador per període complet amb i_D triangular<br>"
                 "Io = ΔI_L·D₂/2 &nbsp;|&nbsp; ΔI_L = (Vi−Vo)·D/(L·f) &nbsp;|&nbsp; D₂ = ΔI_L/(Vi−Vo)·... → equació quadràtica en Vo"),
                ("D₂ (durada descàrrega)",
                 r"D_2 = \frac{V_o}{V_i - V_o}\,D",
                 "⚙️ D₂ és la fracció de període que la bobina descarrega (i_L de pic a 0).<br>"
                 "Volt·segon: (Vi−Vo)·D = Vo·D₂ → <b>D₂ = D·(Vi−Vo)/Vo... espera: D₂ = Vo·D/(Vi−Vo)</b><br>"
                 "Nota: D + D₂ ≤ 1 (la resta és temps mort amb i_L = 0)"),
            ], "#f0a020")

        elif topo == "Boost":
            deriv_block("🟦 MCC — Tensió i corrents", [
                ("Vo = Vi/(1−D)",
                 r"V_o = \frac{V_i}{1-D}",
                 "⚙️ Volt·segon nuls a la bobina (∫v_L dt = 0):<br>"
                 "ON → v_L = Vi durant D·T &nbsp;|&nbsp; OFF → v_L = Vi−Vo durant (1−D)·T<br>"
                 "Vi·D + (Vi−Vo)·(1−D) = 0 → Vi·D + Vi − Vi·D − Vo + Vo·D = 0 → Vi − Vo·(1−D) = 0 → <b>Vo = Vi/(1−D)</b>"),
                ("Io = Vo/R",
                 r"I_o = \frac{V_o}{R}",
                 "⚙️ Llei d'Ohm. El condensador de sortida manté Vo constant en règim permanent."),
                ("IL_med = Io/(1−D)",
                 r"I_{L,med} = \frac{I_o}{1-D}",
                 "⚙️ Conservació d'energia (η=1): Vi·I_L,med = Vo·I_o<br>"
                 "I_L,med = Vo·Io / Vi = [Vi/(1−D)]·Io / Vi = <b>Io/(1−D)</b>"),
                ("ΔIL",
                 r"\Delta I_L = \frac{V_i\,D}{L\,f}",
                 "⚙️ Fase ON: v_L = Vi, Δt = D·T → ΔI_L = Vi·D / (L·f)"),
                ("IL_max i IL_min",
                 r"I_{L,max/min} = I_{L,med} \pm \frac{\Delta I_L}{2}",
                 "⚙️ Igual que al Buck: ona triangular centrada a IL_med, amplitud ΔI_L."),
                ("ΔVo",
                 r"\Delta V_o = \frac{I_o\,D}{f\,C}",
                 "⚙️ Durant la fase ON el díode no condueix → el condensador subministra tot Io sol.<br>"
                 "ΔQ = Io·D·T = Io·D/f → ΔVo = ΔQ/C = <b>Io·D/(f·C)</b>"),
                ("Vsw_max = VD_max = Vo",
                 r"V_{sw,max} = V_{D,max} = V_o",
                 "⚙️ Fase OFF: díode condueix, node entre L i S queda a Vo → switch suporta Vo<br>"
                 "Fase ON: díode en inversa bloquejant Vo → VD,max = Vo"),
            ], "#4c9be8")

            deriv_block("🟣 Paràmetres crítics MCC ↔ MCD", [
                ("Lcrit",
                 r"L_{crit} = \frac{D\,(1-D)^2\,R}{2\,f}",
                 "⚙️ Condició MCC: IL_min ≥ 0 → I_L,med − ΔI_L/2 ≥ 0<br>"
                 "Io/(1−D) ≥ Vi·D/(2·L·f) → Vo·(1−D)/R ≥ Vi·D/(2·L·f)<br>"
                 "Vi/(1−D)·(1−D)/R ≥ Vi·D/(2·L·f) → <b>L ≥ D·(1−D)²·R/(2·f)</b>"),
                ("Io_crit",
                 r"I_{o,crit} = \frac{V_i\,D\,(1-D)}{2\,L\,f}",
                 "⚙️ Igual raonament: Io,crit = ΔI_L/2·(1−D) = Vi·D·(1−D)/(2·L·f)"),
                ("Cmin",
                 r"C_{min} = \frac{I_o\,D}{f\,\Delta V_{o,max}}",
                 "⚙️ Despejant C de ΔVo = Io·D/(f·C) → C = Io·D/(f·ΔVo,max)"),
            ], "#c897e8")

            deriv_block("🟧 MCD — Mode conducció discontínua", [
                ("Paràmetre K",
                 r"K = \frac{2\,L\,f}{R}",
                 "⚙️ En Boost: MCC si K > D·(1−D)² (equivalent a L > Lcrit)"),
                ("Vo en MCD",
                 r"V_o = \frac{V_i}{2}\left(1 + \sqrt{1 + \frac{4D^2}{K}}\right)",
                 "⚙️ Derivació per balanç de càrrega al condensador: Io = corrent mig del díode = ΔI_L·D₂/2<br>"
                 "Combinant amb ΔI_L = Vi·D/(L·f) i la condició volt·segon → equació quadràtica en Vo → solució positiva"),
            ], "#f0a020")

        else:  # Buck-Boost
            deriv_block("🟦 MCC — Tensió i corrents", [
                ("|Vo| = D·Vi/(1−D)  [polaritat invertida]",
                 r"|V_o| = \frac{D}{1-D}\,V_i \quad 	ext{(polaritat invertida)}",
                 "⚙️ Volt·segon nuls a la bobina:<br>"
                 "ON → v_L = Vi (bobina connectada a Vi) durant D·T<br>"
                 "OFF → v_L = −|Vo| (bobina descarrega a la sortida) durant (1−D)·T<br>"
                 "Vi·D·T − |Vo|·(1−D)·T = 0 → <b>|Vo| = Vi·D/(1−D)</b><br>"
                 "La polaritat és invertida perquè la bobina carrega amb Vi i descarrega cap al costat oposat."),
                ("Io = |Vo|/R",
                 r"I_o = \frac{|V_o|}{R}",
                 "⚙️ Llei d'Ohm. Io és positiu per convenció (corrent sortint del terminal positiu de Vo)."),
                ("IL_med = Io/(1−D)",
                 r"I_{L,med} = \frac{I_o}{1-D}",
                 "⚙️ Conservació d'energia: Vi·I_L,med = |Vo|·Io<br>"
                 "I_L,med = |Vo|·Io / Vi = [Vi·D/(1−D)]·Io / Vi = D·Io/(1−D)<br>"
                 "També: I_L,med = Io/(1−D) (el corrent mig al díode = Io = IL_med·(1−D))"),
                ("ΔIL",
                 r"\Delta I_L = \frac{V_i\,D}{L\,f}",
                 "⚙️ Fase ON: v_L = Vi, Δt = D/f → ΔI_L = Vi·D/(L·f) [igual que Boost]"),
                ("IL_max i IL_min",
                 r"I_{L,max/min} = I_{L,med} \pm \frac{\Delta I_L}{2}",
                 "⚙️ Ona triangular centrada a IL_med."),
                ("ΔVo",
                 r"\Delta V_o = \frac{I_o\,D}{f\,C}",
                 "⚙️ Fase ON: díode tallat → condensador subministra sol Io durant D·T<br>"
                 "ΔQ = Io·D/f → ΔVo = Io·D/(f·C) [igual que Boost]"),
                ("Vsw_max = VD_max = Vi + |Vo|",
                 r"V_{sw,max} = V_{D,max} = V_i + |V_o|",
                 "⚙️ Fase ON: díode en inversa. KVL: Vi + |Vo| = V_switch + V_L → en règim: Vswitch = Vi + |Vo|<br>"
                 "Fase OFF: switch obert. KVL: Vi = V_L + V_D_inversa → VD,max = Vi + |Vo|<br>"
                 "⚠️ Aquests valors són els MÉS ALTS de les tres topologies per a mateixa tensió de sortida."),
            ], "#4c9be8")

            deriv_block("🟣 Paràmetres crítics MCC ↔ MCD", [
                ("Lcrit",
                 r"L_{crit} = \frac{(1-D)^2\,R}{2\,f}",
                 "⚙️ Condició MCC: IL_min = IL_med − ΔI_L/2 ≥ 0<br>"
                 "Io/(1−D) ≥ Vi·D/(2·L·f) → |Vo|/R·1/(1−D) ≥ Vi·D/(2·L·f)<br>"
                 "Vi·D/(1−D)·1/(R·(1−D)) ≥ Vi·D/(2·L·f) → <b>L ≥ (1−D)²·R/(2·f)</b>"),
                ("Io_crit",
                 r"I_{o,crit} = \frac{V_i\,D\,(1-D)^2}{2\,L\,f}",
                 "⚙️ Io,crit = ΔI_L/2·(1−D) = Vi·D·(1−D)²/(2·L·f) [factor (1−D) perquè Io = IL_med·(1−D)]"),
                ("Cmin",
                 r"C_{min} = \frac{I_o\,D}{f\,\Delta V_{o,max}}",
                 "⚙️ De ΔVo = Io·D/(f·C) → C = Io·D/(f·ΔVo,max)"),
            ], "#c897e8")

            deriv_block("🟧 MCD — Mode conducció discontínua", [
                ("Paràmetre K",
                 r"K = \frac{2\,L\,f}{R}",
                 "⚙️ En Buck-Boost: MCC si K > (1−D)²"),
                ("Vo en MCD",
                 r"|V_o| = \frac{V_i\,D}{\sqrt{K}}",
                 "⚙️ Balanç d'amp·segon: Io = corrent mig díode = ΔI_L·D₂/2<br>"
                 "ΔI_L = Vi·D/(L·f) &nbsp;|&nbsp; D₂ = ΔI_L·L·f/|Vo| = Vi·D/|Vo|<br>"
                 "Io = |Vo|/R → |Vo|/R = Vi·D/(L·f)·Vi·D/(2·|Vo|) → |Vo|² = Vi²·D²·R/(2·L·f) → <b>|Vo| = Vi·D/√K</b>"),
            ], "#f0a020")

    st.divider()
    st.subheader("📈 Forma d'ona I_L — Comparativa MCC vs MCD")

    fig2, ax2 = plt.subplots(figsize=(11, 4), facecolor='#0e1117')
    ax2.set_facecolor('#131825')
    ax2.tick_params(colors='#888', labelsize=8)
    for sp in ax2.spines.values(): sp.set_color('#2a2a3a')

    t_sym = np.array([0, D, D, 1, 1, 1+D, 1+D, 2])
    iL_mcc = np.array([0.55, 1.0, 1.0, 0.55, 0.55, 1.0, 1.0, 0.55])
    # DCM: rises, falls to 0, stays at 0
    D2_sym = 0.3
    t_mcd = np.array([0, D, D, D+D2_sym, D+D2_sym, 1, 1, 1+D, 1+D, 1+D+D2_sym, 1+D+D2_sym, 2])
    iL_mcd = np.array([0, 1.0, 1.0, 0, 0, 0, 0, 1.0, 1.0, 0, 0, 0])

    ax2.plot(t_sym, iL_mcc, color='#4caf50', lw=2.5, label='MCC — IL', zorder=3)
    ax2.plot(t_mcd, iL_mcd, color='#f0a020', lw=2.2, ls='--', label='MCD — IL', zorder=3)

    ax2.axhline(0.775, color='#90ff90', lw=0.9, ls=':', alpha=0.7)
    ax2.text(0.03, 0.80, 'IL_med (MCC)', color='#90ff90', fontsize=8)
    ax2.axhline(1.0,   color='#ff9090', lw=0.9, ls=':', alpha=0.7)
    ax2.text(0.03, 1.03, 'IL_max', color='#ff9090', fontsize=8)
    ax2.axhline(0.55,  color='#8090ff', lw=0.9, ls=':', alpha=0.7)
    ax2.text(0.03, 0.50, 'IL_min', color='#8090ff', fontsize=8)

    for xv, lbl in [(0,'0'),(D,'D·T'),(D+D2_sym,'(D+D₂)T'),(1,'T'),(1+D,'(1+D)T'),(2,'2T')]:
        ax2.axvline(xv, color='#444', lw=0.8, ls=':')
        ax2.text(xv, -0.12, lbl, color='#999', fontsize=7.5, ha='center')

    # interval arrows
    ax2.annotate('', xy=(D,-0.22), xytext=(0,-0.22),
                 arrowprops=dict(arrowstyle='<->', color='#f0a020', lw=1.2))
    ax2.text(D/2, -0.30, 'D·T', color='#f0a020', fontsize=8.5, ha='center')
    ax2.annotate('', xy=(1,-0.22), xytext=(D,-0.22),
                 arrowprops=dict(arrowstyle='<->', color='#e05050', lw=1.2))
    ax2.text((1+D)/2, -0.30, '(1−D)·T  o  D₂·T+t_off', color='#e05050', fontsize=8, ha='center')

    ax2.set_xlim(-0.04, 2.08)
    ax2.set_ylim(-0.42, 1.22)
    ax2.set_xlabel("Temps (normalitzat a T)", color='#aaa', fontsize=9)
    ax2.set_ylabel("I_L (u.a.)", color='#aaa', fontsize=9)
    ax2.legend(loc='upper right', fontsize=9, framealpha=0.25,
               facecolor='#1a1d2a', edgecolor='#333')
    ax2.set_title(f"Forma d'ona IL — {topo}  |  (verd) MCC  (taronja) MCD", color='#ccc', fontsize=11, pad=8)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

# footer
st.divider()
st.caption("⚡ DC/DC Converter Study Tool — Buck · Boost · Buck-Boost  |  Developed by Vlarac")