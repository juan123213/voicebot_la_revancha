from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import torch
from typing import Dict
from datetime import datetime

class SentimentAnalyzer:
    def __init__(self):
        """Inicializa el analizador de sentimientos usando BERT multilingüe"""
        try:
            self.model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.sentiment_pipeline = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
            self.history = []
            
            # Keywords mejorados con más patrones
            self.keywords = {
                'identificacion': [
                    'mi nombre', 'me llamo', 'dni', 'documento', 'soy', 
                    'mi número', 'mi dni es', 'me identifico'
                ],
                'informativo': [
                    'necesito ayuda', 'tengo una deuda', 'quisiera saber', 
                    'información', 'consulta', 'pregunta', 'deuda'
                ],
                'positivo': [
                    'acepto', 'si acepto', 'de acuerdo', 'me parece bien', 
                    'está bien', 'adelante', 'perfecto', 'excelente', 'gracias',
                    'quiero pagar', 'pagaré', 'haré el pago', 'me interesa',
                    'buena opción', 'me conviene', 'me ayuda'
                ],
                'negativo': [
                    'no puedo', 'no quiero', 'muy alto', 'demasiado', 'imposible',
                    'caro', 'excesivo', 'complicado', 'difícil', 'no me alcanza',
                    'no pagaré', 'no voy a pagar', 'no pago', 'no pagaría',
                    'no estoy de acuerdo', 'no me interesa', 'no acepto',
                    'mucho dinero', 'es injusto', 'no me sirve'
                ],
                'duda': [
                    'opciones', 'alternativas', 'otras opciones', 'tal vez',
                    'quizás', 'puede ser', '¿qué más', '¿qué otro', 'depende',
                    'tendría que ver', 'no estoy seguro', 'necesito pensarlo'
                ]
            }
            
            # Patrones de negación específicos
            self.negation_patterns = [
                'no', 'ni', 'nunca', 'jamás', 'tampoco', 'no quiero', 
                'no puedo', 'no voy', 'no me', 'sin', 'nada', 'ningún',
                'ninguna', 'no hay', 'no tengo'
            ]
            
            print("Modelo BERT cargado correctamente")
        except Exception as e:
            print(f"Error al cargar el modelo BERT: {e}")
            raise

    def analyze(self, text: str) -> Dict:
        """Analiza el sentimiento del texto combinando análisis contextual"""
        try:
            text_lower = text.lower()
            
            # Detectar contexto primero
            context_type = self._detect_context_type(text_lower)
            
            # Verificar negaciones específicas de pago
            if any(neg in text_lower for neg in ['no quiero pagar', 'no pagaré', 'no voy a pagar']):
                return {
                    'sentiment': 'MUY_NEGATIVO',
                    'score': 0.1,
                    'timestamp': datetime.now().isoformat(),
                    'text': text,
                    'context_type': 'negativo',
                    'keywords_detected': {'negativo': ['no pagar']}
                }
            
            # Asignar score basado en contexto
            if context_type == 'identificacion':
                score = 0.6  # Ligeramente positivo
                sentiment = 'NEUTRAL'
            elif context_type == 'informativo':
                score = 0.5  # Neutral
                sentiment = 'NEUTRAL'
            else:
                score = self._analyze_context(text_lower)
                sentiment = self._determine_sentiment(text_lower, score)
            
            analysis = {
                'sentiment': sentiment,
                'score': score,
                'timestamp': datetime.now().isoformat(),
                'text': text,
                'context_type': context_type,
                'keywords_detected': self._get_detected_keywords(text_lower)
            }
            
            self.history.append(analysis)
            return analysis
            
        except Exception as e:
            print(f"Error en el análisis de sentimientos: {e}")
            return {
                'sentiment': 'NEUTRAL',
                'score': 0.5,
                'timestamp': datetime.now().isoformat(),
                'text': text,
                'error': str(e)
            }

    def _detect_context_type(self, text: str) -> str:
        """Detecta el tipo de contexto del mensaje"""
        # Verificar negaciones de pago primero
        if any(phrase in text for phrase in ['no quiero pagar', 'no pagaré', 'no voy a pagar']):
            return 'negativo'
            
        if any(phrase in text for phrase in self.keywords['identificacion']):
            return 'identificacion'
        elif any(phrase in text for phrase in self.keywords['informativo']):
            return 'informativo'
        elif any(phrase in text for phrase in self.keywords['positivo']):
            return 'positivo'
        elif any(phrase in text for phrase in self.keywords['negativo']):
            return 'negativo'
        elif any(phrase in text for phrase in self.keywords['duda']):
            return 'duda'
        return 'general'

    def _analyze_context(self, text: str) -> float:
        """Analiza el contexto y retorna un score entre 0 y 1"""
        score = 0.5  # Punto de partida neutral
        
        # Verificar negaciones explícitas primero
        if any(pattern in text for pattern in self.negation_patterns):
            if any(word in text for word in ['pagar', 'aceptar', 'acuerdo', 'interesa']):
                return 0.1  # Muy negativo para negaciones de pago/aceptación
        
        # Detectar palabras clave
        positive_matches = sum(1 for phrase in self.keywords['positivo'] if phrase in text)
        negative_matches = sum(1 for phrase in self.keywords['negativo'] if phrase in text)
        doubt_matches = sum(1 for phrase in self.keywords['duda'] if phrase in text)
        
        # Casos especiales
        if 'no puedo' in text or 'muy alto' in text or 'demasiado' in text:
            return 0.2  # Negativo por dificultad/costo
        elif 'acepto' in text or 'pagaré' in text:
            return 0.9  # Muy positivo por aceptación
        
        # Ajustes por coincidencias
        if positive_matches > 0:
            score += 0.15 * positive_matches
        if negative_matches > 0:
            score -= 0.25 * negative_matches  # Mayor peso a lo negativo
        if doubt_matches > 0:
            score = min(score, 0.6)  # Las dudas limitan el máximo
        
        return max(0.0, min(1.0, score))

    def _determine_sentiment(self, text: str, score: float) -> str:
        """Determina el sentimiento final"""
        # Casos especiales primero
        if any(neg in text for neg in ['no quiero pagar', 'no pagaré', 'no voy a pagar']):
            return 'MUY_NEGATIVO'
            
        if any(pattern in text for pattern in self.negation_patterns):
            if any(word in text for word in ['pagar', 'aceptar', 'acuerdo', 'interesa']):
                return 'MUY_NEGATIVO'
        
        if 'acepto' in text or 'pagaré' in text:
            return 'MUY_POSITIVO'
            
        if any(phrase in text for phrase in self.keywords['duda']):
            return 'DUDA'
        
        # Basado en score
        if score >= 0.8:
            return 'MUY_POSITIVO'
        elif score >= 0.6:
            return 'POSITIVO'
        elif score <= 0.2:
            return 'MUY_NEGATIVO'
        elif score <= 0.4:
            return 'NEGATIVO'
        return 'NEUTRAL'

    def _get_detected_keywords(self, text: str) -> Dict[str, list]:
        """Detecta palabras clave presentes en el texto"""
        detected = {}
        for category, phrases in self.keywords.items():
            found = [phrase for phrase in phrases if phrase in text]
            if found:
                detected[category] = found
                
        # Detectar negaciones específicas
        if any(pattern in text for pattern in self.negation_patterns):
            if 'negativo' not in detected:
                detected['negativo'] = []
            detected['negativo'].extend([pat for pat in self.negation_patterns if pat in text])
            
        return detected

    def get_conversation_metrics(self) -> Dict:
        """Genera métricas de la conversación completa"""
        if not self.history:
            return {}
            
        total_interactions = len(self.history)
        sentiment_counts = {}
        sentiment_scores = []
        keywords_frequency = {category: 0 for category in self.keywords.keys()}
        
        for analysis in self.history:
            sentiment = analysis['sentiment']
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            sentiment_scores.append(analysis['score'])
            
            if 'keywords_detected' in analysis:
                for category in analysis['keywords_detected']:
                    keywords_frequency[category] += 1
        
        trend = self._calculate_trend(sentiment_scores)
        
        return {
            'total_interactions': total_interactions,
            'sentiment_distribution': sentiment_counts,
            'average_sentiment_score': sum(sentiment_scores) / len(sentiment_scores),
            'sentiment_trend': trend,
            'keywords_frequency': keywords_frequency,
            'timeline': self.history,
            'negotiation_success_probability': self._calculate_success_probability(sentiment_scores)
        }

    def _calculate_trend(self, scores: list) -> str:
        """Calcula la tendencia de la conversación"""
        if len(scores) < 2:
            return 'ESTABLE'
            
        mid = len(scores) // 2
        first_half = sum(scores[:mid]) / mid if mid > 0 else scores[0]
        second_half = sum(scores[mid:]) / (len(scores) - mid)
        
        diff = second_half - first_half
        if diff > 0.1:
            return 'MEJORANDO'
        elif diff < -0.1:
            return 'EMPEORANDO'
        return 'ESTABLE'

    def _calculate_success_probability(self, scores: list) -> float:
        """Calcula probabilidad de éxito en la negociación"""
        if not scores:
            return 0.0
        
        recent_weight = 1.5
        final_score = scores[-1] * recent_weight
        avg_score = sum(scores) / len(scores)
        
        probability = (final_score + avg_score) / (recent_weight + 1)
        
        # Ajuste para últimos mensajes muy positivos
        if final_score > 0.8:
            probability *= 1.2
        elif final_score < 0.3:  # Ajuste para últimos mensajes muy negativos
            probability *= 0.5
        
        return min(1.0, max(0.0, probability))