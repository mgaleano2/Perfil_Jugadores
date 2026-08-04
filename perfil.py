import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Player Profile", layout="wide")

# ============================
# Blanco y Celeste, clean style
# ============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght=700;900&family=Barlow:wght=400;600&family=Space+Mono&display=swap');

[data-testid="stAppViewContainer"] { background: #ffffff; }
section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid rgba(0,0,0,0.08); }

/* HEADER */
.player-header {
    background: #f7f9fc;
    padding: 20px;
    border-radius: 10px;
    border-left: 6px solid #00a8cc;
    margin-bottom: 25px;
}

.player-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 36px;
    letter-spacing: 2px;
    font-weight: 900;
    margin: 0;
}

.player-meta {
    color: #6b7280;
    font-size: 14px;
}

/* ATTRIBUTE BOX */
.attribute-box {
    background: #f7f9fc;
    border: 1px solid rgba(0,0,0,0.06);
    border-top: 2px solid #00a8cc;
    border-radius: 8px;
    padding: 12px 8px;
    text-align: center;
    margin-bottom: 10px;
}

.attribute-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 1px;
    color: #6b7280;
}

.attribute-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 26px;
    font-weight: 700;
}

/* SECTIONS */
.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 20px;
    letter-spacing: 2px;
    border-bottom: 2px solid rgba(0,168,204,0.25);
    margin-top: 35px;
    margin-bottom: 15px;
}

