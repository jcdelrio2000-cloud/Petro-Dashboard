"""
fetch_polymarket.py
Descarga probabilidades implícitas desde Polymarket API
"""

import requests
import json
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolymarketFetcher:
    def __init__(self, api_url="https://api.polymarket.com"):
        self.api_url = api_url
        self.db = DashboardDB()
        self.timeout = 30

        # Mercados de interés - estos son ejemplos
        # En producción, obtener los IDs correctos desde la API
        self.markets = [
            {
                "id": "0x123456789abcdef_iran_escalation",
                "name": "Will Iran launch military strikes against Israel by June 30, 2026?",
                "category": "escalation",
                "weight": 0.25,
                "search_term": "Iran attack Israel 2026"
            },
            {
                "id": "0x987654321fedcba_supply",
                "name": "Will oil supply disruption occur in Middle East by June 30, 2026?",
                "category": "supply",
                "weight": 0.25,
                "search_term": "oil supply disruption Middle East"
            },
            {
                "id": "0xabcdef1234567890_hormuz",
                "name": "Will Strait of Hormuz shipping return to normal by April 30, 2026?",
                "category": "logistics",
                "weight": 0.25,
                "search_term": "Strait Hormuz shipping"
            },
            {
                "id": "0xfedcba0987654321_wti_price",
                "name": "Will WTI crude oil exceed $85/barrel in April 2026?",
                "category": "price",
                "weight": 0.25,
                "search_term": "WTI crude oil price April"
            }
        ]

    def search_markets(self):
        """
        Buscar mercados en Polymarket que coincidan con nuestros criterios
        """
        try:
            logger.info("Buscando mercados en Polymarket...")

            markets_found = []

            for market_spec in self.markets:
                try:
                    # Endpoint de búsqueda de Polymarket
                    url = f"{self.api_url}/markets"
                    params = {
                        "search": market_spec["search_term"],
                        "sort": "liquidity",
                        "order": "desc",
                        "limit": 1
                    }

                    response = requests.get(url, params=params, timeout=self.timeout)
                    response.raise_for_status()

                    results = response.json()

                    if results and len(results) > 0:
                        market = results[0]
                        markets_found.append({
                            "id": market.get("id", market_spec["id"]),
                            "name": market.get("title", market_spec["name"]),
                            "category": market_spec["category"],
                            "weight": market_spec["weight"],
                            "price": float(market.get("price", 0.5)),
                            "probability": float(market.get("price", 0.5)) * 100,
                            "liquidity": float(market.get("liquidity", 0)),
                            "volume_24h": float(market.get("volume24h", 0)),
                            "yes_shares_in_pool": float(market.get("yes_token_count", 0)),
                            "no_shares_in_pool": float(market.get("no_token_count", 0)),
                            "outcome": market.get("outcome", "YES/NO")
                        })
                    else:
                        logger.warning(f"No se encontró mercado para: {market_spec['search_term']}")
                        # Usar datos por defecto para continuidad
                        markets_found.append({
                            "id": market_spec["id"],
                            "name": market_spec["name"],
                            "category": market_spec["category"],
                            "weight": market_spec["weight"],
                            "price": 0.5,
                            "probability": 50.0,
                            "liquidity": 0,
                            "volume_24h": 0,
                            "yes_shares_in_pool": 0,
                            "no_shares_in_pool": 0,
                            "outcome": "YES/NO"
                        })

                except requests.RequestException as e:
                    logger.error(f"Error buscando mercado {market_spec['search_term']}: {e}")
                    # Continuar con otros mercados

            return markets_found

        except Exception as e:
            logger.error(f"Error en búsqueda de mercados: {e}")
            return None

    def get_market_history(self, market_id):
        """
        Obtener histórico de precios para un mercado (si la API lo proporciona)
        """
        try:
            url = f"{self.api_url}/markets/{market_id}/history"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"No se pudo obtener histórico para {market_id}: {e}")
            return None

    def calculate_changes(self, market_id, current_probability):
        """
        Calcular cambios vs ayer y 7 días

        En producción, usar histórico de la BD
        """
        try:
            history = self.db.get_polymarket_history(market_id, days=7)

            change_1d = None
            change_7d = None

            if len(history) >= 2:
                prev_prob = history[-2].get('probability')
                if prev_prob:
                    change_1d = current_probability - prev_prob

            if len(history) >= 2:
                oldest_prob = history[0].get('probability')
                if oldest_prob:
                    change_7d = current_probability - oldest_prob

            return {
                'change_1d': round(change_1d, 2) if change_1d else 0,
                'change_7d': round(change_7d, 2) if change_7d else 0
            }

        except Exception as e:
            logger.error(f"Error calculando cambios: {e}")
            return {'change_1d': 0, 'change_7d': 0}

    def fetch_polymarket_data(self):
        """
        Descargar y procesar datos de Polymarket
        """
        try:
            logger.info("Iniciando descarga de datos Polymarket...")

            markets = self.search_markets()

            if not markets:
                logger.error("No se pudieron obtener mercados de Polymarket")
                return None

            today = datetime.now().strftime("%Y-%m-%d")

            for market in markets:
                # Calcular cambios
                changes = self.calculate_changes(market['id'], market['probability'])
                market['change_1d'] = changes['change_1d']
                market['change_7d'] = changes['change_7d']

                logger.info(
                    f"{market['name']}: {market['probability']:.1f}% "
                    f"({changes['change_1d']:+.1f}% vs ayer)"
                )

            return {
                'date': today,
                'markets': markets,
                'fetch_time': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error descargando datos Polymarket: {e}")
            return None

    def save_to_database(self, data):
        """Guardar datos en la base de datos"""
        if not data:
            logger.error("No hay datos Polymarket para guardar")
            return False

        try:
            for market in data['markets']:
                self.db.insert_polymarket_signal(
                    date=data['date'],
                    market=market
                )
            logger.info(f"Datos Polymarket guardados para {data['date']} ({len(data['markets'])} mercados)")
            return True
        except Exception as e:
            logger.error(f"Error guardando datos Polymarket: {e}")
            return False

    def run(self):
        """Ejecutar proceso completo"""
        data = self.fetch_polymarket_data()
        if data:
            return self.save_to_database(data)
        return False

if __name__ == "__main__":
    fetcher = PolymarketFetcher()
    success = fetcher.run()
    sys.exit(0 if success else 1)
