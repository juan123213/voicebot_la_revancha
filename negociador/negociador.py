import google.generativeai as genai
import logging
import re
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, Optional
from funciones.sentiment_analysis import SentimentAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEBTORS_DB = pd.DataFrame({
    'nombre': ['Miguel'],
    'dni': ['1234'],
    'deuda': [5000.00],
    'estado': ['activo']
})

class DebtNegotiator:
    def __init__(self):
        self.api_keys = [
            "AIzaSyBG0LMFQgXmkxlIbx-kvmrFzBgZFMbyR-g",
            "AIzaSyBhnvqxLjhzfbUp3MnFjwEMsNJ4VYY7r3A",
            "AIzaSyB5wvYrrT1DzA4bH4oRLuO0lF4TS3fMiw8",
            "AIzaSyDKj4QW99q9Kfvues0AtSmGRGNqhYrUr7A",
            "AIzaSyCIt5-vZ45sYP-VlEF98fFbpZAbWOmdNz0",
            "AIzaSyDKzJgxKgHo8mOZ7pJueCRW57x0OQYObBY",
            "AIzaSyD9Bu2jX6jXbuuaTW2Sjh4hhUeuJdYD23s"
        ]
        self.api_key_index = 0
        self.setup_genai()
        self.agent_name = "Carlos"
        # Inicializar el analizador de sentimientos
        self.sentiment_analyzer = SentimentAnalyzer()

    def setup_genai(self):
        try:
            genai.configure(api_key=self.api_keys[self.api_key_index])
            self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
            self.chat = self.genai_model.start_chat(history=[])
        except Exception as e:
            logger.error(f"Error setting up Gemini: {e}")
            self.rotate_api_key()

    def rotate_api_key(self):
        self.api_key_index = (self.api_key_index + 1) % len(self.api_keys)
        self.setup_genai()

    def get_response(self, text: str, conversation_state: Dict = None) -> Tuple[str, bool, Dict]:
        # Initialize conversation state if None
        if conversation_state is None:
            conversation_state = {
                "messages": [],
                "client_verified": False,
                "client_data": None,
                "negotiation_stage": "initial",
                "offer_attempts": 0,
                "last_message_type": None,
                "conversation_flow": [],
                "context": {},
                "sentiment_history": []
            }
        
        # Analyze sentiment
        sentiment_analysis = self.sentiment_analyzer.analyze(text)
        conversation_state['sentiment_history'].append(sentiment_analysis)
        
        # Add message to history
        conversation_state['messages'].append({
            "role": "user", 
            "text": text,
            "sentiment": sentiment_analysis
        })
        
        # Process response based on conversation stage
        if len(conversation_state['messages']) == 1:
            response = self._generate_contextual_greeting(text)
            end_conversation = False
        elif not conversation_state['client_verified']:
            response, end_conversation = self._handle_verification_stage(text, conversation_state)
        else:
            response, end_conversation = self._handle_negotiation(text, conversation_state)

        # Generate conversation metrics if ending
        metrics = {
        'total_messages': len(conversation_state['messages']),
        'sentiment_history': conversation_state['sentiment_history'],
        'negotiation_stage': conversation_state['negotiation_stage'],
        'client_verified': conversation_state['client_verified'],
        'offer_attempts': conversation_state['offer_attempts']
    }   
        return response, end_conversation, metrics

    def _generate_contextual_greeting(self, text: str) -> str:
        greeting_prompt = f"""
        Eres {self.agent_name}, un asesor financiero empático. 
        El cliente dice: "{text}"
        
        Responde naturalmente al saludo, adaptándote al tono del cliente.
        - Si el saludo es informal, responde informal
        - Si es formal, mantén formalidad
        - No uses frases hechas
        - Preséntate solo si es apropiado
        """
        
        try:
            response = self.chat.send_message(greeting_prompt).text
            return response
        except:
            self.rotate_api_key()
            return f"{self._get_time_context()}, soy Carlos. ¿En qué puedo ayudarte?"

    def _handle_verification_stage(self, text: str, conversation_state: Dict) -> Tuple[str, bool]:
        verified, client_data = self.verify_client(text)
        if verified:
            conversation_state['client_verified'] = True
            conversation_state['client_data'] = client_data
            conversation_state['negotiation_stage'] = 'initial_offer'
            return self._generate_initial_offer(text, client_data), False
        
        verification_prompt = f"""
        El cliente dice: "{text}"
        Historial previo: {conversation_state['conversation_flow'][-2:] if len(conversation_state['conversation_flow']) > 1 else 'Inicio'}
        
        Necesitas el DNI y nombre para verificar. Responde:
        - De forma natural y contextual
        - Sin repetir mensajes anteriores
        - Explicando el propósito si hay confusión
        - Manteniendo el tono de la conversación
        """
        
        try:
            response = self.chat.send_message(verification_prompt).text
            return response, False
        except:
            self.rotate_api_key()
            return "Para acceder a las mejores opciones, necesitaría tu DNI y nombre. ¿Me los podrías proporcionar?", False

    def _handle_negotiation(self, text: str, conversation_state: Dict) -> Tuple[str, bool]:
        current_sentiment = conversation_state['sentiment_history'][-1]['sentiment']
        stage = conversation_state['negotiation_stage']
        
        prompt = f"""
        Cliente dice: "{text}"
        Contexto actual:
        - Etapa: {stage}
        - Sentimiento detectado: {current_sentiment}
        - Intentos previos: {conversation_state['offer_attempts']}
        
        Responde:
        - Adaptándote al sentimiento del cliente
        - Manteniendo el objetivo de negociación
        - Con empatía pero firmeza
        - Sin repetir mensajes anteriores
        """
        
        try:
            response = self.chat.send_message(prompt).text
            conversation_state['offer_attempts'] += 1
            
            # Determinar si la conversación debe terminar
            end_conversation = current_sentiment in ['MUY_POSITIVO', 'POSITIVO'] and 'acept' in text.lower()
            
            return response, end_conversation
            
        except:
            self.rotate_api_key()
            return self._generate_fallback_response(current_sentiment, stage), False

    def _generate_initial_offer(self, text: str, client_data: Dict) -> str:
        deuda = float(client_data['deuda'])
        
        plan_unico = {
            'descuento': 0.30,
            'monto_original': deuda,
            'monto_descuento': deuda * 0.30,
            'monto_final': deuda * 0.70
        }
        
        plan_dos_pagos = {
            'descuento': 0.20,
            'monto_original': deuda,
            'monto_descuento': deuda * 0.20,
            'monto_final': deuda * 0.80,
            'monto_por_pago': (deuda * 0.80) / 2
        }
        
        plan_tres_pagos = {
            'descuento': 0.10,
            'monto_original': deuda,
            'monto_descuento': deuda * 0.10,
            'monto_final': deuda * 0.90,
            'monto_por_pago': (deuda * 0.90) / 3
        }

        try:
            prompt = f"""
            Genera una oferta inicial para una deuda de ${deuda:.2f}.
            El cliente dijo: "{text}"

            PLANES DISPONIBLES:
            1. Pago Único:
               - Descuento del 30%
               - Monto original: ${plan_unico['monto_original']:.2f}
               - Descuento: ${plan_unico['monto_descuento']:.2f}
               - Monto final: ${plan_unico['monto_final']:.2f}

            2. Dos Pagos:
               - Descuento del 20%
               - Monto por pago: ${plan_dos_pagos['monto_por_pago']:.2f}

            3. Tres Pagos:
               - Descuento del 10%
               - Monto por pago: ${plan_tres_pagos['monto_por_pago']:.2f}

            INSTRUCCIONES:
            1. Presenta SOLO el plan de pago único inicialmente
            2. Muestra los beneficios del descuento del 30%
            3. Enfatiza que es una oferta por tiempo limitado
            4. Sé empático pero profesional
            5. No menciones los otros planes hasta que el cliente rechace esta oferta
            """
            
            response = self.chat.send_message(prompt).text
            return response
        except:
            self.rotate_api_key()
            return (f"Revisando tu caso, puedo ofrecerte un excelente descuento del 30% "
                   f"si realizas un pago único de ${plan_unico['monto_final']:.2f}, "
                   f"en lugar de los ${plan_unico['monto_original']:.2f} originales. "
                   "¿Te gustaría conocer más detalles de esta oferta especial?")

    def _generate_fallback_response(self, sentiment: str, stage: str) -> str:
        responses = {
            'MUY_NEGATIVO': "Entiendo tu frustración. ¿Qué te parece si exploramos otras opciones más flexibles?",
            'NEGATIVO': "Comprendo tu punto. ¿Qué aspectos de la propuesta te preocupan más?",
            'NEUTRAL': "¿Hay algo específico que te gustaría que te explique mejor?",
            'POSITIVO': "Me alegra que estemos avanzando. ¿Procedemos con esta opción?",
            'MUY_POSITIVO': "Excelente decisión. Permíteme procesar los detalles del acuerdo."
        }
        return responses.get(sentiment, "¿Cómo podría ayudarte mejor?")

    def _get_time_context(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Buenos días"
        elif 12 <= hour < 19:
            return "Buenas tardes"
        else:
            return "Buenas noches"

    def verify_client(self, text: str) -> Tuple[bool, Optional[Dict]]:
        try:
            dni_matches = re.findall(r'\b\d{4}\b', text)
            if not dni_matches:
                return False, None
            
            dni = dni_matches[0]
            client_data = DEBTORS_DB[DEBTORS_DB['dni'] == dni]
            
            if not client_data.empty:
                return True, client_data.to_dict(orient='records')[0]  # Return first match
            else:
                return False, None
        except Exception as e:
            logger.error(f"Error verifying client: {e}")
            return False, None
        