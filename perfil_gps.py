import base64
import glob
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Player Profile - GPS", layout="wide")

# ============================
# WHITE AND BLUE, clean style
# ============================
css_path = os.path.join(os.path.dirname(__file__), "styles_gps.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ======================
# CONFIG
# ======================
SESSIONS_DIR = "sessions"   # las planillas .xls van dentro de esta carpeta
ROSTER_FILE = "roster.xlsx"  # Le agregue Apodo y numero
PHOTO_DIR = "photo"         # Foto de cada uno
LOGO_FILE = "logo.png"      # Logo del equipo (raiz del proyecto)

def load_logo_b64():
    if not os.path.exists(LOGO_FILE):
        return None
    with open(LOGO_FILE, "rb") as f:
        return base64.b64encode(f.read()).decode()

LOGO_B64 = load_logo_b64()

META_MAP = {
    '训练日期': 'Session Date', '训练结束时间': 'Session End Time', '训练ID': 'Session ID',
    '训练主题': 'Session Name', '球队': 'Team', '球队ID': 'Team ID',
    '球员数量': 'Player Count', '场地': 'Field',
}

# Mapeo del nombre de equipo
TEAM_NAME_MAP = {
    '厦门二中高中队': 'Xiamen',
}

def clean_field(raw_field):
    """Extract just the field number, e.g. '1号场' -> '1'."""
    if raw_field is None:
        return raw_field
    digits = ''.join(ch for ch in str(raw_field) if ch.isdigit())
    return digits if digits else str(raw_field)

COLUMN_MAP = {
    '姓名': 'Player', '球衣号': 'Jersey', '位置': 'Position',
    '上场时长': 'Time on Field (s)', '最高心率': 'Max HR (bpm)', '平均心率': 'Avg HR (bpm)',
    '运动负荷': 'Player Load', '运动强度': 'Load Intensity',
    '跑动距离': 'Total Distance (m)', '最快跑动速度': 'Max Speed (m/s)',
    '跑动距离（高速跑）': 'HSR Distance (m)', '跑动距离（冲刺跑）': 'Sprint Distance (m)',
    '跑动次数（高速跑）': 'HSR Count', '跑动次数（冲刺跑）': 'Sprint Count',
}

# What each metric means - shown in the in-app glossary
GLOSSARY = {
    "Time on Field": "Minutos que el chaleco realmente registró. Sirve para poner todo lo demás en contexto: no es lo mismo comparar 90 minutos de partido que 20 minutos de test.",
    "Max HR": "La frecuencia cardíaca más alta que tocó en la sesión. Mide el esfuerzo interno — cuánto le costó al cuerpo, más allá de cuánto corrió.",
    "Avg HR": "La frecuencia cardíaca promedio de toda la sesión. Si un jugador tiene mucha distancia pero FC promedio baja, probablemente no estuvo corriendo a intensidad real.",
    "Player Load": "Carga externa total: suma todas las aceleraciones y frenadas del jugador durante la sesión. Es el número que mejor resume 'cuánto trabajó' el cuerpo.",
    "Load Intensity": "Player Load dividido por los minutos jugados. Permite comparar de forma justa un partido de 90' con un test de 20', aunque duren distinto.",
    "Total Distance": "Metros totales recorridos. Mide volumen de trabajo aeróbico — quién realmente corre la cancha y quién camina.",
    "Max Speed": "La velocidad máxima que alcanzó corriendo. Es la capacidad de sprint pura — el dato más fácil de entender y de comparar entre jugadores.",
    "HSR Distance": "Metros corridos a velocidad alta, pero sin llegar al sprint máximo. Muestra la capacidad de repetir esfuerzos intensos durante el partido.",
    "HSR Count": "Cantidad de carreras a alta velocidad que hizo.",
    "Sprint Distance": "Metros corridos a máxima velocidad (sprint). Son las acciones explosivas que suelen definir jugadas.",
    "Sprint Count": "Cantidad de sprints que hizo. Resume en un solo número el ritmo de trabajo y la explosividad del jugador.",
}

# ======================
# LOAD DATA FUNCTIONS
# ======================
@st.cache_data
def load_roster():
    if not os.path.exists(ROSTER_FILE):
        return pd.DataFrame(columns=["Name", "Jersey", "Nickname", "Photo"])
    df = pd.read_excel(ROSTER_FILE)
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_sessions(_roster):
    sessions = {}
    parsed = []
    for path in sorted(glob.glob(os.path.join(SESSIONS_DIR, "*.xlsx"))):
        try:
            xl = pd.ExcelFile(path)
            if '信息说明' not in xl.sheet_names or '球员数据' not in xl.sheet_names:
                continue

            meta_raw = pd.read_excel(path, sheet_name='信息说明')
            meta = {META_MAP.get(k, k): v for k, v in zip(meta_raw.iloc[:, 0], meta_raw.iloc[:, 1])}
            if 'Team' in meta:
                meta['Team'] = TEAM_NAME_MAP.get(meta['Team'], meta['Team'])
            if 'Field' in meta:
                meta['Field'] = clean_field(meta['Field'])

            df = pd.read_excel(path, sheet_name='球员数据').rename(columns=COLUMN_MAP)

            if 'Max Speed (m/s)' in df.columns:
                df['Max Speed (km/h)'] = pd.to_numeric(df['Max Speed (m/s)'], errors='coerce').fillna(0) * 3.6
            if 'Time on Field (s)' in df.columns:
                df['Time on Field (min)'] = pd.to_numeric(df['Time on Field (s)'], errors='coerce').fillna(0) / 60

            numeric_cols = [
                'Total Distance (m)', 'HSR Distance (m)', 'Sprint Distance (m)',
                'HSR Count', 'Sprint Count', 'Player Load', 'Load Intensity',
                'Max HR (bpm)', 'Avg HR (bpm)',
            ]
            for c in numeric_cols:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

            # Link nickname + photo from the roster (keyed on the exact GPS export name)
            if not _roster.empty:
                df = df.merge(
                    _roster[['Name', 'Nickname', 'Photo']],
                    left_on='Player', right_on='Name', how='left'
                )
            if 'Nickname' not in df.columns:
                df['Nickname'] = None
            if 'Photo' not in df.columns:
                df['Photo'] = None
            def _combine_display_name(row):
                nick = row.get('Nickname')
                if pd.notna(nick) and str(nick).strip():
                    return f"{row['Player']} - {str(nick).strip()}"
                return row['Player']
            df['Display Name'] = df.apply(_combine_display_name, axis=1)

            date = meta.get('Session Date', os.path.basename(path))
            parsed.append((date, meta, df))
        except Exception as e:
            st.sidebar.warning(f"Could not read {os.path.basename(path)}: {e}")

    # Date-only labels; add a "(n)" suffix only for dates that repeat, so nothing collides
    from collections import Counter
    date_counts = Counter(d for d, _, _ in parsed)
    seen = Counter()
    for date, meta, df in parsed:
        if date_counts[date] > 1:
            seen[date] += 1
            label = f"{date} ({seen[date]})"
        else:
            label = str(date)
        sessions[label] = (meta, df)
    return sessions

roster = load_roster()
sessions = load_sessions(roster)

if not sessions:
    st.error(f"No GPS session files found in '{SESSIONS_DIR}/'. Drop your .xlsx exports there and reload.")
    st.stop()
if roster.empty:
    st.sidebar.warning(f"No '{ROSTER_FILE}' found — showing raw GPS names. Add it to link nicknames and photos.")

# ======================
# SIDEBAR
# ======================
if os.path.exists(LOGO_FILE):
    st.sidebar.image(LOGO_FILE, width=140)
    st.sidebar.markdown("---")

st.sidebar.markdown("### Session")
session_label = st.sidebar.selectbox("Select Training Session", list(sessions.keys()))
meta, df_main = sessions[session_label]

st.sidebar.markdown(
    f"**Team:** {meta.get('Team', '-')}  \n"
    f"**Field:** {meta.get('Field', '-')}  \n"
    f"**Players:** {meta.get('Player Count', len(df_main))}"
)

st.sidebar.markdown("### View")
view_mode = st.sidebar.radio("Audience", ["Coach (all metrics)", "Player-friendly (simple)"])

st.sidebar.markdown("### Player Selection")
report_mode = st.sidebar.checkbox("All Players (Report Mode)")

name_options = df_main.sort_values('Display Name')['Display Name'].unique()
if report_mode:
    selected_players = name_options.tolist()
else:
    selected_players = [st.sidebar.selectbox("Select Player", name_options)]

if st.sidebar.button("Export to PDF"):
    st.sidebar.info("Press Ctrl + P (or Cmd + P) → Save as PDF")

st.markdown("---")
st.markdown("<style>@media print {.page-break { page-break-before: always; }}</style>", unsafe_allow_html=True)

max_vals = {
    'Max Speed (km/h)': max(df_main['Max Speed (km/h)'].max(), 1),
    'Total Distance (m)': max(df_main['Total Distance (m)'].max(), 1),
    'Sprint Count': max(df_main['Sprint Count'].max(), 1),
    'Player Load': max(df_main['Player Load'].max(), 1),
    'Load Intensity': max(df_main['Load Intensity'].max(), 1),
}

# ======================
# RENDERING FUNCTIONS
# ======================
def get_row(display_name):
    return df_main[df_main['Display Name'] == display_name].iloc[0]

def render_header(display_name):
    p = get_row(display_name)
    col_info, col_photo = st.columns([4, 1])
    with col_info:
        logo_html = (
            f'<img src="data:image/jpeg;base64,{LOGO_B64}" '
            f'style="height:48px;width:48px;object-fit:contain;border-radius:6px;flex-shrink:0;" />'
        ) if LOGO_B64 else ""
        st.markdown(f"""
        <div class="player-header" style="display:flex;align-items:center;gap:14px;">{logo_html}
            <div>
                <div class="player-name">{p['Display Name']}</div>
                <div class="player-meta">
                    #{p.get('Jersey', '-')} • {meta.get('Team', 'Club')} <br>
                    {session_label} • {p.get('Time on Field (min)', 0):.0f} min on field
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_photo:
        photo_file = p.get('Photo')
        photo_path = os.path.join(PHOTO_DIR, str(photo_file)).replace('\\', '/') if pd.notna(photo_file) else None
        if photo_path:
            try: st.image(photo_path, width=150)
            except: st.write("")

def render_gps_metrics(display_name):
    p = get_row(display_name)
    col_metrics, col_radar = st.columns([1, 1.2])

    with col_metrics:
        st.markdown('<div class="section-title">Physical Performance</div>', unsafe_allow_html=True)

        all_metrics = [
            ("Max Speed", f"{p['Max Speed (km/h)']:.1f} km/h"),
            ("Total Distance", f"{p['Total Distance (m)']:.0f} m"),
            ("Sprints", f"{p['Sprint Count']:.0f} un"),
            ("Time on Field", f"{p['Time on Field (min)']:.0f} min"),
        ]
        coach_only_metrics = [
            ("Sprint Distance", f"{p['Sprint Distance (m)']:.0f} m"),
            ("HSR Distance", f"{p['HSR Distance (m)']:.0f} m"),
            ("HSR Count", f"{p['HSR Count']:.0f} un"),
            ("Player Load", f"{p['Player Load']:.1f} au"),
            ("Load Intensity", f"{p['Load Intensity']:.2f} au/min"),
            ("Max HR", f"{p['Max HR (bpm)']:.0f} bpm"),
            ("Avg HR", f"{p['Avg HR (bpm)']:.0f} bpm"),
        ]
        metrics = all_metrics if view_mode.startswith("Player") else all_metrics + coach_only_metrics

        c1, c2 = st.columns(2)
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
        if view_mode.startswith("Player"):
            categories = ['Speed', 'Distance', 'Sprints']
            radar_values = [
                (p['Max Speed (km/h)'] / max_vals['Max Speed (km/h)']) * 100,
                (p['Total Distance (m)'] / max_vals['Total Distance (m)']) * 100,
                (p['Sprint Count'] / max_vals['Sprint Count']) * 100,
            ]
        else:
            categories = ['Speed', 'Distance', 'Sprints', 'Load', 'Intensity']
            radar_values = [
                (p['Max Speed (km/h)'] / max_vals['Max Speed (km/h)']) * 100,
                (p['Total Distance (m)'] / max_vals['Total Distance (m)']) * 100,
                (p['Sprint Count'] / max_vals['Sprint Count']) * 100,
                (p['Player Load'] / max_vals['Player Load']) * 100,
                (p['Load Intensity'] / max_vals['Load Intensity']) * 100,
            ]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=radar_values, theta=categories, fill='toself', name=display_name, line=dict(color='#00a8cc')))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%")), showlegend=False, margin=dict(t=40, b=40, l=40, r=40), height=320, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, key=f"radar_{display_name}")

# ======================
# TAB LOGIC
# ======================
if not report_mode:
    render_header(selected_players[0])

tab1, tab2, tab3 = st.tabs(["🏃‍♂️ GPS & Load", "⚡ Sprint Power", "🥇 Squad Leaderboard"])

with tab1:
    for i, player in enumerate(selected_players):
        if report_mode and i > 0:
            st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
        if report_mode:
            render_header(player)
        render_gps_metrics(player)
        if report_mode:
            st.markdown("<hr style='border: 1px solid #38bdf8; margin: 40px 0;'>", unsafe_allow_html=True)

    if view_mode.startswith("Coach"):
        with st.expander("📖 Glossary — what each metric means"):
            for label, explanation in GLOSSARY.items():
                st.markdown(f"**{label}** — {explanation}")

with tab2:
    for i, player in enumerate(selected_players):
        if report_mode and i > 0:
            st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
        if report_mode:
            render_header(player)
        p = get_row(player)
        st.markdown("### Sprint-Specific Analysis")
        dist_sprint = p.get('Sprint Distance (m)', 0)
        cant_sprint = p.get('Sprint Count', 0)
        eficiencia = dist_sprint / cant_sprint if cant_sprint > 0 else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Sprint Reps", f"{cant_sprint:.0f}")
        c2.metric("Sprint Distance", f"{dist_sprint:.0f} m")
        c3.metric("Avg per Sprint", f"{eficiencia:.1f} m/sprint")

        if view_mode.startswith("Coach"):
            st.markdown('<div class="section-title">High-Speed Running (HSR)</div>', unsafe_allow_html=True)
            h1, h2 = st.columns(2)
            h1.metric("HSR Distance", f"{p.get('HSR Distance (m)', 0):.0f} m")
            h2.metric("HSR Count", f"{p.get('HSR Count', 0):.0f} un")
        if report_mode:
            st.divider()

with tab3:
    st.markdown('<div class="section-title">Squad Overall Ranking</div>', unsafe_allow_html=True)

    if view_mode.startswith("Player"):
        cols_ranking = ['Jersey', 'Display Name', 'Max Speed (km/h)', 'Total Distance (m)', 'Sprint Count']
    else:
        cols_ranking = [
            'Jersey', 'Display Name', 'Max Speed (km/h)', 'Total Distance (m)',
            'Sprint Distance (m)', 'Sprint Count', 'HSR Distance (m)', 'HSR Count',
            'Player Load', 'Load Intensity', 'Max HR (bpm)', 'Avg HR (bpm)',
        ]
    df_ranking = df_main[cols_ranking].rename(columns={'Display Name': 'Player'})

    st.dataframe(
        df_ranking.sort_values(by='Max Speed (km/h)', ascending=False),
        use_container_width=True,
        hide_index=True,
        height=750,
        column_config={
            "Jersey": st.column_config.NumberColumn("Jersey"),
            "Max Speed (km/h)": st.column_config.ProgressColumn("Max Speed", format="%.1f km/h", min_value=0, max_value=40),
            "Total Distance (m)": st.column_config.NumberColumn("Total Distance", format="%d m"),
            "Sprint Distance (m)": st.column_config.NumberColumn("Sprint Distance", format="%d m"),
            "Sprint Count": st.column_config.NumberColumn("Sprints", format="%d"),
            "HSR Distance (m)": st.column_config.NumberColumn("HSR Distance", format="%d m"),
            "HSR Count": st.column_config.NumberColumn("HSR Count", format="%d"),
            "Player Load": st.column_config.NumberColumn("Player Load", format="%.1f"),
            "Load Intensity": st.column_config.NumberColumn("Load Intensity", format="%.2f"),
            "Max HR (bpm)": st.column_config.NumberColumn("Max HR", format="%d bpm"),
            "Avg HR (bpm)": st.column_config.NumberColumn("Avg HR", format="%d bpm"),
        }
    )
