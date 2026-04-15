"""
Página 1: Resumen Ejecutivo
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

st.set_page_config(page_title="Resumen Ejecutivo", page_icon="📊", layout="wide")

st.title("📊 Resumen Ejecutivo")

db = DashboardDB()

# ============================================================================
# SECCIÓN 1: SCORE DE RIESGO PRINCIPAL
# ============================================================================
col1, col2, col3 = st.columns([2, 1, 1])

latest_score = db.get_latest_risk_score()

if latest_score:
    score = latest_score.get('overall_score', 0)
    level = latest_score.get('risk_level', 'unknown')
    change_1d = latest_score.get('score_change_1d', 0)
    commentary = latest_score.get('commentary', '')

    # Determinar color basado en nivel
    if level == 'low':
        score_color = "🟢"
        level_text = "BAJO"
        color_hex = "#2ecc71"
    elif level == 'medium':
        score_color = "🟡"
        level_text = "MEDIO"
        color_hex = "#f39c12"
    elif level == 'high':
        score_color = "🟠"
        level_text = "ALTO"
        color_hex = "#e74c3c"
    else:
        score_color = "🔴"
        level_text = "CRÍTICO"
        color_hex = "#8b0000"

    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {color_hex}20 0%, {color_hex}10 100%);
            border: 3px solid {color_hex};
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin: 10px 0;
        ">
            <h2 style="margin: 0; color: {color_hex};">{score_color} RIESGO GEOPOLÍTICO</h2>
            <h1 style="margin: 20px 0; font-size: 4em; color: {color_hex};">{score:.1f}</h1>
            <p style="font-size: 1.3em; margin: 0; color: {color_hex};">Nivel: <strong>{level_text}</strong></p>
            <p style="font-size: 0.9em; margin-top: 10px; color: #666;">
                Cambio 24h: <strong style="color: {'green' if change_1d <= 0 else 'red'};color: {color_hex};">
                {change_1d:+.1f}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.metric("Score Cambio 7d", f"{latest_score.get('score_change_7d', 0):+.1f}")
        st.metric("Driver Principal", latest_score.get('primary_driver', 'N/A'))

    with col3:
        st.metric("Actualizado", latest_score.get('timestamp', '')[:10])
        if level in ['high', 'critical']:
            st.warning("⚠️ Alerta Activa")

else:
    st.error("No hay datos de score disponibles")

# ============================================================================
# SECCIÓN 2: COMENTARIO EJECUTIVO
# ============================================================================
st.markdown("---")
st.subheader("🔍 Análisis del Día")

if latest_score:
    st.info(f"💬 {latest_score.get('commentary', 'Sin comentarios disponibles')}")

# ============================================================================
# SECCIÓN 3: KPIs PRINCIPALES
# ============================================================================
st.markdown("---")
st.subheader("📈 Métricas Clave")

col1, col2, col3, col4 = st.columns(4)

latest_oil = db.get_latest_oil_prices()
latest_polymarket = db.get_latest_polymarket_signals()

with col1:
    if latest_oil:
        brent = latest_oil.get('brent_price', 0)
        change = latest_oil.get('brent_change_1d', 0)
        st.metric(
            "🛢️ Brent Spot",
            f"${brent:.2f}",
            f"{change:+.2f}%",
            delta_color="inverse"
        )
    else:
        st.metric("🛢️ Brent Spot", "N/A")

with col2:
    if latest_oil:
        wti = latest_oil.get('wti_price', 0)
        change = latest_oil.get('wti_change_1d', 0)
        st.metric(
            "⛽ WTI",
            f"${wti:.2f}",
            f"{change:+.2f}%",
            delta_color="inverse"
        )
    else:
        st.metric("⛽ WTI", "N/A")

with col3:
    if latest_oil:
        vol = latest_oil.get('brent_volatility_30d', 0)
        vol_level = "🔴 Alta" if vol > 25 else "🟡 Media" if vol > 15 else "🟢 Baja"
        st.metric(
            "📊 Volatilidad 30d",
            f"{vol:.1f}%",
            vol_level
        )
    else:
        st.metric("📊 Volatilidad 30d", "N/A")

with col4:
    if latest_score:
        signal = latest_score.get('polymarket_escalation', 50)
        st.metric(
            "🎯 Escalada (Polymarket)",
            f"{signal:.0f}%",
            f"{'↑ Riesgo' if signal > 70 else '↓ Estable' if signal < 40 else '→ Moderado'}"
        )
    else:
        st.metric("🎯 Escalada (Polymarket)", "N/A")

# ============================================================================
# SECCIÓN 4: DESCOMPOSICIÓN DEL SCORE
# ============================================================================
st.markdown("---")
st.subheader("🔧 Descomposición del Score")

if latest_score:
    components = {
        'Señal Precio Petróleo': latest_score.get('oil_price_signal', 0),
        'Volatilidad Petróleo': latest_score.get('oil_volatility_signal', 0),
        'Escalada (Polymarket)': latest_score.get('polymarket_escalation', 0),
        'Disrupciones Suministro': latest_score.get('polymarket_supply', 0),
        'Sentimiento Noticias': latest_score.get('news_sentiment_signal', 0),
        'Severidad Geopolítica': latest_score.get('geopolitical_severity', 0)
    }

    # Crear DataFrame
    df_components = pd.DataFrame([
        {'Componente': k, 'Puntos': v} for k, v in components.items()
    ])

    # Gráfico de barras
    col1, col2 = st.columns([2, 1])

    with col1:
        st.bar_chart(df_components.set_index('Componente'), height=300)

    with col2:
        st.markdown("**Pesos en Score Final:**")
        weights = {
            'Escalada (Polymarket)': '30%',
            'Señal Precio Petróleo': '20%',
            'Disrupciones Suministro': '20%',
            'Volatilidad Petróleo': '15%',
            'Sentimiento Noticias': '10%',
            'Severidad Geopolítica': '5%'
        }
        for component, weight in weights.items():
            st.text(f"{component}: {weight}")

# ============================================================================
# SECCIÓN 5: NOTICIAS DEL DÍA
# ============================================================================
st.markdown("---")
st.subheader("📰 Noticias del Día")

today_news = db.get_today_news()

if today_news:
    st.info(f"📊 {len(today_news)} noticia(s) relevante(s) hoy")

    for i, news in enumerate(today_news[:5], 1):  # Mostrar top 5
        title = news.get('title', 'Sin título')
        source = news.get('source', 'Unknown')
        impact = news.get('impact_level', 'medium')
        direction = news.get('impact_direction', '→')
        summary = news.get('summary', '')
        url = news.get('url', '#')
        time = news.get('time', '')

        # Color del impacto
        if impact == 'high':
            impact_color = "🔴"
        elif impact == 'medium':
            impact_color = "🟡"
        else:
            impact_color = "🟢"

        # Dirección
        if direction == '↑':
            direction_color = "text-danger"  # Rojo (alcista para petróleo)
            direction_text = "Alcista (↑ Precio)"
        elif direction == '↓':
            direction_color = "text-success"  # Verde (bajista)
            direction_text = "Bajista (↓ Precio)"
        else:
            direction_color = "text-muted"
            direction_text = "Neutral"

        with st.expander(f"{impact_color} [{time}] {title[:60]}... ({source})"):
            st.markdown(f"**Fuente:** {source}")
            st.markdown(f"**Impacto:** {impact.upper()} | **Dirección:** {direction_text}")
            st.markdown(f"**Resumen:** {summary}")
            st.markdown(f"[🔗 Leer artículo completo]({url})")

else:
    st.info("No hay noticias relevantes en el día")

# ============================================================================
# SECCIÓN 6: ALERTAS ACTIVAS
# ============================================================================
st.markdown("---")
st.subheader("⚠️ Alertas Activas")

alerts = db.get_active_alerts()

if alerts:
    for alert in alerts[:5]:
        severity = alert.get('severity', 'info')
        title = alert.get('title', 'Alerta')
        description = alert.get('description', '')

        if severity == 'critical':
            st.error(f"🔴 **{title}** - {description}")
        elif severity == 'warning':
            st.warning(f"🟡 **{title}** - {description}")
        else:
            st.info(f"🔵 **{title}** - {description}")
else:
    st.success("✅ No hay alertas activas")

# ============================================================================
# SECCIÓN 7: MINI GRÁFICO HISTÓRICO
# ============================================================================
st.markdown("---")
st.subheader("📈 Brent - Últimos 30 Días")

oil_history = db.get_oil_prices_history(days=30)

if oil_history:
    df_oil = pd.DataFrame([
        {
            'Fecha': news['date'],
            'Brent': news.get('brent_price'),
            'WTI': news.get('wti_price')
        } for news in reversed(oil_history)
    ])

    df_oil['Fecha'] = pd.to_datetime(df_oil['Fecha'])
    df_oil = df_oil.set_index('Fecha')

    st.line_chart(df_oil)

# ============================================================================
# PIE DE PÁGINA
# ============================================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"⏱️ Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")

with col2:
    st.caption("🔄 Auto-actualiza: Noticias cada hora, Precios diarios, Scores continuo")

with col3:
    st.caption("💾 Histórico: 12 meses de datos archivados")
