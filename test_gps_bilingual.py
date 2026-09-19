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
.cn {
    color: #6b7280;
    font-size: 0.82em;
    font-weight: 400;
}
</style>
""", unsafe_allow_html=True)

# ======================
# CONFIG
# ======================
SESSIONS_DIR = "sessions"   # las planillas .xls van dentro de esta carpeta
ROSTER_FILE = "roster.xlsx"  # Le agregue Apodo y numero
PHOTO_DIR = "photo"         # Foto de cada uno
LOGO_FILE = "logo.png"      # Logo del equipo (raiz del proyecto)

MIN_MINUTES = 10            # sesiones/jugadores con menos minutos NO entran en promedios ni ranking acumulado
TOP_N = 10                  # cuantos jugadores se marcan en el ranking de todas las sesiones

def load_logo_b64():
    if not os.path.exists(LOGO_FILE):
        return None
    with open(LOGO_FILE, "rb") as f:
        return base64.b64encode(f.read()).decode()

LOGO_B64 = load_logo_b64()

# ======================
# BILINGUAL STRINGS (EN · 中文)
# MI(clave) -> "EN · 中文"     texto plano, para widgets (tabs, selectbox, metric, column_config)
# MIH(clave) -> "EN <span class='cn'>中文</span>"   HTML, para st.markdown / HTML
# ======================
L = {
    # --- Sidebar ---
    "session": ("Session", "训练课"),
    "select_training": ("Select Training Session", "选择训练课"),
    "team": ("Team", "队伍"),
    "field": ("Field", "场地"),
    "players": ("Players", "球员"),
    "view": ("View", "视图"),
    "audience": ("Audience", "对象"),
    "coach": ("Coach (all metrics)", "教练（全部指标）"),
    "player_friendly": ("Player-friendly (simple)", "球员友好（简单）"),
    "player_selection": ("Player Selection", "选择球员"),
    "all_players": ("All Players (Report Mode)", "所有球员（报告模式）"),
    "select_player": ("Select Player", "选择球员"),
    "export_pdf": ("Export to PDF", "导出PDF"),
    "pdf_hint": ("Press Ctrl + P (or Cmd + P) → Save as PDF", "按 Ctrl + P 保存为 PDF"),
    "could_not_read": ("Could not read", "无法读取"),
    "no_sessions": ("No GPS session files found", "未找到 GPS 数据文件"),
    "no_roster": ("No roster found — showing raw GPS names", "未找到名单 — 显示原始GPS姓名"),
    # --- Tabs ---
    "tab_gps": ("GPS & Load", "体能负荷"),
    "tab_sprint": ("Sprint Power", "冲刺能力"),
    "tab_squad": ("Squad Leaderboard", "球队排行"),
    "tab_records": ("Squad Records", "球队纪录"),
    # --- Sections ---
    "physical": ("Physical Performance", "体能表现"),
    "average": ("Average — all sessions", "场均（全部训练课）"),
    "no_avg": ("No sessions of {} min to average.", "没有达到 {} 分钟的训练课，无法计算场均。"),
    "sprint_analysis": ("Sprint-Specific Analysis", "冲刺专项分析"),
    "hsr": ("High-Speed Running (HSR)", "高速跑（HSR）"),
    "squad_ranking": ("Squad Overall Ranking", "球队整体排行"),
    "glossary": ("Glossary — what each metric means", "术语表 — 各指标含义"),
    # --- Metrics ---
    "Max Speed": ("Max Speed", "最高速度"),
    "Total Distance": ("Total Distance", "总距离"),
    "Sprints": ("Sprints", "冲刺次数"),
    "avg_per_sprint": ("Avg per Sprint", "平均冲刺"),
    "Time on Field": ("Time on Field", "上场时间"),
    "Sprint Count": ("Sprint Count", "冲刺次数"),
    "Sprint Distance": ("Sprint Distance", "冲刺距离"),
    "HSR Distance": ("HSR Distance", "高速跑距离"),
    "HSR Count": ("HSR Count", "高速跑次数"),
    "Player Load": ("Player Load", "球员负荷"),
    "Load Intensity": ("Load Intensity", "负荷强度"),
    "Max HR": ("Max HR", "最大心率"),
    "Avg HR": ("Avg HR", "平均心率"),
    # --- Radar categories ---
    "Speed": ("Speed", "速度"),
    "Distance": ("Distance", "距离"),
    "Load": ("Load", "负荷"),
    "Intensity": ("Intensity", "强度"),
    # --- Records dashboard ---
    "group": ("Group", "分组"),
    "metric": ("Metric", "指标"),
    "volume": ("Volume", "体量"),
    "intensity_k": ("Intensity", "强度"),
    "records_sub": ("Best single-session mark per player (no averages). Squad distribution by category.",
                    "每个球员的单场最佳成绩（非平均值）。全队按类别分布。"),
    "records_meta": ("{} players · {} sessions", "{} 名球员 · {} 场训练课"),
    "squad_avg": ("Squad Average", "球队平均"),
    "team_best": ("Team Best", "队内最佳"),
    "above_p75": ("Above P75", "超过P75"),
    "counted": ("players counted", "名球员计入"),
    "p75plus": ("P75+", "顶级"),
    "p50_75": ("P50–P75", "中上"),
    "lt_p50": ("<P50", "待提升"),
    "avg_mark": ("squad average", "球队平均"),
    "no_data": ("No valid data for", "无有效数据"),
    "best_total_distance": ("Best Total Distance", "最佳总距离"),
    "best_sprint_count": ("Best Sprint Count", "最佳冲刺次数"),
    "best_sprint_dist": ("Best Sprint Distance", "最佳冲刺距离"),
    "best_hsr_dist": ("Best HSR Distance", "最佳高速跑距离"),
    "best_hsr_count": ("Best HSR Count", "最佳高速跑次数"),
    "best_load": ("Best Player Load", "最佳球员负荷"),
    "best_max_speed": ("Best Max Speed", "最佳最高速度"),
    "best_intensity": ("Best Load Intensity", "最佳负荷强度"),
    "best_maxhr": ("Best Max HR", "最佳最大心率"),
    "narr_line": (
        "{metric}: squad average {avg} {unit}. {leader} leads with {best} {unit} (P100). "
        "{n} of {n_rows} players above P75 ({thr} {unit}).",
        "{metric}：球队平均 {avg} {unit}。{leader} 以 {best} {unit}（P100）领先。{n}/{n_rows} 名球员超过P75（{thr} {unit}）。",
    ),
    "table_note": (
        "Each column = player's best in ONE session (no averages). Only {n}+ min sessions count. "
        "Light blue = squad record.",
        "每列 = 球员单场最佳成绩（非平均值）。仅计入 {n} 分钟以上的训练课。浅蓝色 = 全队纪录。",
    ),
    "best": ("Best", "最佳"),
}

def MI(key):
    en, zh = L[key]
    return f"{en} · {zh}"

def MIH(key):
    en, zh = L[key]
    return f"{en} <span class='cn'>· {zh}</span>"

def MIZH(key):
    return L[key][1]

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

# What each metric means - shown in the in-app glossary. Values: (EN, 中文)
GLOSSARY = {
    "Time on Field": ("Minutes the vest actually logged. Context for everything else: 90' of a match is not the same as 20' of a drill.",
                      "背心实际记录的分钟数，用于理解其他数据：90分钟比赛 ≠ 20分钟训练。"),
    "Max HR": ("Highest heart rate reached. Measures internal effort — what it cost the body, beyond how far it ran.",
               "本次训练达到的最高心率，衡量身体内部负荷。"),
    "Avg HR": ("Average heart rate across the session. High distance + low avg HR usually means the player was not at real intensity.",
               "整场训练的平均心率。距离多但平均心率低，通常说明强度不够。"),
    "Player Load": ("Total external load: sum of all accelerations and decelerations. The best single summary of how hard the body worked.",
                    "外部总负荷：所有加速与减速之和，最能概括身体的总体工作量。"),
    "Load Intensity": ("Player Load divided by minutes played. Lets a 90' match and a 20' drill be compared fairly.",
                       "总负荷除以出场分钟数，让90分钟比赛与20分钟训练可以公平对比。"),
    "Total Distance": ("Total metres covered. Aerobic volume — who really runs the pitch and who walks it.",
                       "总跑动距离（米），衡量有氧工作总量。"),
    "Max Speed": ("Maximum running speed reached. Pure sprint capacity — the easiest metric to understand and compare.",
                  "最高跑动速度，纯冲刺能力，最容易理解和对比的指标。"),
    "HSR Distance": ("Metres run at high speed (below full sprint). Shows ability to repeat intense efforts.",
                     "高速跑距离（低于冲刺），反映重复高强度跑动的能力。"),
    "HSR Count": ("Number of high-speed runs.",
                  "高速跑的次数。"),
    "Sprint Distance": ("Metres run at maximum sprint speed — the explosive actions that usually decide plays.",
                        "最高速度下的冲刺跑距离，通常是决定比赛回合的爆发动作。"),
    "Sprint Count": ("Number of sprints. Packs work rate and explosiveness into a single number.",
                     "冲刺次数，用一个数字概括工作投入度与爆发力。"),
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
            st.sidebar.warning(f"{MI('could_not_read')} {os.path.basename(path)}: {e}")

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
    st.error(f"{MI('no_sessions')} in '{SESSIONS_DIR}/'. Drop your .xlsx exports there and reload. 将 .xlsx 文件放入该目录后重新加载。")
    st.stop()
if roster.empty:
    st.sidebar.warning(f"{MI('no_roster')} — add it to link nicknames and photos. 添加名单以关联昵称和照片。")

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

st.sidebar.markdown(f"### {MI('session')}")
session_label = st.sidebar.selectbox(MI('select_training'), list(sessions.keys()))
meta, df_main = sessions[session_label]

st.sidebar.markdown(
    f"**{MI('team')}:** {meta.get('Team', '-')}  \n"
    f"**{MI('field')}:** {meta.get('Field', '-')}  \n"
    f"**{MI('players')}:** {meta.get('Player Count', len(df_main))}"
)

st.sidebar.markdown(f"### {MI('view')}")
view_mode = st.sidebar.radio(MI('audience'), [MI('coach'), MI('player_friendly')])

st.sidebar.markdown(f"### {MI('player_selection')}")
report_mode = st.sidebar.checkbox(MI('all_players'))

name_options = df_main.sort_values('Display Name')['Display Name'].unique()
if report_mode:
    selected_players = name_options.tolist()
else:
    selected_players = [st.sidebar.selectbox(MI('select_player'), name_options)]

if st.sidebar.button(MI('export_pdf')):
    st.sidebar.info(MI('pdf_hint'))

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
                    {session_label} • {p.get('Time on Field (min)', 0):.0f} min on field · 上场时间
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
        st.markdown(f'<div class="section-title">{MIH("physical")}</div>', unsafe_allow_html=True)

        all_metrics = [
            ("Max Speed", f"{p['Max Speed (km/h)']:.1f} km/h"),
            ("Total Distance", f"{p['Total Distance (m)']:.0f} m"),
            ("Sprints", f"{p['Sprint Count']:.0f} reps"),
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
        metrics = all_metrics if view_mode == MI('player_friendly') else all_metrics + coach_only_metrics

        c1, c2 = st.columns(2)
        for i, (label, value) in enumerate(metrics):
            box = c1 if i % 2 == 0 else c2
            val_part, unit_part = value.split()[0], " ".join(value.split()[1:])
            box.markdown(f"""
            <div class="attribute-box">
                <div class="attribute-label">{MIH(label)}</div>
                <div class="attribute-value" style="font-size:20px">{val_part}</div>
                <div style="font-size:11px;color:#6b7280">{unit_part}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_radar:
        if view_mode == MI('player_friendly'):
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
        radar_cats = [MI(c) for c in categories]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=radar_values, theta=radar_cats, fill='toself', name=display_name, line=dict(color='#00a8cc')))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%")), showlegend=False, margin=dict(t=40, b=40, l=40, r=40), height=320, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, key=f"radar_{display_name}")

