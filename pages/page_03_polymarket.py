"""Página 3: Polymarket & Señales"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

st.set_page_config(page_title="Polymarket", layout="wide")
st.title("🎯 Polymarket & Señales Implícitas")

db = DashboardDB()
markets = db.get_latest_polymarket_signals()

if markets:
    st.subheader("📊 Mercados Activos")

    # Tabla de mercados
    df_markets = pd.DataFrame([
        {
            'Mercado': m.get('market_name', 'N/A')[:50],
            'Categoría': m.get('category', 'N/A'),
            'Probabilidad (%)': f"{m.get('probability', 50):.1f}",
            'Cambio 24h': f"{m.get('change_1d', 0):+.1f}pp",
            'Cambio 7d': f"{m.get('change_7d', 0):+.1f}pp",
            'Liquidez ($)': f"${m.get('liquidity', 0):,.0f}"
        } for m in markets
    ])

    st.dataframe(df_markets, use_container_width=True)

    # Categorías
    st.markdown("---")
    st.subheader("📈 Resumen por Categoría")

    categories = {}
    for m in markets:
        cat = m.get('category', 'other')
        prob = m.get('probability', 50)
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(prob)

    col1, col2, col3, col4 = st.columns(4)

    for i, (cat, probs) in enumerate(categories.items()):
        avg_prob = sum(probs) / len(probs)
        cols = [col1, col2, col3, col4]
        with cols[i % 4]:
            st.metric(
                f"{cat.capitalize()}",
                f"{avg_prob:.1f}%",
                f"{len(probs)} mercados"
            )

    # Índice sintético de riesgo
    st.markdown("---")
    st.subheader("🔴 Índice Sintético de Riesgo")

    escalation_signals = [m.get('probability', 50) for m in markets if m.get('category') == 'escalation']
    supply_signals = [m.get('probability', 50) for m in markets if m.get('category') == 'supply']

    escalation_avg = sum(escalation_signals) / len(escalation_signals) if escalation_signals else 50
    supply_avg = sum(supply_signals) / len(supply_signals) if supply_signals else 50

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Probabilidad Escalada (Polymarket)",
            f"{escalation_avg:.1f}%",
            "Riesgo de conflicto"
        )

    with col2:
        st.metric(
            "Probabilidad Disrupciones Suministro",
            f"{supply_avg:.1f}%",
            "Riesgo logístico"
        )

    # Histórico de un mercado (si está disponible)
    st.markdown("---")
    st.subheader("📊 Histórico de Mercados")

    selected_market = st.selectbox(
        "Selecciona un mercado para ver histórico:",
        [m.get('market_id', '') for m in markets]
    )

    if selected_market:
        market_history = db.get_polymarket_history(selected_market, days=30)
        if market_history:
            df_hist = pd.DataFrame([
                {
                    'Fecha': h.get('date'),
                    'Probabilidad': h.get('probability', 50)
                } for h in reversed(market_history)
            ])
            st.line_chart(df_hist.set_index('Fecha'), height=300)

else:
    st.warning("No hay datos de Polymarket disponibles")

st.info("""
**ℹ️ Acerca de Polymarket:**
Polymarket es una plataforma de predicción donde usuarios compran y venden contratos sobre eventos futuros.
Los precios reflejan probabilidades implícitas del mercado, ofreciendo una señal en tiempo real de expectativas
sobre riesgos geopolíticos, precios de petróleo y disrupciones de suministro.
""")
