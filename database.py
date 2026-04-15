"""
database.py
Inicialización y operaciones con base de datos SQLite para el dashboard
"""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class DashboardDB:
    def __init__(self, db_path: str = "data/dashboard.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Crear tablas si no existen"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabla: Precios de petróleo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oil_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                brent_price REAL,
                brent_change_1d REAL,
                brent_change_7d REAL,
                brent_change_30d REAL,
                wti_price REAL,
                wti_change_1d REAL,
                wti_change_7d REAL,
                wti_change_30d REAL,
                brent_volatility_30d REAL,
                wti_volatility_30d REAL,
                data_source TEXT DEFAULT 'yfinance',
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla: Señales de Polymarket
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS polymarket_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                market_id TEXT NOT NULL,
                market_name TEXT NOT NULL,
                category TEXT,
                probability REAL,
                price REAL,
                change_1d REAL,
                change_7d REAL,
                liquidity REAL,
                volume_24h REAL,
                yes_shares_in_pool REAL,
                no_shares_in_pool REAL,
                data_source TEXT DEFAULT 'polymarket',
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, market_id)
            )
        """)

        # Tabla: Noticias y eventos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT,
                title TEXT NOT NULL,
                source TEXT,
                url TEXT,
                summary TEXT,
                full_content TEXT,
                sentiment TEXT,
                impact_level TEXT,
                impact_direction TEXT,
                keywords TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(url)
            )
        """)

        # Tabla: Scores sintéticos de riesgo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                overall_score REAL,
                oil_price_signal REAL,
                oil_volatility_signal REAL,
                polymarket_escalation REAL,
                polymarket_supply REAL,
                news_sentiment_signal REAL,
                geopolitical_severity REAL,
                risk_level TEXT,
                score_change_1d REAL,
                score_change_7d REAL,
                primary_driver TEXT,
                secondary_drivers TEXT,
                commentary TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabla: Log de alertas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                severity TEXT,
                title TEXT,
                description TEXT,
                value REAL,
                threshold REAL,
                market_name TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        """)

        # Tabla: Metadata del sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logger.info("Base de datos inicializada correctamente")

    # ========================================================================
    # OPERACIONES: OIL PRICES
    # ========================================================================
    def insert_oil_prices(self, date: str, brent: dict, wti: dict):
        """
        Insertar precios de petróleo

        brent = {
            'price': float,
            'change_1d': float,
            'change_7d': float,
            'change_30d': float,
            'volatility_30d': float
        }
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO oil_prices
                (date, brent_price, brent_change_1d, brent_change_7d, brent_change_30d,
                 brent_volatility_30d, wti_price, wti_change_1d, wti_change_7d,
                 wti_change_30d, wti_volatility_30d)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                brent.get('price'),
                brent.get('change_1d'),
                brent.get('change_7d'),
                brent.get('change_30d'),
                brent.get('volatility_30d'),
                wti.get('price'),
                wti.get('change_1d'),
                wti.get('change_7d'),
                wti.get('change_30d'),
                wti.get('volatility_30d')
            ))
            conn.commit()
            logger.info(f"Precios de petróleo insertados para {date}")
        except Exception as e:
            logger.error(f"Error insertando precios: {e}")
        finally:
            conn.close()

    def get_latest_oil_prices(self):
        """Obtener últimos precios de petróleo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM oil_prices
            ORDER BY date DESC LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_oil_prices_history(self, days: int = 365):
        """Obtener histórico de precios"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM oil_prices
            ORDER BY date DESC LIMIT ?
        """, (days,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    # ========================================================================
    # OPERACIONES: POLYMARKET
    # ========================================================================
    def insert_polymarket_signal(self, date: str, market: dict):
        """Insertar señal de Polymarket"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO polymarket_signals
                (date, market_id, market_name, category, probability, price,
                 change_1d, change_7d, liquidity, volume_24h, yes_shares_in_pool,
                 no_shares_in_pool)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                market.get('id'),
                market.get('name'),
                market.get('category'),
                market.get('probability'),
                market.get('price'),
                market.get('change_1d'),
                market.get('change_7d'),
                market.get('liquidity'),
                market.get('volume_24h'),
                market.get('yes_shares_in_pool'),
                market.get('no_shares_in_pool')
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error insertando señal Polymarket: {e}")
        finally:
            conn.close()

    def get_latest_polymarket_signals(self):
        """Obtener últimas señales de Polymarket"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT market_id, market_name, category, probability,
                   price, change_1d, change_7d, liquidity, date
            FROM polymarket_signals
            WHERE date = (SELECT MAX(date) FROM polymarket_signals)
            ORDER BY probability DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_polymarket_history(self, market_id: str, days: int = 90):
        """Obtener histórico de un mercado Polymarket"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM polymarket_signals
            WHERE market_id = ?
            ORDER BY date
            LIMIT ?
        """, (market_id, days))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    # ========================================================================
    # OPERACIONES: NOTICIAS
    # ========================================================================
    def insert_news_event(self, news: dict):
        """Insertar noticia"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO news_events
                (date, time, title, source, url, summary, full_content,
                 sentiment, impact_level, impact_direction, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                news.get('date'),
                news.get('time'),
                news.get('title'),
                news.get('source'),
                news.get('url'),
                news.get('summary'),
                news.get('full_content'),
                news.get('sentiment'),
                news.get('impact_level'),
                news.get('impact_direction'),
                json.dumps(news.get('keywords', []))
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error insertando noticia: {e}")
        finally:
            conn.close()

    def get_today_news(self):
        """Obtener noticias de hoy"""
        today = datetime.now().strftime("%Y-%m-%d")
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM news_events
            WHERE date = ?
            ORDER BY time DESC
        """, (today,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    def get_news_history(self, days: int = 30):
        """Obtener histórico de noticias"""
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM news_events
            WHERE date >= ?
            ORDER BY date DESC, time DESC
        """, (start_date,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    # ========================================================================
    # OPERACIONES: RISK SCORES
    # ========================================================================
    def insert_risk_score(self, date: str, scores: dict):
        """Insertar score de riesgo"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO risk_scores
                (date, overall_score, oil_price_signal, oil_volatility_signal,
                 polymarket_escalation, polymarket_supply, news_sentiment_signal,
                 geopolitical_severity, risk_level, score_change_1d, score_change_7d,
                 primary_driver, secondary_drivers, commentary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                scores.get('overall_score'),
                scores.get('oil_price_signal'),
                scores.get('oil_volatility_signal'),
                scores.get('polymarket_escalation'),
                scores.get('polymarket_supply'),
                scores.get('news_sentiment_signal'),
                scores.get('geopolitical_severity'),
                scores.get('risk_level'),
                scores.get('score_change_1d'),
                scores.get('score_change_7d'),
                scores.get('primary_driver'),
                json.dumps(scores.get('secondary_drivers', [])),
                scores.get('commentary')
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error insertando score de riesgo: {e}")
        finally:
            conn.close()

    def get_latest_risk_score(self):
        """Obtener último score de riesgo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM risk_scores
            ORDER BY date DESC LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_risk_scores_history(self, days: int = 90):
        """Obtener histórico de scores"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM risk_scores
            ORDER BY date DESC LIMIT ?
        """, (days,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    # ========================================================================
    # OPERACIONES: ALERTAS
    # ========================================================================
    def insert_alert(self, alert: dict):
        """Insertar alerta"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO alerts_log
                (alert_type, severity, title, description, value, threshold,
                 market_name, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.get('type'),
                alert.get('severity'),
                alert.get('title'),
                alert.get('description'),
                alert.get('value'),
                alert.get('threshold'),
                alert.get('market_name'),
                1
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error insertando alerta: {e}")
        finally:
            conn.close()

    def get_active_alerts(self):
        """Obtener alertas activas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM alerts_log
            WHERE is_active = 1
            ORDER BY timestamp DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

    # ========================================================================
    # UTILIDADES
    # ========================================================================
    def get_metadata(self, key: str):
        """Obtener valor de metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT value FROM system_metadata WHERE key = ?
        """, (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_metadata(self, key: str, value: str):
        """Establecer valor de metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO system_metadata (key, value, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        conn.commit()
        conn.close()

    def cleanup_old_data(self, retention_days: int = 365):
        """Limpiar datos antiguos"""
        cutoff_date = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%d")
        conn = self.get_connection()
        cursor = conn.cursor()

        tables_to_clean = ['news_events']  # No limpiar series de precios
        for table in tables_to_clean:
            cursor.execute(f"""
                DELETE FROM {table} WHERE date < ?
            """, (cutoff_date,))

        conn.commit()
        conn.close()
        logger.info(f"Datos anteriores a {cutoff_date} limpiados")

if __name__ == "__main__":
    # Test
    db = DashboardDB()
    print("Base de datos lista")
