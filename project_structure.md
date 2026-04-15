# Estructura del Proyecto - Dashboard Geopolítico Ormuz

```
geopolitical-risk-dashboard/
│
├── README.md                          # Documentación principal
├── requirements.txt                   # Dependencias Python
├── config.yaml                        # Configuración (keys, umbrales, etc.)
│
├── data/
│   └── dashboard.db                   # Base de datos SQLite (gitignored)
│
├── scripts/
│   ├── __init__.py
│   ├── database.py                    # Inicialización y operaciones DB
│   ├── fetch_oil_prices.py            # Ingesta de precios (yfinance)
│   ├── fetch_polymarket.py            # Ingesta de Polymarket
│   ├── fetch_news.py                  # Scraping de noticias
│   ├── calculate_scores.py            # Cálculo de scores sintéticos
│   └── utils.py                       # Utilidades compartidas
│
├── dashboard/
│   ├── __init__.py
│   ├── app.py                         # Main Streamlit app
│   ├── pages/
│   │   ├── 01_📊_Resumen_Ejecutivo.py
│   │   ├── 02_🛢️_Petroleo.py
│   │   ├── 03_🎯_Polymarket.py
│   │   ├── 04_📰_Noticias.py
│   │   └── 05_📈_Analisis.py
│   └── components/
│       ├── __init__.py
│       ├── charts.py                  # Funciones de visualización
│       ├── formatters.py              # Formato de datos/valores
│       └── alerts.py                  # Lógica de alertas
│
├── .github/
│   └── workflows/
│       ├── daily-update.yml           # GitHub Actions daily
│       ├── hourly-news.yml            # GitHub Actions 4h noticias
│       └── test.yml                   # CI/CD testing
│
└── .gitignore
    # data/dashboard.db
    # .env
    # __pycache__/
```
