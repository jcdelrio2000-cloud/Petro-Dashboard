"""
fetch_news.py
Descarga noticias relevantes sobre petróleo y geopolítica del Medio Oriente
"""

import requests
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import logging
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self, newsapi_key=None):
        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_KEY')
        self.db = DashboardDB()
        self.timeout = 30

        # Palabras clave principales
        self.keywords = [
            "Strait of Hormuz",
            "Iran oil",
            "oil supply disruption",
            "tanker attack",
            "OPEC",
            "Middle East escalation",
            "shipping disruption",
            "crude oil",
            "sanctions Iran",
            "petróleo"
        ]

        # Fuentes confiables
        self.trusted_sources = [
            "reuters.com",
            "bloomberg.com",
            "ft.com",
            "bbc.com",
            "cnbc.com",
            "aljazeera.com",
            "oilprice.com"
        ]

    def fetch_from_newsapi(self):
        """
        Descargar noticias desde NewsAPI (requiere API key gratuita)
        """
        if not self.newsapi_key:
            logger.warning("NEWSAPI_KEY no configurada, saltando NewsAPI")
            return []

        try:
            logger.info("Descargando noticias desde NewsAPI...")

            all_articles = []

            # Buscar por cada palabra clave
            for keyword in self.keywords[:5]:  # Limitar para no exceder límite de requests
                try:
                    url = "https://newsapi.org/v2/everything"
                    params = {
                        'q': keyword,
                        'sortBy': 'publishedAt',
                        'language': 'en',
                        'pageSize': 20,
                        'apiKey': self.newsapi_key,
                        'from': (datetime.now() - timedelta(days=1)).isoformat()
                    }

                    response = requests.get(url, params=params, timeout=self.timeout)
                    response.raise_for_status()

                    data = response.json()

                    if data.get('articles'):
                        all_articles.extend(data['articles'])
                        logger.info(f"Encontradas {len(data['articles'])} artículos para '{keyword}'")

                except requests.RequestException as e:
                    logger.error(f"Error descargando para '{keyword}': {e}")

            return all_articles

        except Exception as e:
            logger.error(f"Error en NewsAPI: {e}")
            return []

    def classify_sentiment(self, title, summary=""):
        """
        Clasificar sentimiento de una noticia (alcista/bajista/neutral para petróleo)

        Palabras clave alcistas (precio sube):
        - disruption, attack, sanctions, crisis, escalation, shortage
        Palabras clave bajistas (precio baja):
        - peace, agreement, de-escalation, increase production, surplus
        """
        text = (title + " " + summary).lower()

        bullish_keywords = [
            "disruption", "attack", "sanctions", "crisis", "escalation",
            "shortage", "conflict", "strike", "closure", "blockade",
            "missile", "threat", "tension", "war"
        ]

        bearish_keywords = [
            "peace", "agreement", "ceasefire", "de-escalation", "increase production",
            "surplus", "recovery", "opens", "resolution", "deal"
        ]

        bullish_score = sum(1 for kw in bullish_keywords if kw in text)
        bearish_score = sum(1 for kw in bearish_keywords if kw in text)

        if bullish_score > bearish_score:
            return "bullish", "↑"
        elif bearish_score > bullish_score:
            return "bearish", "↓"
        else:
            return "neutral", "→"

    def classify_impact_level(self, title, summary=""):
        """
        Clasificar nivel de impacto: bajo, medio, alto

        Alto: Ataques, cierres, conflictosescalada
        Medio: Cambios de política, investigaciones, alertas
        Bajo: Análisis, comentarios, datos históricos
        """
        text = (title + " " + summary).lower()

        high_impact_keywords = [
            "attack", "strike", "military", "closure", "blockade",
            "escalation", "war", "conflict", "missile", "armed",
            "disruption confirmed", "emergency"
        ]

        medium_impact_keywords = [
            "investigation", "warning", "alert", "risk", "concerns",
            "threatens", "policy", "sanction", "resolution", "talks"
        ]

        high_score = sum(1 for kw in high_impact_keywords if kw in text)
        medium_score = sum(1 for kw in medium_impact_keywords if kw in text)

        if high_score >= 1:
            return "high"
        elif medium_score >= 1:
            return "medium"
        else:
            return "low"

    def is_duplicate(self, title, existing_articles):
        """
        Detectar si el artículo es duplicado o muy similar

        Usa ratio de similitud de secuencias
        """
        for existing in existing_articles:
            # Comparar títulos
            ratio = SequenceMatcher(None, title.lower(), existing['title'].lower()).ratio()
            if ratio > 0.85:  # >85% similar
                return True
        return False

    def process_articles(self, articles):
        """
        Procesar y deduplicar artículos
        """
        logger.info(f"Procesando {len(articles)} artículos brutos...")

        processed = []
        existing_urls = set()

        for article in articles:
            try:
                url = article.get('url', '')
                title = article.get('title', '')

                # Evitar duplicados por URL
                if url in existing_urls:
                    continue
                existing_urls.add(url)

                # Evitar duplicados por similitud de título
                if self.is_duplicate(title, processed):
                    logger.debug(f"Duplicado detectado: {title[:50]}")
                    continue

                # Procesar
                published = article.get('publishedAt', '')
                if published:
                    # Convertir ISO a datetime
                    dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M")
                else:
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    time_str = datetime.now().strftime("%H:%M")

                sentiment, direction = self.classify_sentiment(
                    title,
                    article.get('description', '')
                )

                impact = self.classify_impact_level(
                    title,
                    article.get('description', '')
                )

                news_item = {
                    'date': date_str,
                    'time': time_str,
                    'title': title,
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': url,
                    'summary': article.get('description', '')[:200],
                    'full_content': article.get('content', ''),
                    'sentiment': sentiment,
                    'impact_level': impact,
                    'impact_direction': direction,
                    'keywords': self.keywords
                }

                processed.append(news_item)

            except Exception as e:
                logger.error(f"Error procesando artículo: {e}")

        logger.info(f"Procesados {len(processed)} artículos únicos")
        return processed

    def fetch_news(self):
        """
        Ejecutar proceso completo de descarga de noticias
        """
        try:
            logger.info("Iniciando descarga de noticias...")

            # Descargar desde NewsAPI
            articles = self.fetch_from_newsapi()

            if not articles:
                logger.warning("No se obtuvieron artículos")
                return None

            # Procesar y deduplicar
            processed = self.process_articles(articles)

            if not processed:
                logger.warning("No se procesaron artículos")
                return None

            return {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'fetch_time': datetime.now().isoformat(),
                'articles': processed,
                'count': len(processed)
            }

        except Exception as e:
            logger.error(f"Error descargando noticias: {e}")
            return None

    def save_to_database(self, data):
        """Guardar noticias en la base de datos"""
        if not data:
            logger.error("No hay noticias para guardar")
            return False

        try:
            saved_count = 0
            for article in data['articles']:
                try:
                    self.db.insert_news_event(article)
                    saved_count += 1
                except Exception as e:
                    logger.warning(f"Error guardando artículo: {e}")

            logger.info(f"Guardadas {saved_count}/{len(data['articles'])} noticias")
            return saved_count > 0

        except Exception as e:
            logger.error(f"Error guardando noticias: {e}")
            return False

    def run(self):
        """Ejecutar proceso completo"""
        data = self.fetch_news()
        if data:
            return self.save_to_database(data)
        return False

if __name__ == "__main__":
    fetcher = NewsFetcher()
    success = fetcher.run()
    sys.exit(0 if success else 1)