/* Bio boxes */
.bio-box {
    background: #f0f9ff;
    border: 1px solid rgba(0,168,204,0.15);
    border-radius: 8px;
    padding: 12px;
    text-align: center;
}
.bio-label {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.bio-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #111;
}
.bio-unit {
    font-size: 11px;
    color: #6b7280;
}
div[data-testid='stImage'] {
    margin-top: -25px;
}
</style>
""", unsafe_allow_html=True)

# ======================
# Carga datos - Planillas
# ======================
@st.cache_data
def load_antropometria():
    try:
        df_ant = pd.read_excel("jugadores_stats.xls", sheet_name="Antropometria")
        df_ant.columns = df_ant.columns.str.strip()
        return df_ant
    except:
        return pd.DataFrame()

@st.cache_data
def load_fuerza():
    try:
        df_fuerza = pd.read_excel("jugadores_stats.xls", sheet_name="Fuerza")
        df_fuerza.columns = df_fuerza.columns.str.strip()
        return df_fuerza
    except:
        return pd.DataFrame()

@st.cache_data
def load_saltabilidad():
    try:
        df_salt = pd.read_excel("jugadores_stats.xls", sheet_name="Saltabilidad")
        df_salt.columns = df_salt.columns.str.strip()
        return df_salt
    except:
        return pd.DataFrame()

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("jugadores_stats.xls")
        df.columns = df.columns.str.strip()

        cols = ['Maxima velocidad','Distancia Total(m)','Conteo de sprints','Max Acc (g)','Calor(Kcal)', 'Distancia de sprint(m)']
        for c in cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            else:
                if c == 'Distancia de sprint(m)':
                    df[c] = 0.0
        return df
    except:
        return pd.DataFrame()

# Data instantiations
df_main = load_data()
df_ant = load_antropometria()
df_fuerza = load_fuerza()
df_salt = load_saltabilidad()

if df_main.empty:
    st.error("No se pudo cargar el archivo 'jugadores_stats.xls' o la hoja principal está vacía.")
    st.stop()

# ======================
# Biometria Calculadora
# ======================
def calculate_bmi(weight, height):
    return weight / (height ** 2) if height > 0 else 0

def calculate_body_fat_jackson_pollock(triceps_skinfold, subscapular_skinfold, age, sex='m'):
    sum_folds = triceps_skinfold + subscapular_skinfold
    if sum_folds <= 0 or age is None or age <= 0: return None
    if sex == 'm':
        density = 1.112 - 0.00043499 * sum_folds + 0.00000055 * (sum_folds ** 2) - 0.00028826 * age
    else:
        density = 1.097 - 0.00046971 * sum_folds + 0.00000056 * (sum_folds ** 2) - 0.00012828 * age
    return max(3, min(50, (495 / density) - 450))

def estimate_body_fat(bmi, age):
    return max(5, min(40, (1.20 * bmi) + (0.23 * age) - 10.8))

def get_body_fat(player, weight, age=None):
    if df_ant.empty: return None, "estimated"
    row = df_ant[df_ant['Deportista'] == player]
    if row.empty: return None, "estimated"
    
    row = row.iloc[0]
    grasa_pct = row.get('grasa porcentaje')
    if pd.notna(grasa_pct) and grasa_pct > 0: return float(grasa_pct), "excel"
    
    pliegue_tri = row.get('pliegue tricipital')
    pliegue_sub = row.get('pliegue subescapular')
    edad_calc = age if age is not None else row.get('Edad', 25)
    
    if pd.notna(pliegue_tri) and pd.notna(pliegue_sub) and (pliegue_tri + pliegue_sub) > 0:
        body_fat_calc = calculate_body_fat_jackson_pollock(pliegue_tri, pliegue_sub, edad_calc)
        if body_fat_calc: return body_fat_calc, "skinfold"
    return None, "estimated"

def estimate_muscle_mass(weight, height, body_fat):
    return weight * (100 - body_fat) / 100 * 0.45

def get_physical_status(bmi):
    if bmi < 18.5: return "Underweight"
    elif bmi < 25: return "Normal"
    elif bmi < 30: return "Overweight"
    else: return "Obesity"

max_vals = {
    'Maxima velocidad': max(df_main['Maxima velocidad'].max(), 1),
    'Distancia Total(m)': max(df_main['Distancia Total(m)'].max(), 1),
    'Conteo de sprints': max(df_main['Conteo de sprints'].max(), 1),
    'Max Acc (g)': max(df_main['Max Acc (g)'].max(), 1),
    'Calor(Kcal)': max(df_main['Calor(Kcal)'].max(), 1)
}

# ======================
# Renderizado
# ======================
def render_header(player_name):
    p = df_main[df_main['Deportista'] == player_name].iloc[0]
    photo_path = str(p.get('Photo')).replace('\\', '/') if pd.notna(p.get('Photo')) else None

    col_info, col_photo = st.columns([4, 1])
    with col_info:
        st.markdown(f"""
        <div class="player-header">
            <div class="player-name">{p['Deportista'].upper()}</div>
            <div class="player-meta">
                {p.get('Posicion', 'N/A')} • {p.get('Nacionalidad', 'N/A')} • {p.get('Equipo','Club')} <br>
                {p.get('Altura (mts)', 0)} m • {p.get('Peso (kg)', 0)} kg
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_photo:
        if photo_path:
            try: st.image(photo_path, width=150)
            except: st.write("")

