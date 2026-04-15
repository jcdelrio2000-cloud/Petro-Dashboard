"""Página 5: Análisis Avanzado & Alertas"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

st.set_page_config(page_title="Análisis Avanzado", layout="wide")
st.title("📈 Análisis Avanzado & Alertas")

db = DashboardDB()

# Sección 1: Comparativa de cambios
st.subheader("📊 Comparativa de Cambios")

latest_score = db.get_latest_risk_score()
latest_oil = db.get_latest_oil_prices()

if latest_score and latest_oil:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Score Vs Ayer",
            f"{latest_score.get('score_change_1d', 0):+.1f}",
            "Puntos"
        )
    with col2:
        st.metric(
            "Score Vs Hace 7d",
            f"{latest_score.get('score_change_7d', 0):+.1f}",
            "Puntos"
        )
    with col3:
        st.metric(
            "Brent Vs Ayer",
            f"{latest_oil.get('brent_change_1d', 0):+.2f}",
            "%"
        )
    with col4:
        st.metric(
            "Brent Vs Hace 7d",
            f"{latest_oil.get('brent_change_7d', 0):+.2f}",
            "%"
        )
    with col5:
        st.metric(
            "Brent Vs Hace 30d",
            f"{latest_oil.get('brent_change_30d', 0):+.2f}",
            "%"
        )

# Sección 2: Histórico de scores
st.markdown("---")
st.subheader("📈 Histórico de Scores (últimos 90 días)")

scores_history = db.get_risk_scores_history(days=90)

if scores_history:
    scores_history = list(reversed(scores_history))
    df_scores = pd.DataFrame([
        {
            'Fecha': s.get('date'),
            'Score': s.get('overall_score'),
            'Nivel': s.get('risk_level')
        } for s in scores_history
    ])

    df_scores['Fecha'] = pd.to_datetime(df_scores['Fecha'])

    col1, col2 = st.columns([3, 1])

    with col1:
        st.line_chart(df_scores.set_index('Fecha')[['Score']], height=400)

    with col2:
        level_counts = df_scores['Nivel'].value_counts()
        st.bar_chart(level_counts)

# Sección 3: Desacoplamiento
st.markdown("---")
st.subheader("🔀 Análisis de Desacoplamiento")

oil_history = db.get_oil_prices_history(days=30)
scores_history = db.get_risk_scores_history(days=30)

if oil_history and scores_history:
    # Normalizar ambas series
    oil_prices = [h.get('brent_price', 0) for h in reversed(oil_history)]
    scores = [s.get('overall_score', 50) for s in reversed(scores_history)]

    # Correlación simple
    if len(oil_prices) == len(scores):
        df_comparison = pd.DataFrame({
            'Brent (norm)': [x/max(oil_prices)*100 if max(oil_prices) > 0 else 50 for x in oil_prices],
            'Score (norm)': [x/100*100 for x in scores]
        })

        st.line_chart(df_comparison, height=400)

        st.info("""
        **Interpretación:**
        - Líneas juntas: Petróleo y riesgo se mueven juntos (correlación normal)
        - Líneas separadas: Desacoplamiento (Polymarket diverge del precio)
        - Si Score ↑ pero Brent ↓: Mercado de futuros espera escalada sin impacto inmediato
        """)

# Sección 4: Alertas activas detalladas
st.markdown("---")
st.subheader("⚠️ Sistema de Alertas")

alerts = db.get_active_alerts()

if alerts:
    st.warning(f"🔴 {len(alerts)} alertas activas")

    for alert in alerts[:10]:
        severity = alert.get('severity', 'info')
        title = alert.get('title', 'Alerta')
        description = alert.get('description', '')
        timestamp = alert.get('timestamp', '')

        severity_emoji = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🔵'
        }

        st.markdown(f"{severity_emoji.get(severity, '❓')} **{title}**")
        st.markdown(f"_{description}_")
        st.caption(f"Generada: {timestamp}")
else:
    st.success("✅ Sistema en verde - No hay alertas activas")

# Sección 5: Metodología
st.markdown("---")
st.subheader("🔧 Metodología del Score")

st.markdown("""
#### Componentes del Score de Riesgo (0-100)

1. **Señal Precio Petróleo** (Peso: 20%)
   - Precio > $110: 90 pts
   - Precio $95-110: 70 pts
   - Precio $85-95: 50 pts
   - Precio < $85: 30 pts

2. **Volatilidad Petróleo** (Peso: 15%)
   - Vol > 40%: 80 pts
   - Vol 30-40%: 60 pts
   - Vol 20-30%: 40 pts
   - Vol < 20%: 20 pts

3. **Escalada (Polymarket)** (Peso: 30%)
   - Probabilidad directa de conflicto

4. **Disrupciones Suministro** (Peso: 20%)
   - Probabilidad de disrupciones logísticas

5. **Sentimiento Noticias** (Peso: 10%)
   - Agregado de noticias alcistas/bajistas

6. **Severidad Geopolítica** (Peso: 5%)
   - Número y severidad de eventos

#### Niveles de Riesgo

| Nivel | Score | Color | Acción |
|-------|-------|-------|--------|
| BAJO | 0-30 | 🟢 | Monitoreo rutinario |
| MEDIO | 30-50 | 🟡 | Vigilancia incrementada |
| ALTO | 50-75 | 🟠 | Seguimiento diario |
| CRÍTICO | 75-100 | 🔴 | Evaluación urgente |
""")

st.info("💡 Esta metodología es editable. Contactar para ajustar pesos o umbrales.")
