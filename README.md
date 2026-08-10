# Perfil de Jugadores · Performance Hub

Dashboard en [Streamlit](https://streamlit.io/) para el seguimiento individual de jugadores de fútbol: **ficha de jugador**, **GPS y carga de campo**, **composición corporal**, **fuerza máxima (1RM)**, **potencia de sprint** y **ranking del plantel**.

Construido para el uso real de un cuerpo técnico: sirve tanto para la consulta diaria por jugador como para generar un **reporte en PDF** de todo el plantel (modo reporte con saltos de página para imprimir/guardar).

## Funcionalidades

- **Ficha del jugador**: nombre, posición, nacionalidad, altura, peso y foto.
- **Métricas GPS**: velocidad máxima, distancia total, distancia de sprint, cantidad de sprints, aceleración máxima y carga en kcal.
- **Radar comparativo**: perfil atlético del jugador **vs. el promedio del plantel** (Plotly).
- **Composición corporal**: IMC, % grasa (con [Jackson–Pollock](https://en.wikipedia.org/wiki/Skinfold_measurement) por pliegues cuando hay datos, o estimación por IMC), masa muscular y estado físico.
- **Fuerza máxima (1RM)**: squat, press banca, peso muerto y curl de bíceps.
- **Análisis de sprint**: repeticiones, distancia y eficiencia (m/sprint), más saltabilidad (CMJ/SJ).
- **Ranking del plantel**: tabla ordenada por velocidad máxima con barras de progreso.
- **Modo reporte**: checkbox "Todos / Report Mode" que recorre a todos los jugadores con `page-break` entre fichas → **Ctrl+P → Guardar como PDF**.

## Archivos

| Archivo | Descripción |
|---|---|
| `perfil.py` | App principal: `jugadores_stats.xls`, fotos por jugador y leaderboard bilingüe (ES/中文). |
| `perfil_esp_v2.py` | V2: `jugadores_stats_latinos.xls`, radar contra promedio de plantel, carga robusta de datos y exportación a PDF desde el botón. |

Ambas comparten el mismo diseño visual (tipografía Barlow Condensed + paleta `#00a8cc` / `#38bdf8`).

## Datos

El app lee planillas Excel de **múltiples hojas** (`Antropometria`, `Fuerza`, `Saltabilidad` y la hoja principal de GPS):

- `jugadores_stats.xls` → `perfil.py`
- `jugadores_stats_latinos.xls` → `perfil_esp_v2.py`

El loader limpia headers, convierte a numérico (`errors='coerce'` + `fillna(0)`) y maneja valores sucios reales (p. ej. rangos `"370~410"` en kcal se promedian). Todo con `@st.cache_data` para no releer Excel en cada interacción.

## Cómo correrlo

```bash
pip install streamlit pandas plotly xlrd   # xlrd para archivos .xls
streamlit run perfil.py                    # o: streamlit run perfil_esp_v2.py
```

> Ejecutar desde la carpeta del proyecto (las rutas de datos son relativas al directorio de trabajo).
