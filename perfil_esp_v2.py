import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ============================
# CONFIGURACIÓN Y ESTILO V2.0
# ============================
st.set_page_config(page_title="Performance Hub V2", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700;900&family=Inter:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Barlow Condensed', sans-serif; }

.player-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 30px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    border-left: 6px solid #38bdf8;
}
.player-name { font-family: 'Barlow Condensed', sans-serif; font-size: 48px; font-weight: 900; line-height: 1; text-transform: uppercase; letter-spacing: 1px; }
.player-meta { font-size: 16px; color: #94a3b8; margin-top: 10px; font-weight: 600; }

.metric-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px;
    text-align: center; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); transition: transform 0.2s;
    height: 100%;
}
.metric-card:hover { transform: translateY(-3px); border-color: #38bdf8; }
.metric-label { font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
.metric-value { font-family: 'Barlow Condensed', sans-serif; font-size: 34px; font-weight: 700; color: #0f172a; margin: 5px 0;}
.metric-unit { font-size: 14px; color: #94a3b8; }
.metric-relative { font-size: 13px; color: #0ea5e9; font-weight: 600; background: #e0f2fe; padding: 4px 8px; border-radius: 20px; display: inline-block; margin-top:5px;}

.section-title {
    font-family: 'Barlow Condensed', sans-serif; font-size: 24px; font-weight: 700;
    color: #1e293b; border-bottom: 3px solid #38bdf8; display: inline-block; margin-bottom: 20px; padding-bottom: 5px; margin-top: 20px;
}

@media print {
    .page-break { display: block; page-break-before: always; break-before: page; }
    .stSidebar, button, .stTabs [role="tablist"], [data-testid="stHeader"] { display: none !important; }
    .metric-card { page-break-inside: avoid; }
}
</style>
""", unsafe_allow_html=True)

# ============================
# FUNCIONES DE CARGA ROBUSTAS
# ============================
def clean_kcal(val):
    if isinstance(val, str) and '~' in val:
        try:
            parts = [float(p) for p in val.split('~')]
            return sum(parts) / len(parts)
        except: return 0
    return pd.to_numeric(val, errors='coerce')

@st.cache_data
def load_all_data():
    file_name = "jugadores_stats_latinos.xls"
    try:
        xls = pd.ExcelFile(file_name)
        sheets = xls.sheet_names
        df_main = pd.read_excel(xls, sheets[0])
        df_main.columns = df_main.columns.str.strip() # Limpiamos espacios en los nombres de columnas
        
        if 'Calor(Kcal)' in df_main.columns:
            df_main['Calor(Kcal)'] = df_main['Calor(Kcal)'].apply(clean_kcal)

        # Incluimos las métricas numéricas necesarias
        cols_num = ['Maxima velocidad', 'Distancia Total(m)', 'Distancia de sprint(m)', 'Conteo de sprints', 'Max Acc (g)', 'Calor(Kcal)']
        for c in cols_num:
            if c in df_main.columns:
                df_main[c] = pd.to_numeric(df_main[c], errors='coerce').fillna(0) # Convertimos a numérico y llenamos NaN con 0
                
        df_salt = pd.read_excel(xls, "Saltabilidad") if "Saltabilidad" in sheets else pd.DataFrame()
        if not df_salt.empty: df_salt.columns = df_salt.columns.str.strip()

        return {'main': df_main, 'salt': df_salt}
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None

data = load_all_data()
if not data or data['main'].empty:
    st.stop()

df_main = data['main'] # df_main Dataframe principal
df_salt = data['salt'] # df_salt Dataframe de saltabilidad


# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8084/8084128.png", width=80)
    st.markdown("### Total Performance Hub")
    report_mode = st.checkbox("All Players (Report Mode)")
    if report_mode:
        selected_players = df_main['Deportista'].unique().tolist()
    else:
        jugador_choice = st.selectbox("Seleccionar Deportista", df_main['Deportista'].unique())
        selected_players = [jugador_choice]
    
    if st.button("📄 Exportar a PDF"):
        st.components.v1.html("<script>window.parent.print();</script>", height=0, width=0)
    st.caption("v2.0 Analytics - GPS & Gym")

# ======================
# FUNCIONES DE RENDERIZADO
# ======================
def render_header(p_name):
    p = df_main[df_main['Deportista'] == p_name].iloc[0]
    st.markdown(f"""
    <div class="player-header">
        <div class="player-name">{p.get('Deportista', p_name)}</div>
        <div class="player-meta">
            {p.get('Posicion', 'POSICIÓN')} | {p.get('Nacionalidad', 'NACIONALIDAD')} | {p.get('Equipo', 'CLUB')} <br>
            ALTURA: {p.get('Altura (mts)', '--')} m | PESO: {p.get('Peso (kg)', '--')} kg
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_gps_metrics(p_name):
    p = df_main[df_main['Deportista'] == p_name].iloc[0]
    col_met, col_rad = st.columns([1.2, 1])
    with col_met:
        st.markdown('<div class="section-title">Métricas de GPS</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        metrics = [
            ("Velocidad Máxima", p.get('Maxima velocidad', 0), "km/h", "Peak Speed"),
            ("Distancia Total", p.get('Distancia Total(m)', 0), "m", "Volumen Total"),
            ("Distancia Sprint", p.get('Distancia de sprint(m)', 0), "m", "High Intensity"),
            ("Cant. Sprints", p.get('Conteo de sprints', 0), "veces", "Repetition"),
            ("Aceleración Máx", p.get('Max Acc (g)', 0), "g", "Explosividad"),
            ("Carga (Calorías)", p.get('Calor(Kcal)', 0), "kcal", "Energy Expenditure")
        ]
        for i, (label, val, unit, desc) in enumerate(metrics):
            box = c1 if i % 2 == 0 else c2
            val_str = f"{val:.2f}" if isinstance(val, float) and val < 100 else f"{val:.0f}"
            box.markdown(f"""
            <div class="metric-card" style="margin-bottom: 15px;">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val_str} <span class="metric-unit">{unit}</span></div>
                <div style="font-size:11px;color:#94a3b8">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    with col_rad:
        st.markdown('<div class="section-title">Perfil Atlético vs Plantel</div>', unsafe_allow_html=True)
        radar_cols = ['Maxima velocidad', 'Distancia Total(m)', 'Conteo de sprints', 'Max Acc (g)', 'Calor(Kcal)']
        radar_labels = ['Velocidad', 'Volumen', 'Sprints', 'Aceleración', 'Carga']
        jugador_vals_norm, avg_vals_norm = [], []
        for col in radar_cols:
            max_squad = df_main[col].max() if df_main[col].max() > 0 else 1
            jugador_vals_norm.append((p.get(col, 0) / max_squad) * 100)
            avg_vals_norm.append((df_main[col].mean() / max_squad) * 100)
        fig_gps = go.Figure()
        fig_gps.add_trace(go.Scatterpolar(r=avg_vals_norm, theta=radar_labels, fill='toself', name='Promedio Plantel', line_color='rgba(148, 163, 184, 0.5)'))
        fig_gps.add_trace(go.Scatterpolar(r=jugador_vals_norm, theta=radar_labels, fill='toself', name=p_name, line_color='#0ea5e9'))
        fig_gps.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, margin=dict(t=40, b=40), showlegend=True)
        st.plotly_chart(fig_gps, use_container_width=True)

# ======================
# LÓGICA DE PESTAÑAS
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
    st.markdown('<div class="section-title">Ranking General del Equipo</div>', unsafe_allow_html=True)
    
    # Definición de columnas y renombramiento
    cols_ranking = {
        'Deportista': 'Jugador', 
        'Maxima velocidad': 'Vel. Máx (km/h)', 
        'Distancia de sprint(m)': 'Dist. Sprint (m)', 
        'Distancia Total(m)': 'Dist. Total (m)', 
        'Conteo de sprints': 'Sprints', 
        'Max Acc (g)': 'Acel. Máx (g)'
    }
    
    df_ranking = df_main[list(cols_ranking.keys())].copy().rename(columns=cols_ranking)
    
    # Mostramos la tabla ordenada por Velocidad Máxima (Descendente)
    st.dataframe(
        df_ranking.sort_values(by='Vel. Máx (km/h)', ascending=False), 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Vel. Máx (km/h)": st.column_config.ProgressColumn("Velocidad Máxima", format="%.2f", min_value=0, max_value=40),
            "Dist. Sprint (m)": st.column_config.NumberColumn("Sprint Total", format="%d m"),
            "Dist. Total (m)": st.column_config.NumberColumn(format="%d m"),
            "Acel. Máx (g)": st.column_config.NumberColumn(format="%.2f g")
        }
    )