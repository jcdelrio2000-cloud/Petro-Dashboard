"""
app.py
Aplicación Streamlit principal - Dashboard de Riesgo Geopolítico Ormuz
"""

import streamlit as st
from pathlib import Path
import sys

# Configuración de página
st.set_page_config(
    page_title="Dashboard Geopolítico Ormuz",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Agregar estilos personalizados
st.markdown("""
    <style>
    /* Colores del semáforo */
    .risk-low { color: #2ecc71; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-high { color: #e74c3c; font-weight: bold; }
    .risk-critical { color: #8b0000; font-weight: bold; }

    /* Tarjetas KPI */
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2c3e50;
        margin: 10px 0;
    }

    /* Encabezados */
    h1 {
        color: #1a1a1a;
        border-bottom: 3px solid #2c3e50;
        padding-bottom: 10px;
    }

    /* Tablas */
    .table-compact { font-size: 0.85em; }
    </style>
""", unsafe_allow_html=True)

# Información del dashboard en la barra lateral
st.sidebar.title("📊 Dashboard Geopolítico")
st.sidebar.markdown("""
### Estrecho de Ormuz
**Monitoreo de Riesgo & Precio Petróleo**

---

### Actualizaciones
- 🛢️ Precios: Diariamente
- 🎯 Polymarket: Cada 6 horas
- 📰 Noticias: Cada hora
- 📈 Scores: Automático

---

### Últimas métricas
""")

# Cargar datos
sys.path.insert(0, str(Path(__file__).parent))
try:
    from database import DashboardDB
    db = DashboardDB()

    # Mostrar score actual en sidebar
    latest_score = db.get_latest_risk_score()
    latest_oil = db.get_latest_oil_prices()

    if latest_score:
        score = latest_score.get('overall_score', 0)
        level = latest_score.get('risk_level', 'unknown')

        if level == 'low':
            emoji = "🟢"
        elif level == 'medium':
            emoji = "🟡"
        elif level == 'high':
            emoji = "🟠"
        else:
            emoji = "🔴"

        st.sidebar.metric(
            f"{emoji} Score Riesgo",
            f"{score:.1f}/100",
            f"{latest_score.get('score_change_1d', 0):+.1f} vs ayer"
        )

    if latest_oil:
        st.sidebar.metric(
            "🛢️ Brent",
            f"${latest_oil.get('brent_price', 0):.2f}",
            f"{latest_oil.get('brent_change_1d', 0):+.2f}% 1d"
        )

except Exception as e:
    st.sidebar.error(f"Error cargando datos: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### Acerca de este dashboard
**Propósito:** Monitoreo ejecutivo de riesgo geopolítico
en el Estrecho de Ormuz y su impacto en el precio del petróleo.

**Componentes:**
- Precios: yfinance
- Probabilidades: Polymarket
- Noticias: NewsAPI
- Score: Metodología propia

**Actualizado:** Automáticamente mediante GitHub Actions

---

**Contacto:** jcdelrio2000@gmail.com
""")

# Página principal
st.title("🛢️ Dashboard de Riesgo Geopolítico - Estrecho de Ormuz")

st.markdown("""
### 📌 ¿Qué monitorea este dashboard?

Este dashboard proporciona un **resumen ejecutivo** del riesgo geopolítico asociado al Estrecho de Ormuz
y su relación con el precio del petróleo Brent y WTI.

**Módulos principales:**
- **📊 Resumen Ejecutivo**: Score de riesgo, métricas clave, alertas
- **🛢️ Módulo Petróleo**: Precios históricos, volatilidad, análisis técnico
- **🎯 Polymarket**: Probabilidades implícitas de riesgos geopolíticos
- **📰 Noticias**: Cobertura en tiempo real de eventos relevantes
- **📈 Análisis Avanzado**: Cambios, correlaciones, alertas

---

### 🚀 Cómo usar

1. **Navega por las pestañas** en el menú lateral izquierdo
2. **Revisa el Resumen Ejecutivo** para contexto rápido
3. **Analiza tendencias** en la sección de gráficos históricos
4. **Monitorea alertas activas** para cambios significativos
5. **Comparte el link** con colegas para consultas colaborativas

---

### ⚠️ Interpretación de niveles

| Nivel | Score | Significado | Acción |
|-------|-------|-------------|--------|
| 🟢 **BAJO** | 0-30 | Riesgo mínimo | Monitoreo de rutina |
| 🟡 **MEDIO** | 30-50 | Riesgo moderado | Vigilancia incrementada |
| 🟠 **ALTO** | 50-75 | Riesgo considerable | Seguimiento diario |
| 🔴 **CRÍTICO** | 75-100 | Riesgo extremo | Evaluación urgente |

---

### 📚 Fuentes de datos

**Petróleo:** Yahoo Finance (yfinance)
**Polymarket:** API pública de Polymarket
**Noticias:** NewsAPI + Reuters, Bloomberg, FT
**Análisis:** Cálculos internos de riesgo

""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85em;">
<p>Dashboard de Riesgo Geopolítico v1.0 | Actualizado automáticamente |
<a href="mailto:jcdelrio2000@gmail.com">Contactar</a></p>
</div>
""", unsafe_allow_html=True)