def render_gps_metrics(player_name):
    p = df_main[df_main['Deportista'] == player_name].iloc[0]
    col_metrics, col_radar = st.columns([1, 1.2])

    with col_metrics:
        st.markdown('<div class="section-title">Physical Performance</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        metrics = [
            ("Speed", f"{p['Maxima velocidad']:.2f} km/h"),
            ("Resistance", f"{p['Distancia Total(m)']:.0f} m"),
            ("Sprints", f"{p['Conteo de sprints']:.0f} un"),
            ("Acceleration", f"{p['Max Acc (g)']:.2f} g"),
            ("Load", f"{p['Calor(Kcal)']:.0f} kcal"),
        ]
        for i, (label, value) in enumerate(metrics):
            box = c1 if i % 2 == 0 else c2
            val_part, unit_part = value.split()[0], " ".join(value.split()[1:])
            box.markdown(f"""
            <div class="attribute-box">
                <div class="attribute-label">{label}</div>
                <div class="attribute-value" style="font-size:20px">{val_part}</div>
                <div style="font-size:11px;color:#6b7280">{unit_part}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_radar:
        categories = ['Speed','Resistance','Sprints','Acceleration','Load']
        radar_values = [
            (p['Maxima velocidad'] / max_vals['Maxima velocidad']) * 100,
            (p['Distancia Total(m)'] / max_vals['Distancia Total(m)']) * 100,
            (p['Conteo de sprints'] / max_vals['Conteo de sprints']) * 100,
            (p['Max Acc (g)'] / max_vals['Max Acc (g)']) * 100,
            (p['Calor(Kcal)'] / max_vals['Calor(Kcal)']) * 100
        ]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=radar_values, theta=categories, fill='toself', name=player_name, line=dict(color='#00a8cc')))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%")), showlegend=False, margin=dict(t=40, b=40, l=40, r=40), height=320, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, key=f"radar_{player_name}")

    # Biometry subsection
    st.markdown('<div class="section-title">Biometry & Body Composition</div>', unsafe_allow_html=True)
    weight, height = float(p.get('Peso (kg)', 70)), float(p.get('Altura (mts)', 1.70))
    bmi = calculate_bmi(weight, height)
    age = p.get('Edad')
    age_val = int(age) if pd.notna(age) else 25

    body_fat, fat_source = get_body_fat(player_name, weight, age_val)
    if body_fat is None:
        body_fat = estimate_body_fat(bmi, age_val)
        fat_source = "estimated"

    muscle = estimate_muscle_mass(weight, height, body_fat)
    status = get_physical_status(bmi)

    col_bio1, col_bio2, col_bio3, col_bio4, col_bio5 = st.columns(5)
    col_bio1.markdown(f'<div class="bio-box"><div class="bio-label">Age</div><div class="bio-value">{int(age) if pd.notna(age) else "-"}</div><div class="bio-unit">years</div></div>', unsafe_allow_html=True)
    col_bio2.markdown(f'<div class="bio-box"><div class="bio-label">BMI</div><div class="bio-value">{bmi:.1f}</div><div class="bio-unit">kg/m²</div></div>', unsafe_allow_html=True)
    col_bio3.markdown(f'<div class="bio-box"><div class="bio-label">Body Fat</div><div class="bio-value">{body_fat:.1f}%</div><div class="bio-unit">{fat_source}</div></div>', unsafe_allow_html=True)
    col_bio4.markdown(f'<div class="bio-box"><div class="bio-label">Muscle Mass</div><div class="bio-value">{muscle:.1f}</div><div class="bio-unit">kg</div></div>', unsafe_allow_html=True)
    col_bio5.markdown(f'<div class="bio-box"><div class="bio-label">Status</div><div class="bio-value" style="font-size:18px">{status}</div><div class="bio-unit">physical</div></div>', unsafe_allow_html=True)

    # Strength subsection
    if not df_fuerza.empty:
        row_fuerza = df_fuerza[df_fuerza['Deportista'] == player_name]
        if not row_fuerza.empty:
            row_f = row_fuerza.iloc[0]
            st.markdown('<div class="section-title">Max Strength - 1RM</div>', unsafe_allow_html=True)
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            col_f1.markdown(f'<div class="bio-box"><div class="bio-label">Squat</div><div class="bio-value">{row_f.get("Squat (kg)", "-")} <span class="bio-unit">kg</span></div></div>', unsafe_allow_html=True)
            col_f2.markdown(f'<div class="bio-box"><div class="bio-label">Bench Press</div><div class="bio-value">{row_f.get("Press banca (kg)", "-")} <span class="bio-unit">kg</span></div></div>', unsafe_allow_html=True)
            col_f3.markdown(f'<div class="bio-box"><div class="bio-label">Deadlift</div><div class="bio-value">{row_f.get("Peso muerto (kg)", "-")} <span class="bio-unit">kg</span></div></div>', unsafe_allow_html=True)
            col_f4.markdown(f'<div class="bio-box"><div class="bio-label">Bicep Curl</div><div class="bio-value">{row_f.get("Curl biceps (kg)", "-")} <span class="bio-unit">kg</span></div></div>', unsafe_allow_html=True)

# ======================
# Panel izquierda
# ======================
st.sidebar.markdown("### Seleccione Jugador")
report_mode = st.sidebar.checkbox("Todos (Report Mode)")

if report_mode:
    selected_players = df_main['Deportista'].unique().tolist()
else:
    selected_players = [st.sidebar.selectbox("Select Player", df_main['Deportista'].unique())]

if st.sidebar.button("Export to PDF"):
    st.sidebar.info("Press Ctrl + P (or Cmd + P) → Save as PDF")

st.markdown("---")

# CSS FOR PAGE BREAKS
st.markdown("<style>@media print {.page-break { page-break-before: always; }}</style>", unsafe_allow_html=True)

# ======================
# Tab - Menu
# ======================
if not report_mode:
    render_header(selected_players[0])

tab1, tab2, tab3 = st.tabs(["🏃‍♂️ GPS & Campo", "⚡ Potencia de Sprint", "🥇 Leaderboard Plantel"])

with tab1:
    for i, player in enumerate(selected_players):
        if report_mode and i > 0: st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
        if report_mode: render_header(player)
        render_gps_metrics(player)
        if report_mode: st.markdown("<hr style='border: 1px solid #38bdf8; margin: 40px 0;'>", unsafe_allow_html=True)

with tab2:
    for i, player in enumerate(selected_players):
        if report_mode and i > 0: st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
        if report_mode: render_header(player)
        p = df_main[df_main['Deportista'] == player].iloc[0]
        st.markdown(f"### Análisis Específico de Sprints")
        dist_sprint = p.get('Distancia de sprint(m)', 0)
        cant_sprint = p.get('Conteo de sprints', 0)
        eficiencia = dist_sprint / cant_sprint if cant_sprint > 0 else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Repeticiones de Sprint", f"{cant_sprint:.0f}")
        c2.metric("Distancia de Sprint", f"{dist_sprint:.0f} m")
        c3.metric("Media por Sprint", f"{eficiencia:.1f} m/sp")
        
        p_salt = df_salt[df_salt['Deportista'] == player] if not df_salt.empty else pd.DataFrame()
        if not p_salt.empty:
            st.markdown('<div class="section-title">Potencia de Salto Relacionada</div>', unsafe_allow_html=True)
            s1, s2 = st.columns(2)
            s_curr = p_salt.iloc[-1]
            s1.metric("Explosividad CMJ", f"{s_curr.get('CMJ', '--')} cm")
            s2.metric("Potencia SJ", f"{s_curr.get('SJ', '--')} cm")
        if report_mode: st.divider()

with tab3:
    # Título traducido al Chino mediante string literal bilingüe
    st.markdown('<div class="section-title">Ranking General del Equipo | 球队综合排名</div>', unsafe_allow_html=True)
    
    # Definición de columnas base y renombramiento inicial en el backend
    cols_ranking = {
        'Deportista': 'Jugador', 
        'Maxima velocidad': 'Vel. Máx (km/h)', 
        'Distancia de sprint(m)': 'Dist. Sprint (m)', 
        'Distancia Total(m)': 'Dist. Total (m)', 
        'Conteo de sprints': 'Sprints', 
        'Max Acc (g)': 'Acel. Máx (g)'
    }
    
    df_ranking = df_main[list(cols_ranking.keys())].copy().rename(columns=cols_ranking)
    
    # Mostramos la tabla ordenada con las etiquetas bilingües aplicadas mediante el 'column_config'
    st.dataframe(
        df_ranking.sort_values(by='Vel. Máx (km/h)', ascending=False), 
        use_container_width=True, 
        hide_index=True,
        height=600,
        column_config={
            "Jugador": st.column_config.NumberColumn("Jugador | 球员"),
            "Vel. Máx (km/h)": st.column_config.ProgressColumn("Velocidad Máxima | 最高速度", format="%.2f", min_value=0, max_value=40),
            "Dist. Sprint (m)": st.column_config.NumberColumn("Sprint Total | 冲刺总距离", format="%d m"),
            "Dist. Total (m)": st.column_config.NumberColumn("Dist. Total (m) | 总距离 (米)", format="%d m"),
            "Sprints": st.column_config.NumberColumn("Sprints | 冲刺次数", format="%d"),
            "Acel. Máx (g)": st.column_config.NumberColumn("Acel Máx | 最大加速度", format="%.2f g")
        }
    )
