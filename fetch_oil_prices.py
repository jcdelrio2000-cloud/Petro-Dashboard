"""
fetch_oil_prices.py
Descarga y calcula precios de petróleo desde yfinance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OilPriceFetcher:
    def __init__(self, config_brent="BZ=F", config_wti="CL=F"):
        self.brent_ticker = config_brent
        self.wti_ticker = config_wti
        self.db = DashboardDB()

    def calculate_returns_and_volatility(self, prices_series):
        """
        Calcular cambios porcentuales y volatilidad

        Args:
            prices_series: pd.Series con precios ordenados por fecha

        Returns:
            dict con cambios 1d, 7d, 30d y volatilidad 30d
        """
        if len(prices_series) < 1:
            return {
                'price': None,
                'change_1d': None,
                'change_7d': None,
                'change_30d': None,
                'volatility_30d': None
            }

        current_price = prices_series.iloc[-1]

        # Cambios porcentuales
        change_1d = None
        change_7d = None
        change_30d = None

        if len(prices_series) >= 2:
            change_1d = ((current_price - prices_series.iloc[-2]) / prices_series.iloc[-2] * 100)

        if len(prices_series) >= 6:  # 5 días anteriores + hoy
            change_7d = ((current_price - prices_series.iloc[-6]) / prices_series.iloc[-6] * 100)

        if len(prices_series) >= 21:  # ~30 días
            change_30d = ((current_price - prices_series.iloc[-21]) / prices_series.iloc[-21] * 100)

        # Volatilidad 30 días (desviación estándar de retornos diarios)
        volatility_30d = None
        if len(prices_series) >= 21:
            returns = prices_series.iloc[-21:].pct_change().dropna()
            volatility_30d = returns.std() * 100  # Expresar como porcentaje

        return {
            'price': round(float(current_price), 2),
            'change_1d': round(float(change_1d), 2) if change_1d else None,
            'change_7d': round(float(change_7d), 2) if change_7d else None,
            'change_30d': round(float(change_30d), 2) if change_30d else None,
            'volatility_30d': round(float(volatility_30d), 2) if volatility_30d else None
        }

    def fetch_oil_data(self):
        """
        Descargar datos de petróleo desde yfinance

        Retorna:
            dict con precios y cambios para Brent y WTI
        """
        try:
            logger.info("Descargando datos de petróleo...")

            # Descargar últimos 365 días
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            # Brent
            logger.info(f"Descargando Brent ({self.brent_ticker})...")
            brent_data = yf.download(
                self.brent_ticker,
                start=start_date,
                end=end_date,
                progress=False
            )

            if brent_data.empty:
                logger.error("No se pudo descargar datos de Brent")
                return None

            # WTI
            logger.info(f"Descargando WTI ({self.wti_ticker})...")
            wti_data = yf.download(
                self.wti_ticker,
                start=start_date,
                end=end_date,
                progress=False
            )

            if wti_data.empty:
                logger.error("No se pudo descargar datos de WTI")
                return None

            # Usar 'Close' como precio
            brent_prices = brent_data['Close']
            wti_prices = wti_data['Close']

            # Calcular métricas
            brent_metrics = self.calculate_returns_and_volatility(brent_prices)
            wti_metrics = self.calculate_returns_and_volatility(wti_prices)

            today = datetime.now().strftime("%Y-%m-%d")

            result = {
                'date': today,
                'brent': brent_metrics,
                'wti': wti_metrics,
                'brent_history': brent_data,
                'wti_history': wti_data,
                'fetch_time': datetime.now().isoformat()
            }

            logger.info(f"Brent: ${brent_metrics['price']} ({brent_metrics['change_1d']:+.2f}% 1d)")
            logger.info(f"WTI: ${wti_metrics['price']} ({wti_metrics['change_1d']:+.2f}% 1d)")

            return result

        except Exception as e:
            logger.error(f"Error descargando datos de petróleo: {e}")
            return None

    def save_to_database(self, data):
        """Guardar datos en la base de datos"""
        if not data:
            logger.error("No hay datos para guardar")
            return False

        try:
            self.db.insert_oil_prices(
                date=data['date'],
                brent=data['brent'],
                wti=data['wti']
            )
            logger.info(f"Datos guardados en base de datos para {data['date']}")
            return True
        except Exception as e:
            logger.error(f"Error guardando datos: {e}")
            return False

    def run(self):
        """Ejecutar proceso completo de descarga y almacenamiento"""
        data = self.fetch_oil_data()
        if data:
            return self.save_to_database(data)
        return False

if __name__ == "__main__":
    fetcher = OilPriceFetcher()
    success = fetcher.run()
    sys.exit(0 if success else 1)
