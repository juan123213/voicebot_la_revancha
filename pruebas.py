import google.generativeai as genai
import logging
import re
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, Optional


import negociador.negociador as negociador

def interactive_test():
    negotiator = negociador.DebtNegotiator()
    conversation_state = {
        'client_verified': False,
        'negotiation_stage': 'identification',
        'messages': [],
        'client_data': None
    }
    
    print("Iniciando simulación de negociación (escribe 'salir' para terminar)")
    
    while True:
        user_input = input("\nUsuario: ")
        
        if user_input.lower() == 'salir':
            break
            
        response, should_end = negotiator.get_response(user_input, conversation_state)
        
        conversation_state['messages'].append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        conversation_state['messages'].append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"Asistente: {response}")
        
        if should_end:
            print("\nFin de la negociación.")
            break

if __name__ == "__main__":
    interactive_test()