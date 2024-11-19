import logging
from datetime import datetime
import re
from config import DEBTORS_DB

logger = logging.getLogger(__name__)

def rotate_api_key(negotiator):
    negotiator.api_key_index = (negotiator.api_key_index + 1) % len(negotiator.api_keys)
    negotiator.setup_genai()

def analyze_response(text: str) -> str:
    # Clasificación de sentimiento
    return "POSITIVE" if "acepto" in text.lower() else "NEGATIVE"

def get_time_context() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Buenos días"
    elif 12 <= hour < 19:
        return "Buenas tardes"
    else:
        return "Buenas noches"

def verify_client(text: str):
    dni_matches = re.findall(r'\b\d{4}\b', text)
    if dni_matches:
        client_data = DEBTORS_DB[DEBTORS_DB['dni'] == dni_matches[0]]
        if not client_data.empty:
            return True, client_data.iloc[0].to_dict()
    return False, None
