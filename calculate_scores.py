"""
calculate_scores.py
Calcula score sintético de riesgo geopolítico combinando múltiples señales
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from database import DashboardDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskScoreCalculator:
    def __init__(self):
        self.db = DashboardDB()

        # Pesos de componentes (debe sumar 1.0)
        self.weights = {
            'oil_price_signal': 0.20,
            'oil_volatility_signal': 0.15,
            'polymarket_escalation': 0.30,
            'polymarket_supply': 0.20,
            'news_sentiment_signal': 0.10,
            'geopolitical_severity': 0.05
        }

        # Umbrales para niveles de riesgo
        self.level_thresholds = {
            'low': (0, 30),
            'medium': (30, 50),
            'high': (50, 75),
            'critical': (75, 100)
        }

        # Precios de referencia históricos (en USD)
        self.oil_price_thresholds = {
            'baseline': 75,      # Precio "normal"
            'elevated': 85,      # Precio elevado (riesgo moderado)
            'high': 95,          # Precio alto (riesgo considerable)
            'critical': 110      # Precio crítico
        }

    def calculate_oil_price_signal(self):
        """
        Calcular señal de riesgo basada en precio del Brent

        Lógica:
        - Precio > $110: 90 puntos (crítico)
        - Precio $95-110: 70 puntos (alto)
        - Precio $85-95: 50 puntos (medio)
        - Precio <$85: 30 puntos (bajo)

        Retorna: valor 0-100
        """
        try:
            latest = self.db.get_latest_oil_prices()
            if not latest or not latest.get('brent_price'):
                logger.warning("No hay datos de petróleo")
                return 50  # Default neutral

            price = latest['brent_price']

            if price >= self.oil_price_thresholds['critical']:
                signal = 90
            elif price >= self.oil_price_thresholds['high']:
                signal = 70
            elif price >= self.oil_price_thresholds['elevated']:
                signal = 50
            else:
                signal = 30

            logger.info(f"Oil price signal: {signal} (Brent=${price})")
            return signal

        except Exception as e:
            logger.error(f"Error en oil_price_signal: {e}")
            return 50

    def calculate_volatility_signal(self):
        """
        Calcular señal basada en volatilidad del petróleo

        Lógica:
        - Vol > 40%: 80 puntos (muy alta, pánico)
        - Vol 30-40%: 60 puntos (alta)
        - Vol 20-30%: 40 puntos (media)
        - Vol < 20%: 20 puntos (baja)

        Retorna: valor 0-100
        """
        try:
            latest = self.db.get_latest_oil_prices()
            if not latest or not latest.get('brent_volatility_30d'):
                return 30  # Volatilidad baja por defecto

            vol = latest['brent_volatility_30d']

            if vol >= 40:
                signal = 80
            elif vol >= 30:
                signal = 60
            elif vol >= 20:
                signal = 40
            else:
                signal = 20

            logger.info(f"Volatility signal: {signal} (Vol={vol:.1f}%)")
            return signal

        except Exception as e:
            logger.error(f"Error en volatility_signal: {e}")
            return 30

    def calculate_polymarket_signals(self):
        """
        Calcular señales de riesgo desde Polymarket

        Retorna tupla:
        - escalation_signal: 0-100 (probabilidad de escalada)
        - supply_signal: 0-100 (probabilidad de disrupciones de suministro)
        """
        try:
            markets = self.db.get_latest_polymarket_signals()

            if not markets:
                logger.warning("No hay datos de Polymarket")
                return 50, 50

            escalation_signal = 50
            supply_signal = 50

            for market in markets:
                category = market.get('category', '')
                prob = market.get('probability', 50)

                if category == 'escalation':
                    # Promedio ponderado de mercados de escalada
                    escalation_signal = prob
                elif category == 'supply':
                    supply_signal = prob

            logger.info(f"Polymarket escalation: {escalation_signal:.1f}%, supply: {supply_signal:.1f}%")
            return escalation_signal, supply_signal

        except Exception as e:
            logger.error(f"Error en polymarket_signals: {e}")
            return 50, 50

    def calculate_news_sentiment_signal(self):
        """
        Calcular sentimiento agregado de noticias de hoy

        Lógica:
        - Si hay noticias alcistas (bull) recientes: aumentar señal
        - Si hay noticias bajistas (bear): reducir señal
        - Nivel de impacto afecta el peso

        Retorna: valor 0-100
        """
        try:
            today_news = self.db.get_today_news()

            if not today_news:
                return 50  # Neutral si sin noticias

            bullish_count = 0
            bearish_count = 0
            high_impact_weight = 3

            for news in today_news:
                impact = news.get('impact_level', 'medium')
                direction = news.get('impact_direction', '→')

                weight = 1
                if impact == 'high':
                    weight = high_impact_weight
                elif impact == 'medium':
                    weight = 2

                if direction == '↑':
                    bullish_count += weight
                elif direction == '↓':
                    bearish_count += weight

            # Convertir a escala 0-100
            total = bullish_count + bearish_count
            if total == 0:
                signal = 50
            else:
                # Más noticias alcistas = mayor signal
                signal = 30 + (bullish_count / total) * 40

            logger.info(f"News sentiment: {signal:.1f} (bull:{bullish_count}, bear:{bearish_count})")
            return signal

        except Exception as e:
            logger.error(f"Error en news_sentiment_signal: {e}")
            return 50

    def calculate_geopolitical_severity(self):
        """
        Calcular severidad de eventos geopolíticos recientes

        Se podría conectar a un índice externo o análisis manual
        Por ahora, basarse en noticias de alto impacto

        Retorna: valor 0-100
        """
        try:
            recent_news = self.db.get_news_history(days=7)

            high_impact_count = sum(1 for n in recent_news if n.get('impact_level') == 'high')

            if high_impact_count >= 3:
                severity = 75
            elif high_impact_count == 2:
                severity = 50
            elif high_impact_count == 1:
                severity = 30
            else:
                severity = 10

            logger.info(f"Geopolitical severity: {severity} (high impact events: {high_impact_count})")
            return severity

        except Exception as e:
            logger.error(f"Error en geopolitical_severity: {e}")
            return 20

    def calculate_overall_score(self, components):
        """
        Calcular score general como promedio ponderado
        """
        score = (
            components['oil_price_signal'] * self.weights['oil_price_signal'] +
            components['oil_volatility_signal'] * self.weights['oil_volatility_signal'] +
            components['polymarket_escalation'] * self.weights['polymarket_escalation'] +
            components['polymarket_supply'] * self.weights['polymarket_supply'] +
            components['news_sentiment_signal'] * self.weights['news_sentiment_signal'] +
            components['geopolitical_severity'] * self.weights['geopolitical_severity']
        )

        return round(min(100, max(0, score)), 2)

    def get_risk_level(self, score):
        """Obtener nivel de riesgo basado en score"""
        for level, (min_val, max_val) in self.level_thresholds.items():
            if min_val <= score < max_val:
                return level
        return 'critical'

    def calculate_change_vs_previous(self, new_score):
        """Calcular cambios vs día anterior y 7 días"""
        try:
            history = self.db.get_risk_scores_history(days=7)

            change_1d = None
            change_7d = None

            if len(history) >= 2:
                prev_score = history[0].get('overall_score')  # Ayer es el segundo más reciente
                if prev_score:
                    change_1d = new_score - prev_score

            if len(history) >= 2:
                oldest_score = history[-1].get('overall_score')  # Más antiguo
                if oldest_score:
                    change_7d = new_score - oldest_score

            return (
                round(change_1d, 2) if change_1d else 0,
                round(change_7d, 2) if change_7d else 0
            )

        except Exception as e:
            logger.error(f"Error calculando cambios: {e}")
            return 0, 0

    def determine_primary_driver(self, components):
        """Determinar qué componente está impulsando el riesgo"""
        drivers = {
            'oil_price_signal': components['oil_price_signal'],
            'polymarket_escalation': components['polymarket_escalation'],
            'polymarket_supply': components['polymarket_supply'],
            'news_sentiment_signal': components['news_sentiment_signal']
        }

        return max(drivers, key=drivers.get)

    def generate_commentary(self, score, components, change_1d):
        """Generar comentario ejecutivo automático sobre el riesgo"""
        level = self.get_risk_level(score)

        if score >= 75:
            if change_1d > 0:
                return "⚠️ Riesgo geopolítico CRÍTICO con tendencia alcista. Monitorear escalada Irán."
            else:
                return "🔴 Riesgo geopolítico CRÍTICO. Requiere atención inmediata."
        elif score >= 50:
            if change_1d > 5:
                return "⚠️ Riesgo ALTO con aceleración. Señales de Polymarket y noticias alertantes."
            else:
                return "🟠 Riesgo ALTO pero estable. Vigilancia de Ormuz necesaria."
        elif score >= 30:
            if change_1d < -5:
                return "📉 Riesgo MEDIO en tendencia bajista. Señales de desescalada."
            else:
                return "🟡 Riesgo MEDIO. Monitoreo continuo de factores geopolíticos."
        else:
            return "🟢 Riesgo BAJO. Condiciones relativamente normales en Medio Oriente."

    def run(self):
        """
        Ejecutar cálculo completo de score y guardar en BD
        """
        try:
            logger.info("Iniciando cálculo de score de riesgo...")

            # Calcular componentes
            components = {
                'oil_price_signal': self.calculate_oil_price_signal(),
                'oil_volatility_signal': self.calculate_volatility_signal(),
                'news_sentiment_signal': self.calculate_news_sentiment_signal(),
                'geopolitical_severity': self.calculate_geopolitical_severity()
            }

            esc, sup = self.calculate_polymarket_signals()
            components['polymarket_escalation'] = esc
            components['polymarket_supply'] = sup

            # Score general
            overall_score = self.calculate_overall_score(components)

            # Cambios
            change_1d, change_7d = self.calculate_change_vs_previous(overall_score)

            # Nivel y drivers
            risk_level = self.get_risk_level(overall_score)
            primary_driver = self.determine_primary_driver(components)
            commentary = self.generate_commentary(overall_score, components, change_1d)

            # Guardar
            today = datetime.now().strftime("%Y-%m-%d")

            score_data = {
                'overall_score': overall_score,
                'oil_price_signal': components['oil_price_signal'],
                'oil_volatility_signal': components['oil_volatility_signal'],
                'polymarket_escalation': components['polymarket_escalation'],
                'polymarket_supply': components['polymarket_supply'],
                'news_sentiment_signal': components['news_sentiment_signal'],
                'geopolitical_severity': components['geopolitical_severity'],
                'risk_level': risk_level,
                'score_change_1d': change_1d,
                'score_change_7d': change_7d,
                'primary_driver': primary_driver,
                'secondary_drivers': [k for k, v in sorted(components.items(),
                                                           key=lambda x: -x[1])[:2]],
                'commentary': commentary
            }

            self.db.insert_risk_score(today, score_data)

            logger.info(f"Score calculado: {overall_score} ({risk_level})")
            logger.info(f"Comentario: {commentary}")

            return True

        except Exception as e:
            logger.error(f"Error calculando score: {e}")
            return False

if __name__ == "__main__":
    calculator = RiskScoreCalculator()
    success = calculator.run()
    sys.exit(0 if success else 1)