def render_avg_metrics(display_name):
    """Same boxes as the daily card, but with the average of ALL the player's sessions."""
    g = all_df[all_df['Display Name'] == display_name]
    n = g['Session'].nunique()
    st.markdown(f'<div class="section-title">{MIH("average")} ({n})</div>', unsafe_allow_html=True)
    if g.empty:
        st.caption(f"{L['no_avg'][0].format(MIN_MINUTES)}\n\n{L['no_avg'][1].format(MIN_MINUTES)}")
        return

    avg = g.mean(numeric_only=True)
    best_speed = g['Max Speed (km/h)'].max()

    all_metrics = [
        ("Max Speed", fmt(avg['Max Speed (km/h)'], "{:.1f}"), f"km/h · best {fmt(best_speed, '{:.1f}')}"),
        ("Total Distance", fmt(avg['Total Distance (m)']), "m"),
        ("Sprints", fmt(avg['Sprint Count'], "{:.1f}"), "reps"),
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
    metrics = all_metrics if view_mode == MI('player_friendly') else all_metrics + coach_only_metrics

    cols = st.columns(4)
    for i, (label, val_part, unit_part) in enumerate(metrics):
        cols[i % 4].markdown(f"""
        <div class="attribute-box">
            <div class="attribute-label">{MIH(label)}</div>
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
    f"🏃‍♂️ {MI('tab_gps')}", f"⚡ {MI('tab_sprint')}", f"🥇 {MI('tab_squad')}", f"🏆 {MI('tab_records')}",
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

    if view_mode == MI('coach'):
        with st.expander(f"📖 {MIH('glossary')}"):
            for label, (en, zh) in GLOSSARY.items():
                st.markdown(f"**{MIH(label)}** — {en}  \n{zh}")

with tab2:
    for i, player in enumerate(selected_players):
        if report_mode and i > 0:
            st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
        if report_mode:
            render_header(player)
        p = get_row(player)
        st.markdown(f"### {MI('sprint_analysis')}")
        dist_sprint = p.get('Sprint Distance (m)', 0)
        cant_sprint = p.get('Sprint Count', 0)
        eficiencia = dist_sprint / cant_sprint if cant_sprint > 0 else 0
        c1, c2, c3 = st.columns(3)
        c1.metric(MI('Sprints'), f"{cant_sprint:.0f}")
        c2.metric(MI('Sprint Distance'), f"{dist_sprint:.0f} m")
        c3.metric(MI('avg_per_sprint'), f"{eficiencia:.1f} m/sprint")

        if view_mode == MI('coach'):
            st.markdown(f'<div class="section-title">{MIH("hsr")}</div>', unsafe_allow_html=True)
            h1, h2 = st.columns(2)
            h1.metric(MI('HSR Distance'), f"{p.get('HSR Distance (m)', 0):.0f} m")
            h2.metric(MI('HSR Count'), f"{p.get('HSR Count', 0):.0f} un")
        if report_mode:
            st.divider()

with tab3:
    st.markdown(f'<div class="section-title">{MIH("squad_ranking")}</div>', unsafe_allow_html=True)

    if view_mode == MI('player_friendly'):
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
            "Jersey": st.column_config.NumberColumn("Jersey", help="Jersey · 号码"),
            "Player": st.column_config.TextColumn("Player · 球员"),
            "Max Speed (km/h)": st.column_config.ProgressColumn(MI('Max Speed'), format="%.1f km/h", min_value=0, max_value=40),
            "Total Distance (m)": st.column_config.NumberColumn(MI('Total Distance'), format="%d m"),
            "Sprint Distance (m)": st.column_config.NumberColumn(MI('Sprint Distance'), format="%d m"),
            "Sprint Count": st.column_config.NumberColumn(MI('Sprints'), format="%d"),
            "HSR Distance (m)": st.column_config.NumberColumn(MI('HSR Distance'), format="%d m"),
            "HSR Count": st.column_config.NumberColumn(MI('HSR Count'), format="%d"),
            "Player Load": st.column_config.NumberColumn(MI('Player Load'), format="%.1f"),
            "Load Intensity": st.column_config.NumberColumn(MI('Load Intensity'), format="%.2f"),
            "Max HR (bpm)": st.column_config.NumberColumn(MI('Max HR'), format="%d bpm"),
            "Avg HR (bpm)": st.column_config.NumberColumn(MI('Avg HR'), format="%d bpm"),
        }
    )

with tab4:
    if all_df.empty:
        st.info(f"{L['no_avg'][0].format(MIN_MINUTES)} · {L['no_avg'][1].format(MIN_MINUTES)}")
    else:
        lb = build_records(all_df)

        n_players = len(lb)
        n_sessions = int(all_df['Session'].nunique())

        st.markdown(
            f'<div class="records-header">{MIH("tab_records")}</div>'
            f'<div class="records-sub">{MIH("records_sub")}</div>'
            f'<div class="records-meta">{L["records_meta"][0].format(n_players, n_sessions)} · '
            f'<span class="cn">{L["records_meta"][1].format(n_players, n_sessions)}</span></div>',
            unsafe_allow_html=True,
        )

        metric_groups = {
            MI('volume'): [
                ('Best Total Distance', 'BestDist', 'm', "{:.0f}", 'best_total_distance'),
                ('Best Sprint Count', 'BestSprints', 'sprints', "{:.0f}", 'best_sprint_count'),
                ('Best Sprint Distance', 'BestSprintDist', 'm', "{:.0f}", 'best_sprint_dist'),
                ('Best HSR Distance', 'BestHSRDist', 'm', "{:.0f}", 'best_hsr_dist'),
                ('Best HSR Count', 'BestHSRCount', 'veces', "{:.0f}", 'best_hsr_count'),
                ('Best Player Load', 'BestLoad', 'au', "{:.0f}", 'best_load'),
            ],
            MI('intensity_k'): [
                ('Best Max Speed', 'BestSpeed', 'km/h', "{:.1f}", 'best_max_speed'),
                ('Best Load Intensity', 'BestIntensity', 'au/min', "{:.2f}", 'best_intensity'),
                ('Best Max HR', 'BestMaxHR', 'bpm', "{:.0f}", 'best_maxhr'),
            ],
        }

        c_sel = st.columns([1, 3])
        with c_sel[0]:
            group = st.segmented_control(MI('group'), list(metric_groups), default=MI('intensity_k'), key="pk_group")
        with c_sel[1]:
            metric_opts = {MI(lkey): (key, unit, spec, lkey) for lab, key, unit, spec, lkey in metric_groups[group]}
            metric = st.selectbox(MI('metric'), list(metric_opts), key="pk_metric")
        metric_key, unit, spec, lkey = metric_opts[metric]

        vals = lb[['Display Name', 'Jersey', metric_key]].dropna(subset=[metric_key]).copy()
        vals = vals[vals[metric_key] > 0].sort_values(metric_key, ascending=False).reset_index(drop=True)

        if vals.empty:
            st.info(f"{MI(lkey)} — {L['no_data'][1]}.")
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
                f'<div class="pk-kpi"><div class="pk-kpi-label">{MIH("squad_avg")}</div>'
                f'<div class="pk-kpi-value">{spec.format(avg_val)}<span class="pk-unit"> {unit}</span></div>'
                f'<div class="pk-kpi-sub">{n_rows} players counted · {n_rows} 名球员计入</div></div>'
                f'<div class="pk-kpi"><div class="pk-kpi-label">{MIH("team_best")}</div>'
                f'<div class="pk-kpi-value">{spec.format(best_val)}<span class="pk-unit"> {unit}</span></div>'
                f'<div class="pk-kpi-sub">{leader_name}{leader_jersey}</div></div>'
                f'<div class="pk-kpi"><div class="pk-kpi-label">{MIH("above_p75")}</div>'
                f'<div class="pk-kpi-value">{n_p75}<span class="pk-unit"> players</span></div>'
                f'<div class="pk-kpi-sub">≥ {spec.format(p75_thr)} {unit}</div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="pk-legend">'
                f'<span><span class="pk-dot pk-green"></span>{MI("p75plus")}</span>'
                f'<span><span class="pk-dot pk-amber"></span>{MI("p50_75")}</span>'
                f'<span><span class="pk-dot pk-grey"></span>{MI("lt_p50")}</span>'
                f'<span style="margin-left:auto">⋮ {MI("avg_mark")}</span>'
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

            narr_en = L["narr_line"][0].format(
                metric=MI(lkey), avg=spec.format(avg_val), unit=unit,
                leader=leader_name, best=spec.format(best_val),
                n=n_p75, n_rows=n_rows, thr=spec.format(p75_thr),
            )
            narr_zh = L["narr_line"][1].format(
                metric=MI(lkey), avg=spec.format(avg_val), unit=unit,
                leader=leader_name, best=spec.format(best_val),
                n=n_p75, n_rows=n_rows, thr=spec.format(p75_thr),
            )
            st.caption(f"{narr_en}\n\n{narr_zh}")

        st.markdown("---")

        labels = {
            'Jersey': 'Jersey', 'Display Name': 'Player',
            'BestSpeed': MI('best_max_speed'), 'BestDist': MI('best_total_distance'),
            'BestSprints': MI('best_sprint_count'), 'BestSprintDist': MI('best_sprint_dist'),
            'BestHSRDist': MI('best_hsr_dist'), 'BestHSRCount': MI('best_hsr_count'),
            'BestLoad': MI('best_load'), 'BestIntensity': MI('best_intensity'),
            'BestMaxHR': MI('best_maxhr'),
        }
        cols_lb = [
            'Jersey', 'Display Name', 'BestSpeed', 'BestDist', 'BestSprints',
            'BestSprintDist', 'BestHSRDist', 'BestHSRCount', 'BestLoad',
            'BestIntensity', 'BestMaxHR',
        ]

        styled = lb[cols_lb].rename(columns=labels).style.highlight_max(
            axis=0,
            subset=[
                MI('best_max_speed'), MI('best_total_distance'), MI('best_sprint_count'),
                MI('best_sprint_dist'), MI('best_hsr_dist'), MI('best_hsr_count'),
                MI('best_load'), MI('best_intensity'), MI('best_maxhr'),
            ],
            color='#e0f2fe',
        )

        st.dataframe(
            styled,
            use_container_width=True,
            hide_index=True,
            height=560,
            column_config={
                "Jersey": st.column_config.NumberColumn("Jersey", help="Jersey · 号码"),
                "Player": st.column_config.TextColumn("Player · 球员"),
                MI('best_max_speed'): st.column_config.ProgressColumn(MI('best_max_speed'), format="%.1f km/h", min_value=0, max_value=40),
                MI('best_total_distance'): st.column_config.NumberColumn(MI('best_total_distance'), format="%.0f m"),
                MI('best_sprint_count'): st.column_config.NumberColumn(MI('best_sprint_count'), format="%d"),
                MI('best_sprint_dist'): st.column_config.NumberColumn(MI('best_sprint_dist'), format="%.0f m"),
                MI('best_hsr_dist'): st.column_config.NumberColumn(MI('best_hsr_dist'), format="%.0f m"),
                MI('best_hsr_count'): st.column_config.NumberColumn(MI('best_hsr_count'), format="%d"),
                MI('best_load'): st.column_config.NumberColumn(MI('best_load'), format="%.1f"),
                MI('best_intensity'): st.column_config.NumberColumn(MI('best_intensity'), format="%.2f"),
                MI('best_maxhr'): st.column_config.NumberColumn(MI('best_maxhr'), format="%d bpm"),
            },
        )

        note_en = L["table_note"][0].format(n=MIN_MINUTES)
        note_zh = L["table_note"][1].format(n=MIN_MINUTES)
        st.caption(f"{note_en}\n\n{note_zh}")