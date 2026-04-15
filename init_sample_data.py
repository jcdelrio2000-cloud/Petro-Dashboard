"""
init_sample_data.py
Script para generar datos históricos de ejemplo y llenar la BD inicialmente
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

def generate_sample_oil_data():
    """Generar datos históricos de petróleo de ejemplo"""
    db = DashboardDB()
    db.cleanup_old_data(retention_days=1)  # Limpiar primero

    print("Generando datos históricos de petróleo...")

    base_brent = 80.0
    base_wti = 75.0

    for days_ago in range(365, 0, -1):
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        # Simular movimientos realistas de precios
        brent_price = base_brent + random.uniform(-5, 5)
        wti_price = base_wti + random.uniform(-5, 5)

        # Cambios porcentuales
        if days_ago < 365:
            prev_brent = base_brent - random.uniform(-0.5, 0.5)
            change_1d = ((brent_price - prev_brent) / prev_brent * 100)
        else:
            change_1d = random.uniform(-2, 2)

        change_7d = random.uniform(-5, 5)
        change_30d = random.uniform(-10, 15)

        # Volatilidad
        vol = random.uniform(10, 35)

        brent = {
            'price': round(brent_price, 2),
            'change_1d': round(change_1d, 2),
            'change_7d': round(change_7d, 2),
            'change_30d': round(change_30d, 2),
            'volatility_30d': round(vol, 2)
        }

        wti = {
            'price': round(wti_price, 2),
            'change_1d': round(change_1d * 0.95, 2),
            'change_7d': round(change_7d * 0.95, 2),
            'change_30d': round(change_30d * 0.95, 2),
            'volatility_30d': round(vol * 0.9, 2)
        }

        db.insert_oil_prices(date, brent, wti)
        base_brent = brent_price
        base_wti = wti_price

    print("✅ Datos de petróleo generados (365 días)")

def generate_sample_polymarket_data():
    """Generar datos históricos de Polymarket de ejemplo"""
    db = DashboardDB()

    print("Generando datos históricos de Polymarket...")

    markets = [
        {
            "id": "market_escalation_1",
            "name": "Will Iran launch military strikes against Israel by June 30, 2026?",
            "category": "escalation",
            "weight": 0.25
        },
        {
            "id": "market_supply_1",
            "name": "Will oil supply disruption occur in Middle East by June 30, 2026?",
            "category": "supply",
            "weight": 0.25
        },
        {
            "id": "market_hormuz_1",
            "name": "Will Strait of Hormuz shipping return to normal by April 30, 2026?",
            "category": "logistics",
            "weight": 0.25
        },
        {
            "id": "market_price_1",
            "name": "Will WTI crude oil exceed $85/barrel in April 2026?",
            "category": "price",
            "weight": 0.25
        }
    ]

    for days_ago in range(90, 0, -1):
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        for market in markets:
            # Generar probabilidades realistas
            base_prob = {
                "escalation": 45,
                "supply": 55,
                "logistics": 35,
                "price": 50
            }

            prob = base_prob.get(market['category'], 50) + random.uniform(-10, 10)
            prob = max(10, min(90, prob))  # Mantener entre 10-90%

            market_data = {
                'id': market['id'],
                'name': market['name'],
                'category': market['category'],
                'probability': round(prob, 1),
                'price': round(prob / 100, 2),
                'change_1d': round(random.uniform(-5, 5), 1),
                'change_7d': round(random.uniform(-10, 10), 1),
                'liquidity': random.uniform(1000, 50000),
                'volume_24h': random.uniform(100, 5000),
                'yes_shares_in_pool': random.uniform(1000, 100000),
                'no_shares_in_pool': random.uniform(1000, 100000)
            }

            db.insert_polymarket_signal(date, market_data)

    print("✅ Datos de Polymarket generados (90 días)")

def generate_sample_news():
    """Generar noticias de ejemplo"""
    db = DashboardDB()

    print("Generando noticias de ejemplo...")

    news_samples = [
        {
            "title": "Iran's Nuclear Program Raises Regional Tensions",
            "source": "Reuters",
            "summary": "International observers report increased uranium enrichment at Iranian facilities.",
            "sentiment": "bullish",
            "impact_level": "high"
        },
        {
            "title": "OPEC+ Maintains Oil Production Targets",
            "source": "Bloomberg",
            "summary": "OPEC+ decides to maintain current production levels amid market uncertainty.",
            "sentiment": "neutral",
            "impact_level": "medium"
        },
        {
            "title": "Tanker Route Disruptions in Strait of Hormuz",
            "source": "FT",
            "summary": "Multiple shipping companies report delays in transiting the Strait.",
            "sentiment": "bullish",
            "impact_level": "high"
        },
        {
            "title": "Oil Prices Recover on Supply Concerns",
            "source": "CNBC",
            "summary": "Brent crude rebounds above $85 on geopolitical tensions.",
            "sentiment": "bullish",
            "impact_level": "medium"
        },
        {
            "title": "Peace Talks Resume Between Regional Powers",
            "source": "BBC",
            "summary": "Diplomatic efforts intensify to reduce tensions in the Middle East.",
            "sentiment": "bearish",
            "impact_level": "medium"
        }
    ]

    for days_ago in range(30, 0, -1):
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        # Agregar 1-3 noticias por día
        num_news = random.randint(1, 3)
        for _ in range(num_news):
            news = random.choice(news_samples)
            news_data = {
                'date': date,
                'time': f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
                'title': news['title'],
                'source': news['source'],
                'url': f"https://example.com/news/{random.randint(1, 10000)}",
                'summary': news['summary'],
                'full_content': news['summary'],
                'sentiment': news['sentiment'],
                'impact_level': news['impact_level'],
                'impact_direction': '↑' if news['sentiment'] == 'bullish' else '↓' if news['sentiment'] == 'bearish' else '→',
                'keywords': ['oil', 'Iran', 'Ormuz']
            }
            db.insert_news_event(news_data)

    print("✅ Noticias generadas (30 días)")

def generate_sample_risk_scores():
    """Generar scores de riesgo de ejemplo"""
    db = DashboardDB()

    print("Generando scores de riesgo...")

    for days_ago in range(90, 0, -1):
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        # Score base que varía con tendencia
        trend = (90 - days_ago) / 90  # Varía de 0 a 1
        base_score = 40 + trend * 20 + random.uniform(-10, 10)
        base_score = max(10, min(95, base_score))

        scores = {
            'overall_score': round(base_score, 1),
            'oil_price_signal': round(30 + random.uniform(0, 40), 1),
            'oil_volatility_signal': round(20 + random.uniform(0, 40), 1),
            'polymarket_escalation': round(35 + trend * 30 + random.uniform(-5, 5), 1),
            'polymarket_supply': round(50 + random.uniform(-15, 15), 1),
            'news_sentiment_signal': round(45 + random.uniform(-20, 20), 1),
            'geopolitical_severity': round(20 + trend * 50 + random.uniform(-10, 10), 1),
            'risk_level': 'critical' if base_score > 75 else 'high' if base_score > 50 else 'medium' if base_score > 30 else 'low',
            'score_change_1d': round(random.uniform(-10, 10), 1),
            'score_change_7d': round(random.uniform(-20, 20), 1),
            'primary_driver': random.choice(['oil_price_signal', 'polymarket_escalation', 'polymarket_supply']),
            'secondary_drivers': ['oil_volatility_signal', 'news_sentiment_signal'],
            'commentary': 'Riesgo moderado con tendencia alcista' if base_score > 50 else 'Riesgo controlado'
        }

        db.insert_risk_score(date, scores)

    print("✅ Scores de riesgo generados (90 días)")

def main():
    print("=" * 60)
    print("INICIALIZADOR DE BASE DE DATOS - DASHBOARD GEOPOLÍTICO")
    print("=" * 60)
    print()

    try:
        # Generar todos los datos de ejemplo
        generate_sample_oil_data()
        generate_sample_polymarket_data()
        generate_sample_news()
        generate_sample_risk_scores()

        print()
        print("=" * 60)
        print("✅ BASE DE DATOS INICIALIZADA EXITOSAMENTE")
        print("=" * 60)
        print()
        print("Pasos siguientes:")
        print("1. Configurar NEWSAPI_KEY en .env o GitHub Secrets")
        print("2. Ejecutar: streamlit run app.py")
        print("3. Abrir navegador en http://localhost:8501")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
