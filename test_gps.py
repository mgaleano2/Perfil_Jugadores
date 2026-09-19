import base64
import glob
import html
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Player Profile - GPS", layout="wide")

# ============================
# WHITE AND BLUE, clean style
# ============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght=700;900&family=Barlow:wght=400;600&family=Space+Mono&display=swap');

[data-testid="stAppViewContainer"] { background: #ffffff; }
section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid rgba(0,0,0,0.08); }

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
.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 20px;
    letter-spacing: 2px;
    border-bottom: 2px solid rgba(0,168,204,0.25);
    margin-top: 35px;
    margin-bottom: 15px;
}
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
.records-header {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 26px;
    letter-spacing: 2px;
    font-weight: 900;
    color: #0e3a5d;
    margin: 0;
}
.records-sub {
    color: #6b7280;
    font-size: 14px;
    margin: 2px 0 6px;
}
.records-meta {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    color: #00a8cc;
    margin-bottom: 16px;
}
.pk-kpis {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 0 0 18px;
}
@media (max-width: 900px) { .pk-kpis { grid-template-columns: 1fr; } }
.pk-kpi {
    background: #f7f9fc;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-top: 3px solid #00a8cc;
    border-radius: 10px;
    padding: 12px 14px;
}
.pk-kpi-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #6b7280;
}
.pk-kpi-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: #0e3a5d;
    line-height: 1.15;
}
.pk-kpi-sub {
    font-size: 11px;
    color: #6b7280;
}
.pk-kpi .pk-unit {
    font-size: 13px;
    color: #6b7280;
}
.pk-legend {
    display: flex;
    gap: 16px;
    margin: 6px 0 10px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.5px;
    color: #6b7280;
}
.pk-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
}
.pk-green { background: #22c55e; }
.pk-amber { background: #f59e0b; }
.pk-grey { background: #cbd5e1; }
.pk-bars {
    background: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 12px;
    padding: 10px 18px 14px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05);
}
.pk-row {
    display: grid;
    grid-template-columns: 34px 220px minmax(120px, 1fr) 130px;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px dashed rgba(0, 0, 0, 0.05);
}
.pk-row:last-child { border-bottom: none; }
.pk-rank {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #9ca3af;
}
.pk-rank-lead { color: #00a8cc; font-weight: 700; }
.pk-name {
    display: flex;
    align-items: center;
    min-width: 0;
    overflow: hidden;
    white-space: nowrap;
    font-size: 14px;
}
.pk-name .pk-dot { margin-right: 8px; flex-shrink: 0; }
.pk-who { font-weight: 600; }
.pk-who-lead { color: #0e3a5d; }
.pk-jersey { color: #00a8cc; font-weight: 700; font-size: 12px; margin-left: 6px; }
.pk-track { position: relative; }
.pk-bar {
    position: relative;
    height: 8px;
    border-radius: 6px;
    background: #eef2f7;
}
.pk-fill {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    border-radius: 6px;
    background: #cbd5e1;
}
.pk-fill-lead { background: linear-gradient(90deg, #00a8cc, #38bdf8); }
.pk-avg {
    position: absolute;
    top: -4px;
    bottom: -4px;
    width: 0;
    border-left: 1px dashed rgba(0, 168, 204, 0.6);
}
.pk-val {
    font-family: 'Barlow Condensed', sans-serif;
    text-align: right;
    white-space: nowrap;
}
.pk-num { font-size: 20px; font-weight: 700; color: #0e3a5d; }
.pk-unit { font-size: 11px; color: #6b7280; margin-left: 4px; }
.pk-pct {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #9ca3af;
    margin-left: 8px;
}
</style>
""", unsafe_allow_html=True)

# ======================
# CONFIG
# ======================
SESSIONS_DIR = "sessions"   # las planillas .xls van dentro de esta carpeta
ROSTER_FILE = "roster.xlsx"  # Le agregue Apodo y numero
PHOTO_DIR = "photo"         # Foto de cada uno
LOGO_FILE = "logo.png1"      # Logo del equipo (raiz del proyecto)

MIN_MINUTES = 10            # sesiones/jugadores con menos minutos NO entran en promedios ni ranking acumulado
TOP_N = 10                  # cuantos jugadores se marcan en el ranking de todas las sesiones

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


# Metrics considered simple/motivating enough to show players directly
PLAYER_FACING_METRICS = ["Max Speed", "Total Distance", "Sprint Count", "Time on Field"]

# ======================
# HELPERS
# ======================
def fmt(value, spec="{:.0f}"):
    """Format a number, or '-' when the value is missing."""
    return "-" if pd.isna(value) else spec.format(value)

def _mtime(path):
    return os.path.getmtime(path) if os.path.exists(path) else 0

def data_signature():
    """Changes whenever a session file is added, removed or edited, so the cache reloads
    (before, a new .xlsx in sessions/ did not show up until the app was restarted)."""
    return tuple((p, _mtime(p)) for p in sorted(glob.glob(os.path.join(SESSIONS_DIR, "*.xlsx"))))

# ======================
# LOAD DATA FUNCTIONS
# ======================
@st.cache_data
def load_roster(signature):
    # 'signature' is only the cache key (roster file mtime)
    if not os.path.exists(ROSTER_FILE):
        return pd.DataFrame(columns=["Name", "Jersey", "Nickname", "Photo"])
    df = pd.read_excel(ROSTER_FILE)
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_sessions(_roster, signature):
    # '_roster' is not hashed by Streamlit; 'signature' is what invalidates the cache
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

roster = load_roster(_mtime(ROSTER_FILE))
sessions = load_sessions(roster, data_signature())

if not sessions:
    st.error(f"No GPS session files found in '{SESSIONS_DIR}/'. Drop your .xlsx exports there and reload.")
    st.stop()
if roster.empty:
    st.sidebar.warning(f"No '{ROSTER_FILE}' found — showing raw GPS names. Add it to link nicknames and photos.")

# ======================
# ALL-SESSIONS DATA (for averages and the all-sessions ranking)
# ======================
def build_all_sessions(sessions):
    """Stack every session in one table. Only valid data is kept for averages:
    - rows with fewer than MIN_MINUTES on the field are dropped
    - a max speed / HR of 0 (signal lost, exported as blank) is treated as missing, not as a real 0."""
    frames = []
    for label, (_, d) in sessions.items():
        f = d.copy()
        f['Session'] = label
        frames.append(f)
    all_df = pd.concat(frames, ignore_index=True)
    for c in ['Max Speed (km/h)', 'Max HR (bpm)', 'Avg HR (bpm)']:
        all_df[c] = all_df[c].where(all_df[c] > 0)
    return all_df[all_df['Time on Field (min)'] >= MIN_MINUTES].copy()

all_df = build_all_sessions(sessions)

def build_records(all_df):
    """One row per player with their BEST single-session mark per metric (records-style,
    not averages). Every qualifying session in the folder counts."""
    lb = all_df.groupby('Display Name').agg(
        Jersey=('Jersey', 'last'),
        BestSpeed=('Max Speed (km/h)', 'max'),
        BestDist=('Total Distance (m)', 'max'),
        BestSprints=('Sprint Count', 'max'),
        BestSprintDist=('Sprint Distance (m)', 'max'),
        BestHSRDist=('HSR Distance (m)', 'max'),
        BestHSRCount=('HSR Count', 'max'),
        BestLoad=('Player Load', 'max'),
        BestIntensity=('Load Intensity', 'max'),
        BestMaxHR=('Max HR (bpm)', 'max'),
    ).reset_index()
    return lb.sort_values('BestSpeed', ascending=False, na_position='last').reset_index(drop=True)

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

def render_avg_metrics(display_name):
    """Same boxes as the daily card, but with the average of ALL the player's sessions."""
    g = all_df[all_df['Display Name'] == display_name]
    n = g['Session'].nunique()
    st.markdown(f'<div class="section-title">Average — all sessions ({n})</div>', unsafe_allow_html=True)
    if g.empty:
        st.caption(f"No hay sesiones de {MIN_MINUTES}+ min para promediar.")
        return

    avg = g.mean(numeric_only=True)
    best_speed = g['Max Speed (km/h)'].max()

    all_metrics = [
        ("Max Speed", fmt(avg['Max Speed (km/h)'], "{:.1f}"), f"km/h · best {fmt(best_speed, '{:.1f}')}"),
        ("Total Distance", fmt(avg['Total Distance (m)']), "m"),
        ("Sprints", fmt(avg['Sprint Count'], "{:.1f}"), "un"),
        ("Time on Field", fmt(avg['Time on Field (min)']), "min"),
    ]
    coach_only_metrics = [
        ("Sprint Distance", fmt(avg['Sprint Distance (m)']), "m"),
        ("HSR Distance", fmt(avg['HSR Distance (m)']), "m"),
        ("HSR Count", fmt(avg['HSR Count'], "{:.1f}"), "un"),
        ("Player Load", fmt(avg['Player Load'], "{:.1f}"), "au"),
        ("Load Intensity", fmt(avg['Load Intensity'], "{:.2f}"), "au/min"),
        ("Max HR", fmt(avg['Max HR (bpm)']), "bpm"),
        ("Avg HR", fmt(avg['Avg HR (bpm)']), "bpm"),
    ]
    metrics = all_metrics if view_mode.startswith("Player") else all_metrics + coach_only_metrics

    cols = st.columns(4)
    for i, (label, val_part, unit_part) in enumerate(metrics):
        cols[i % 4].markdown(f"""
        <div class="attribute-box">
            <div class="attribute-label">{label}</div>
            <div class="attribute-value" style="font-size:20px">{val_part}</div>
            <div style="font-size:11px;color:#6b7280">{unit_part}</div>
        </div>
        """, unsafe_allow_html=True)

# ======================
# TAB LOGIC
# ======================
if not report_mode:
    render_header(selected_players[0])

tab1, tab2, tab3, tab4 = st.tabs([
    "🏃‍♂️ GPS & Load", "⚡ Sprint Power", "🥇 Squad Leaderboard", "🏆 Squad Records",
])

with tab1:
    for i, player in enumerate(selected_players):
        if report_mode and i > 0:
            st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
        if report_mode:
            render_header(player)
        render_gps_metrics(player)
        render_avg_metrics(player)
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

with tab4:
    if all_df.empty:
        st.info(f"No hay sesiones de {MIN_MINUTES}+ min para armar el tablero de récords.")
    else:
        lb = build_records(all_df)

        n_players = len(lb)
        n_sessions = int(all_df['Session'].nunique())

        st.markdown(
            '<div class="records-header">Squad Records</div>'
            '<div class="records-sub">La mejor marca de cada jugador en una sola sesión (sin promedios). '
            'Distribución del plantel por categoría.</div>'
            f'<div class="records-meta">{n_players} jugadores · {n_sessions} sesiones</div>',
            unsafe_allow_html=True,
        )

        metric_groups = {
            'Volumen': [
                ('Best Total Distance', 'BestDist', 'm', "{:.0f}"),
                ('Best Sprint Count', 'BestSprints', 'sprints', "{:.0f}"),
                ('Best Sprint Distance', 'BestSprintDist', 'm', "{:.0f}"),
                ('Best HSR Distance', 'BestHSRDist', 'm', "{:.0f}"),
                ('Best HSR Count', 'BestHSRCount', 'veces', "{:.0f}"),
                ('Best Player Load', 'BestLoad', 'au', "{:.0f}"),
            ],
            'Intensidad': [
                ('Best Max Speed', 'BestSpeed', 'km/h', "{:.1f}"),
                ('Best Load Intensity', 'BestIntensity', 'au/min', "{:.2f}"),
                ('Best Max HR', 'BestMaxHR', 'bpm', "{:.0f}"),
            ],
        }

        c_sel = st.columns([1, 3])
        with c_sel[0]:
            group = st.segmented_control("Grupo", list(metric_groups), default="Intensidad", key="pk_group")
        with c_sel[1]:
            metric_opts = {lab: (key, unit, spec) for lab, key, unit, spec in metric_groups[group]}
            metric = st.selectbox("Métrica", list(metric_opts), key="pk_metric")
        metric_key, unit, spec = metric_opts[metric]

        vals = lb[['Display Name', 'Jersey', metric_key]].dropna(subset=[metric_key]).copy()
        vals = vals[vals[metric_key] > 0].sort_values(metric_key, ascending=False).reset_index(drop=True)

        if vals.empty:
            st.info(f"Sin datos válidos para {metric}.")
        else:
            best_val = vals[metric_key].iloc[0]
            avg_val = vals[metric_key].mean()
            p75_thr = vals[metric_key].quantile(0.75)
            n_p75 = int((vals[metric_key] >= p75_thr).sum())
            vals['pct'] = (vals[metric_key].rank(pct=True) * 100).round().astype(int)
            n_rows = len(vals)

            leader_row = vals.iloc[0]
            leader_name = html.escape(str(leader_row['Display Name']))
            leader_jersey = f' #{int(leader_row["Jersey"])}' if pd.notna(leader_row['Jersey']) else ''

            st.markdown(
                f'<div class="pk-kpis">'
                f'<div class="pk-kpi"><div class="pk-kpi-label">Promedio plantel</div>'
                f'<div class="pk-kpi-value">{spec.format(avg_val)}<span class="pk-unit"> {unit}</span></div>'
                f'<div class="pk-kpi-sub">{n_rows} jugadores computados</div></div>'
                f'<div class="pk-kpi"><div class="pk-kpi-label">Team best</div>'
                f'<div class="pk-kpi-value">{spec.format(best_val)}<span class="pk-unit"> {unit}</span></div>'
                f'<div class="pk-kpi-sub">{leader_name}{leader_jersey}</div></div>'
                f'<div class="pk-kpi"><div class="pk-kpi-label">Superan P75</div>'
                f'<div class="pk-kpi-value">{n_p75}<span class="pk-unit"> jug.</span></div>'
                f'<div class="pk-kpi-sub">≥ {spec.format(p75_thr)} {unit}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="pk-legend">'
                '<span><span class="pk-dot pk-green"></span>P75+' + '</span>'
                '<span><span class="pk-dot pk-amber"></span>P50–P75</span>'
                '<span><span class="pk-dot pk-grey"></span>&lt;P50</span>'
                f'<span style="margin-left:auto">⋮ promedio plantel</span>'
                '</div>',
                unsafe_allow_html=True,
            )

            avg_pct = avg_val / best_val * 100 if best_val > 0 else 0
            rows_html = []
            for i, (_, r) in enumerate(vals.iterrows(), start=1):
                val_pct = r[metric_key] / best_val * 100
                pct = int(r['pct'])
                flag = 'pk-green' if pct >= 75 else ('pk-amber' if pct >= 50 else 'pk-grey')
                name = html.escape(str(r['Display Name']))
                jersey = f'<span class="pk-jersey">#{int(r["Jersey"])}</span>' if pd.notna(r['Jersey']) else ''
                leader = i == 1
                rows_html.append(
                    f'<div class="pk-row">'
                    f'<div class="pk-rank{" pk-rank-lead" if leader else ""}">{i:02d}</div>'
                    f'<div class="pk-name">'
                    f'<span class="pk-dot {flag}"></span>'
                    f'<span class="pk-who{" pk-who-lead" if leader else ""}">{name}{" " + jersey if jersey else ""}</span>'
                    f'</div>'
                    f'<div class="pk-track">'
                    f'<div class="pk-bar"><div class="pk-fill{" pk-fill-lead" if leader else ""}" style="width:{val_pct:.1f}%"></div></div>'
                    f'<div class="pk-avg" style="left:{avg_pct:.1f}%"></div>'
                    f'</div>'
                    f'<div class="pk-val"><span class="pk-num">{spec.format(r[metric_key])}</span>'
                    f'<span class="pk-unit"> {unit}</span><span class="pk-pct">P{pct}</span></div>'
                    f'</div>'
                )
            st.markdown(f'<div class="pk-bars">{"".join(rows_html)}</div>', unsafe_allow_html=True)

            st.caption(
                f"{metric}: el promedio del plantel es {spec.format(avg_val)} {unit}. "
                f"{leader_name} lidera con {spec.format(best_val)} {unit} (P100). "
                f"{n_p75} de {n_rows} jugadores superan el P75 ({spec.format(p75_thr)} {unit})."
            )

        st.markdown("---")

        labels = {
            'Jersey': 'Jersey', 'Display Name': 'Player', 'BestSpeed': 'Best Max Speed',
            'BestDist': 'Best Total Distance', 'BestSprints': 'Best Sprint Count',
            'BestSprintDist': 'Best Sprint Distance', 'BestHSRDist': 'Best HSR Distance',
            'BestHSRCount': 'Best HSR Count', 'BestLoad': 'Best Player Load',
            'BestIntensity': 'Best Load Intensity', 'BestMaxHR': 'Best Max HR',
        }
        cols_lb = [
            'Jersey', 'Display Name', 'BestSpeed', 'BestDist', 'BestSprints',
            'BestSprintDist', 'BestHSRDist', 'BestHSRCount', 'BestLoad',
            'BestIntensity', 'BestMaxHR',
        ]

        styled = lb[cols_lb].rename(columns=labels).style.highlight_max(
            axis=0,
            subset=[
                'Best Max Speed', 'Best Total Distance', 'Best Sprint Count',
                'Best Sprint Distance', 'Best HSR Distance', 'Best HSR Count',
                'Best Player Load', 'Best Load Intensity', 'Best Max HR',
            ],
            color='#e0f2fe',
        )

        st.dataframe(
            styled,
            use_container_width=True,
            hide_index=True,
            height=560,
            column_config={
                "Jersey": st.column_config.NumberColumn("Jersey"),
                "Best Max Speed": st.column_config.ProgressColumn("Best Max Speed", format="%.1f km/h", min_value=0, max_value=40),
                "Best Total Distance": st.column_config.NumberColumn("Best Total Distance", format="%.0f m"),
                "Best Sprint Count": st.column_config.NumberColumn("Best Sprint Count", format="%d"),
                "Best Sprint Distance": st.column_config.NumberColumn("Best Sprint Distance", format="%.0f m"),
                "Best HSR Distance": st.column_config.NumberColumn("Best HSR Distance", format="%.0f m"),
                "Best HSR Count": st.column_config.NumberColumn("Best HSR Count", format="%d"),
                "Best Player Load": st.column_config.NumberColumn("Best Player Load", format="%.1f"),
                "Best Load Intensity": st.column_config.NumberColumn("Best Load Intensity", format="%.2f"),
                "Best Max HR": st.column_config.NumberColumn("Best Max HR", format="%d bpm"),
            },
        )

        st.caption(
            f"Cada columna = mejor marca del jugador en UNA sola sesión (no promedios). "
            f"Solo cuentan sesiones de {MIN_MINUTES}+ minutos. Celeste = récord del equipo."
        )