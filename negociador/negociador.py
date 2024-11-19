import google.generativeai as genai
import logging
import re
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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

    def get_response(self, text: str, conversation_state: Dict = None) -> Tuple[str, bool]:
        # Initialize or update conversation state
        if conversation_state is None:
            conversation_state = {
                "messages": [],
                "client_verified": False,
                "client_data": None,
                "negotiation_stage": "initial",
                "offer_attempts": 0,
                "last_message_type": None,
                "conversation_flow": [],
                "context": {}
            }
        
        # Ensure all required keys exist
        required_keys = {
            "messages": [],
            "client_verified": False,
            "client_data": None,
            "negotiation_stage": "initial",
            "offer_attempts": 0,
            "last_message_type": None,
            "conversation_flow": [],
            "context": {}
        }
        
        # Update conversation state with any missing keys
        for key, default_value in required_keys.items():
            if key not in conversation_state:
                conversation_state[key] = default_value
        
        # Add user message to history
        conversation_state['messages'].append({"role": "user", "text": text})
        
        # Initial contact
        if len(conversation_state['messages']) == 1:
            response = self._generate_contextual_greeting(text)
            conversation_state['conversation_flow'].append({
                'text': text,
                'response': response,
                'stage': 'greeting'
            })
            return response, False
        
        # Verification stage
        if not conversation_state['client_verified']:
            response, end_conversation = self._handle_verification_stage(text, conversation_state)
            conversation_state['conversation_flow'].append({
                'text': text,
                'response': response,
                'stage': 'verification'
            })
            return response, end_conversation
        
        # Handle negotiation
        response, end_conversation = self._handle_negotiation(text, conversation_state)
        conversation_state['conversation_flow'].append({
            'text': text,
            'response': response,
            'stage': conversation_state['negotiation_stage']
        })
        return response, end_conversation

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
        sentiment = self._analyze_response(text)
        stage = conversation_state['negotiation_stage']
        
        negotiation_context = {
            'text': text,
            'stage': stage,
            'attempts': conversation_state['offer_attempts'],
            'last_response': conversation_state['conversation_flow'][-1]['response'] if conversation_state['conversation_flow'] else None,
            'sentiment': sentiment
        }
        
        prompt = f"""
        Cliente dice: "{text}"
        Contexto actual:
        - Etapa: {stage}
        - Sentimiento: {sentiment}
        - Intentos: {negotiation_context['attempts']}
        
        Responde:
        - Naturalmente y sin repetir
        - Adaptándote al sentimiento
        - Manteniendo el objetivo de negociación
        - Con empatía pero firmeza
        """
        
        try:
            response = self.chat.send_message(prompt).text
            
            # Update negotiation state
            conversation_state['offer_attempts'] += 1
            conversation_state['last_message_type'] = sentiment
            
            return response, sentiment == 'POSITIVE'
            
        except:
            self.rotate_api_key()
            return self._generate_fallback_response(sentiment, stage), False

    def _generate_initial_offer(self, text: str, client_data: Dict) -> str:
        try:
            return self.chat.send_message(
                f"""
                Genera una primera oferta para deuda de ${client_data['deuda']}.
                El cliente dijo: "{text}"
                
                La oferta debe ser:
                - Natural y empática
                - Adaptada al contexto
                - Sin frases hechas
                - Enfocada en beneficios principales
                GUÍA DE NEGOCIACIÓN DE DEUDA - INSTRUCCIONES PARA ASESORES

PRIMERA OPCIÓN - PAGO ÚNICO (Descuento 30%)


Presentar como primera y mejor opción
Describir: "Pago único con 30% de descuento sobre el total de la deuda"
Enfatizar que es la opción con mayor ahorro
Mencionar que es válida solo si se realiza el pago hoy mismo
Calcular y mostrar: monto original, descuento y monto final a pagar


SEGUNDA OPCIÓN - DOS PAGOS (Descuento 20%)


Presentar SOLO si el cliente rechaza la primera opción
Describir: "División en dos pagos con 20% de descuento total"
Calcular y mostrar: monto por cada pago
Especificar que el primer pago debe realizarse hoy
Explicar que el segundo pago debe realizarse en 30 días


TERCERA OPCIÓN - TRES PAGOS (Descuento 10%)


Presentar SOLO si el cliente rechaza las dos primeras opciones
Describir: "División en tres pagos con 10% de descuento total"
Calcular y mostrar: monto por cada pago
Especificar que el primer pago debe realizarse hoy
Explicar que los pagos restantes son a 30 y 60 días

REGLAS IMPORTANTES:

Presentar las opciones EN ORDEN y una a la vez
NO mencionar la siguiente opción hasta que la actual sea rechazada
Una vez aceptada una opción:

Confirmar los montos y fechas
Proporcionar información de pago
Explicar proceso de envío de comprobantes
Mantener comunicación abierta para dudas



RECORDATORIOS:

Mantener tono profesional y empático
Enfatizar que los descuentos son por tiempo limitado
Explicar que el primer pago siempre debe ser hoy
Aclarar dudas sobre montos y fechas
Si rechazan todas las opciones, dejar la puerta abierta para futuras negociaciones
                """
            ).text
        except:
            self.rotate_api_key()
            return f"He revisado tu caso y tengo una propuesta especial para tu deuda. ¿Te gustaría conocerla?"

    def _analyze_response(self, text: str) -> str:
        try:
            result = self.chat.send_message(
                f"""
                Clasifica como POSITIVE/NEGATIVE/QUESTION/HESITANT/UNCLEAR:
                "{text}"
                Responde solo con la clasificación.
                """
            ).text.strip().upper()
            return result if result in ['POSITIVE', 'NEGATIVE', 'QUESTION', 'HESITANT', 'UNCLEAR'] else 'UNCLEAR'
        except:
            self.rotate_api_key()
            return "UNCLEAR"

    def _generate_fallback_response(self, sentiment: str, stage: str) -> str:
        responses = {
            'NEGATIVE': "Comprendo tu punto. ¿Qué te parecería una alternativa más flexible?",
            'QUESTION': "Dime qué parte te gustaría que te explique mejor",
            'HESITANT': "Entiendo tu duda. ¿Qué aspecto te preocupa más?",
            'UNCLEAR': "¿Podrías explicarme mejor tu situación para ayudarte?"
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
                return True, client_data.iloc[0].to_dict()
            return False, None
        except Exception as e:
            logger.error(f"Error verifying client: {e}")
            return False, None