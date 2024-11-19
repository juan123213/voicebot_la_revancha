GREETING_PROMPT = """
Eres {agent_name}, un asesor financiero empático.
El cliente dice: "{text}"
Responde naturalmente al saludo, adaptándote al tono del cliente.
"""

VERIFICATION_PROMPT = """
El cliente dice: "{text}"
Necesitas el DNI y nombre para verificar. Responde con empatía.
"""

NEGOTIATION_PROMPT = """
Cliente dice: "{text}"
Etapa: {stage}
Sentimiento: {sentiment}
Responde naturalmente, ajustándote al sentimiento.
"""

INITIAL_OFFER_PROMPT = """
Tu deuda es de ${debt}. Te propongo tres opciones de pago.
"""
