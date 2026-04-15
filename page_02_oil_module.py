"""Página 2: Módulo Petróleo"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

st.set_page_config(page_title="Módulo Petróleo", layout="wide")
st.title("🛢️ Módulo Petróleo")

db = DashboardDB()
history = db.get_oil_prices_history(days=365)

if history:
    # Invertir para que esté en orden cronológico
    history = list(reversed(history))
    df = pd.DataFrame([
        {
            'Fecha': h['date'],
            'Brent': h.get('brent_price'),
            'WTI': h.get('wti_price'),
            'Vol_Brent': h.get('brent_volatility_30d'),
            'Cambio_1d': h.get('brent_change_1d')
        } for h in history
    ])

    df['Fecha'] = pd.to_datetime(df['Fecha'])

    # Sección 1: Gráficos principales
    st.subheader("📊 Histórico de Precios (12 Meses)")

    col1, col2 = st.columns(2)

    with col1:
        st.line_chart(df.set_index('Fecha')[['Brent', 'WTI']], height=400)

    with col2:
        st.area_chart(df.set_index('Fecha')[['Vol_Brent']], height=400)

    # Sección 2: Estadísticas
    st.markdown("---")
    st.subheader("📈 Estadísticas")

    latest = history[-1]

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Brent Actual", f"${latest.get('brent_price', 0):.2f}")
    with col2:
        st.metric("Cambio 1d", f"{latest.get('brent_change_1d', 0):+.2f}%")
    with col3:
        st.metric("Cambio 7d", f"{latest.get('brent_change_7d', 0):+.2f}%")
    with col4:
        st.metric("Cambio 30d", f"{latest.get('brent_change_30d', 0):+.2f}%")
    with col5:
        st.metric("Volatilidad 30d", f"{latest.get('brent_volatility_30d', 0):.2f}%")

    # Sección 3: Tabla histórica
    st.markdown("---")
    st.subheader("📋 Histórico Detallado (últimos 30 días)")

    df_display = pd.DataFrame([
        {
            'Fecha': h['date'],
            'Brent ($)': f"${h.get('brent_price', 0):.2f}",
            'WTI ($)': f"${h.get('wti_price', 0):.2f}",
            'Cambio 1d (%)': f"{h.get('brent_change_1d', 0):+.2f}",
            'Vol 30d (%)': f"{h.get('brent_volatility_30d', 0):.2f}"
        } for h in history[-30:]
    ])

    st.dataframe(df_display, use_container_width=True)

    # Sección 4: Análisis
    st.markdown("---")
    st.subheader("🔍 Análisis")

    min_price = df['Brent'].min()
    max_price = df['Brent'].max()
    curr_price = latest.get('brent_price', 0)

    st.markdown(f"""
    **Rango 12 meses:**
    - Mínimo: ${min_price:.2f}
    - Máximo: ${max_price:.2f}
    - Actual: ${curr_price:.2f}
    - Posición en rango: {((curr_price - min_price) / (max_price - min_price) * 100):.1f}%
    """)

else:
    st.warning("No hay datos de petróleo disponibles")
