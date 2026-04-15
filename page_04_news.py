"""Página 4: Noticias & Eventos"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

st.set_page_config(page_title="Noticias", layout="wide")
st.title("📰 Noticias & Eventos")

db = DashboardDB()

# Selector de período
col1, col2 = st.columns(2)
with col1:
    days_back = st.slider("Mostrar noticias de últimos X días", 1, 30, 7)
with col2:
    filter_impact = st.multiselect(
        "Filtrar por impacto",
        ["low", "medium", "high"],
        default=["low", "medium", "high"],
        format_func=lambda x: {"low": "Bajo", "medium": "Medio", "high": "Alto"}[x]
    )

news_history = db.get_news_history(days=days_back)

if news_history:
    # Filtrar
    news_filtered = [n for n in news_history if n.get('impact_level') in filter_impact]

    st.metric("Noticias encontradas", len(news_filtered))

    st.markdown("---")

    if news_filtered:
        # Agrupar por fecha
        dates = {}
        for news in news_filtered:
            date = news.get('date', 'Unknown')
            if date not in dates:
                dates[date] = []
            dates[date].append(news)

        # Mostrar por fecha
        for date in sorted(dates.keys(), reverse=True):
            st.subheader(f"📅 {date}")

            for news in dates[date]:
                title = news.get('title', 'Sin título')
                source = news.get('source', 'Unknown')
                impact = news.get('impact_level', 'medium')
                direction = news.get('impact_direction', '→')
                summary = news.get('summary', '')
                url = news.get('url', '#')
                time = news.get('time', '')

                # Color del impacto
                impact_colors = {
                    'high': '🔴 Alto',
                    'medium': '🟡 Medio',
                    'low': '🟢 Bajo'
                }

                direction_icons = {
                    '↑': '📈 Alcista (↑ Precio)',
                    '↓': '📉 Bajista (↓ Precio)',
                    '→': '➡️ Neutral'
                }

                with st.expander(f"{impact_colors.get(impact, '?')} | {time} | {title[:60]}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{title}**")
                    with col2:
                        st.caption(source)
                    with col3:
                        st.caption(direction_icons.get(direction, direction))

                    st.markdown(f"**Resumen:** {summary}")
                    st.markdown(f"[🔗 Leer en la fuente]({url})")
    else:
        st.info("No hay noticias con los filtros seleccionados")

else:
    st.info("No hay noticias en el período seleccionado")

# Estadísticas
st.markdown("---")
st.subheader("📊 Estadísticas de Noticias")

if news_history:
    col1, col2, col3 = st.columns(3)

    high_impact = len([n for n in news_history if n.get('impact_level') == 'high'])
    bullish = len([n for n in news_history if n.get('impact_direction') == '↑'])
    bearish = len([n for n in news_history if n.get('impact_direction') == '↓'])

    with col1:
        st.metric("Noticias de Alto Impacto", high_impact)
    with col2:
        st.metric("Noticias Alcistas", bullish)
    with col3:
        st.metric("Noticias Bajistas", bearish)
