import re
import pandas as pd
import os
try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
except (ImportError, OSError):
    # Mock spacy if not available
    spacy = None
    class MockNLP:
        def __init__(self):
            pass
        def __call__(self, text):
            return MockDoc(text)
    class MockDoc:
        def __init__(self, text):
            self.text = text
            self.ents = []
    nlp = MockNLP()

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import json
import smtplib
from email.message import EmailMessage
import unicodedata
import requests

# Expanded intent examples for robust code-mixed support
intent_examples = [
    # English
    ("I want to book a car service", "book_service"),
    ("Book oil change", "book_service"),
    ("Schedule car inspection", "book_service"),
    ("I need a car inspection in Lahore", "book_service"),
    ("Book detailing for my Suzuki Alto", "book_service"),
    ("Search for cars", "search_car"),
    ("Show me cars for sale", "search_car"),
    ("Find Toyota Corolla in Lahore", "search_car"),
    ("Find Honda City under 20 lacs", "search_car"),
    ("Show me used cars in Karachi", "search_car"),
    ("Tell me about Honda Civic", "car_info"),
    ("What are the variants of Suzuki Alto?", "car_info"),
    ("Known faults of Toyota Prius", "car_info"),
    ("Problems with Honda City", "car_info"),
    ("Help", "help"),
    ("Madad", "help"),
    # Urdu
    ("مجھے کار سروس بک کرنی ہے", "book_service"),
    ("آئل چینج بک کریں", "book_service"),
    ("لاہور میں کار انسپیکشن چاہیے", "book_service"),
    ("سوزوکی آلٹو کی ڈیٹیلنگ بک کریں", "book_service"),
    ("گاڑیاں تلاش کریں", "search_car"),
    ("فروخت کے لیے کاریں دکھائیں", "search_car"),
    ("لاہور میں ٹویوٹا کرولا تلاش کریں", "search_car"),
    ("ہونڈا سٹی 20 لاکھ سے کم", "search_car"),
    ("کراچی میں استعمال شدہ کاریں دکھائیں", "search_car"),
    ("ہونڈا سوک کے بارے میں بتائیں", "car_info"),
    ("سوزوکی آلٹو کے ویرینٹس کیا ہیں؟", "car_info"),
    ("ٹویوٹا پریوس کے مسائل", "car_info"),
    ("ہونڈا سٹی کے مسائل", "car_info"),
    ("مدد", "help"),
    # Code-mixed
    ("Mujhe car service book karni hai", "book_service"),
    ("Lahore mein Honda City chahiye", "search_car"),
    ("Suzuki Alto ki maloomat do", "car_info"),
    ("Oil change book karen", "book_service"),
    ("Karachi mein used cars dikhain", "search_car"),
    ("Help karo", "help"),
    ("Madad chahiye", "help"),
    ("Honda City under 20 لاکھ", "search_car"),
    ("Toyota Corolla ki variants batao", "car_info"),
    ("Book detailing for میری Suzuki Alto", "book_service"),
    ("Find Toyota Corolla in لاہور", "search_car"),
    ("Show me استعمال شدہ cars in Karachi", "search_car"),
    ("Suzuki Alto کے بارے میں بتائیں", "car_info"),
]
vectorizer = CountVectorizer()
X = vectorizer.fit_transform([x[0] for x in intent_examples])
y = [x[1] for x in intent_examples]
intent_clf = LogisticRegression().fit(X, y)

# Car brands/models/cities for entity extraction
CAR_BRANDS = ["Toyota", "Honda", "Suzuki", "KIA", "Hyundai", "MG", "Daihatsu", "Nissan", "Mitsubishi", "Mercedes", "BMW"]
CITIES = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Faisalabad", "Gujranwala", "Multan", "Sargodha", "Hyderabad"]
SERVICES = ["oil change", "tuning", "detailing", "inspection", "maintenance", "repair"]

# Improved Urdu detection: returns True if both Urdu and English present (code-mixed), or only Urdu
def detect_urdu(text):
    urdu_count = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    eng_count = sum(1 for c in text if 'A' <= c <= 'Z' or 'a' <= c <= 'z')
    # Code-mixed if both Urdu and English present
    return urdu_count > 0 and (eng_count > 0 or len(text) > urdu_count)

# Add Urdu keywords for brands, cities, and services
URDU_CAR_BRANDS = ["ٹويوٹا", "ہونڈا", "سوزوکی", "کِیا", "ہنڈائی", "ایم جی", "ڈائی ہاٹسو", "نسان", "مٹسوبشی", "مرسڈیز", "بی ایم ڈبلیو"]
URDU_CITIES = ["کراچی", "لاہور", "اسلام آباد", "راولپنڈی", "پشاور", "فیصل آباد", "گوجرانوالہ", "ملتان", "سرگودھا", "حیدرآباد"]
URDU_SERVICES = ["آئل چینج", "ٹیوننگ", "ڈیٹیلنگ", "انسپیکشن", "مینٹیننس", "مرمت"]

# Improved entity extraction
def extract_entities(text):
    doc = nlp(text)
    entities = {}
    # spaCy NER
    for ent in doc.ents:
        entities[ent.label_] = ent.text
    # Advanced NER: use custom model or rules for car models/variants/Urdu
    adv_ents = advanced_ner(text, lang='ur' if detect_urdu(text) else 'en')
    entities.update(adv_ents)
    # Urdu NER (placeholder, can be replaced with Urduhack)
    if detect_urdu(text):
        urdu_ents = urdu_ner(text)
        entities.update(urdu_ents)
    # Custom for car brands/models/cities/services (English)
    for brand in CAR_BRANDS:
        if brand.lower() in text.lower():
            entities['CAR_BRAND'] = brand
    for city in CITIES:
        if city.lower() in text.lower():
            entities['CITY'] = city
    for service in SERVICES:
        if service in text.lower():
            entities['SERVICE_TYPE'] = service
    # Custom for car brands/models/cities/services (Urdu)
    urdu_to_eng_brand = dict(zip(URDU_CAR_BRANDS, CAR_BRANDS))
    urdu_to_eng_city = dict(zip(URDU_CITIES, CITIES))
    urdu_to_eng_service = dict(zip(URDU_SERVICES, SERVICES))
    for brand in URDU_CAR_BRANDS:
        if brand in text:
            entities['CAR_BRAND'] = urdu_to_eng_brand[brand]
    for city in URDU_CITIES:
        if city in text:
            entities['CITY'] = urdu_to_eng_city[city]
    for service in URDU_SERVICES:
        if service in text:
            entities['SERVICE_TYPE'] = urdu_to_eng_service[service]
    # Budget (English and Urdu)
    budget_match = re.search(r'(\d{1,3})\s*(lacs|lac|لاکھ)', text.lower())
    if budget_match:
        entities['BUDGET'] = budget_match.group(1)
    return entities

def classify_intent(text):
    X_test = vectorizer.transform([text])
    return intent_clf.predict(X_test)[0]

user_state = {}

USER_STATE_FILE = 'user_state.json'
CHAT_HISTORIES_FILE = 'chat_histories.json'

# Load user state from disk
if os.path.exists(USER_STATE_FILE):
    with open(USER_STATE_FILE, 'r', encoding='utf-8') as f:
        user_state = json.load(f)
else:
    user_state = {}

# Load chat histories from disk
if os.path.exists(CHAT_HISTORIES_FILE):
    with open(CHAT_HISTORIES_FILE, 'r', encoding='utf-8') as f:
        chat_histories = json.load(f)
else:
    chat_histories = {}

def save_user_state():
    with open(USER_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_state, f, ensure_ascii=False, indent=2)

def save_chat_histories():
    with open(CHAT_HISTORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(chat_histories, f, ensure_ascii=False, indent=2)

def append_to_chat_history(user_id, sender, message):
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({
        'sender': sender,
        'message': message
    })
    save_chat_histories()

def get_chat_history(user_id):
    return chat_histories.get(user_id, [])

def get_all_chat_histories():
    return chat_histories

def send_booking_email(user_id, booking_details):
    # Real SMTP email sending with user-friendly error and .env support
    try:
        msg = EmailMessage()
        msg['Subject'] = f'New Car Service Booking from {user_id}'
        msg['From'] = os.environ.get('SMTP_SENDER', 'pakbot@example.com')
        msg['To'] = os.environ.get('SMTP_RECEIVER', 'servicecenter@example.com')
        msg.set_content(f"Booking Details:\n" + '\n'.join([f"{k}: {v}" for k, v in booking_details.items()]))
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.example.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER', 'user')
        smtp_pass = os.environ.get('SMTP_PASS', 'pass')
        if smtp_server == 'smtp.example.com':
            print("[Email] WARNING: SMTP server not configured. Set SMTP_SERVER and credentials as environment variables.")
            print(f"[Email] Would send: {msg}")
            return
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"[Email] Sent booking: {booking_details}")
    except Exception as e:
        print(f"[Email] Failed: {e}")
        # Optionally, log or notify admin here

# Advanced NER placeholder (for future custom model integration)
def advanced_ner(text, lang='en'):
    # Expanded regex-based extraction for car models, variants, engine, year, and cc
    result = {}
    # Brand + Model + Variant + Engine + Year (e.g., "Toyota Corolla Altis Grande 1.8 2021")
    car_pattern = r"((Toyota|Honda|Suzuki|KIA|Hyundai|MG|Daihatsu|Nissan|Mitsubishi|Mercedes|BMW)\s+[A-Za-z0-9\- ]{2,})"
    model_match = re.search(car_pattern, text, re.IGNORECASE)
    if model_match:
        result['MODEL'] = model_match.group(1).strip()
    # Variant (multiple common ones)
    variant_pattern = r"\b(GLi|Aspire|VXL|VX|Altis|Grande|XLi|RS|Turbo|G|F|S|SE|EX|DLX|AT|MT|AG|Alpha|Sigma|Base|Oriel|RS Turbo|RS-Turbo|Hybrid|Primo|Prosmatec|Civic X|Civic XI|Civic 10th|Civic 11th)\b"
    variants = re.findall(variant_pattern, text, re.IGNORECASE)
    if variants:
        result['VARIANT'] = ' '.join(set(variants))
    # Engine size (e.g., 1.3, 1.5L, 660cc, 1800cc)
    engine_pattern = r"(\d{1,2}\.\d{1,2}\s?L|\d{3,4}\s?cc)"
    engine_match = re.search(engine_pattern, text, re.IGNORECASE)
    if engine_match:
        result['ENGINE'] = engine_match.group(1).replace(' ', '')
    # Year (e.g., 2015, 2021)
    year_pattern = r"(19\d{2}|20\d{2})"
    year_match = re.search(year_pattern, text)
    if year_match:
        result['YEAR'] = year_match.group(1)
    return result

# Urdu NER with Urduhack integration (improved)
def urdu_ner(text):
    try:
        import urduhack
        from urduhack.ner import NER
        urduhack.download('ner')
        urduhack.initialize()
        ner = NER()
        doc = urduhack.Pipeline(text)
        entities = {}
        for ent in doc.entities:
            # Map Urduhack entity types to our schema if needed
            if ent[2] == 'LOCATION':
                entities['CITY'] = ent[0]
            elif ent[2] == 'ORGANIZATION':
                entities['CAR_BRAND'] = ent[0]
            elif ent[2] == 'PERSON':
                entities['MODEL'] = ent[0]
            # Add more mappings as needed
        return entities
    except ImportError:
        return {}
    except Exception:
        return {}

# Voice input/output hooks (integration-ready)
def process_voice_input(audio_data):
    # TODO: Integrate speech-to-text
    return "[voice to text not implemented]"
def generate_voice_output(text):
    # TODO: Integrate text-to-speech
    return None

# Feedback collection
FEEDBACK_FILE = 'user_feedback.txt'
def save_feedback(user_id, feedback):
    with open(FEEDBACK_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{user_id}: {feedback}\n")

# --- Transformer-based response config ---
USE_TRANSFORMER = os.environ.get('USE_TRANSFORMER', 'false').lower() == 'true'
# Default to Qwen1.5-7B-Chat (permissive, free, multilingual, good for code-mixed)
TRANSFORMER_MODEL = os.environ.get('TRANSFORMER_MODEL', 'Qwen/Qwen1.5-7B-Chat')

# --- Local HuggingFace Transformers inference ---
try:
    from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
    _transformer_pipe = None
    def get_local_transformer_pipe():
        global _transformer_pipe
        if _transformer_pipe is None:
            tokenizer = AutoTokenizer.from_pretrained(TRANSFORMER_MODEL)
            model = AutoModelForCausalLM.from_pretrained(TRANSFORMER_MODEL)
            _transformer_pipe = pipeline('text-generation', model=model, tokenizer=tokenizer, max_new_tokens=128)
        return _transformer_pipe
    def get_transformer_response(prompt, lang_hint=None):
        pipe = get_local_transformer_pipe()
        # Optionally add language hint to prompt
        if lang_hint == 'ur':
            prompt = f"[Urdu] {prompt}"
        elif lang_hint == 'en':
            prompt = f"[English] {prompt}"
        result = pipe(prompt, num_return_sequences=1)
        return result[0]['generated_text'][len(prompt):].strip()
except ImportError:
    def get_transformer_response(prompt, lang_hint=None):
        return "[Transformer model not installed. Please install transformers and a model.]"

def format_response_multiline(text):
    # Split on sentence-ending punctuation followed by space or end, add <br>
    import re
    # Only split if not already HTML (avoid double <br>)
    if '<br>' in text:
        return text
    # Split on . ! ? (including Urdu equivalents) followed by space or end
    sentences = re.split(r'(?<=[.!?۔؟])\s+', text)
    return '<br>'.join(s.strip() for s in sentences if s.strip())

def handle_user_message(message, user_id='default'):
    global user_state, chat_histories
    message = message.strip()
    # --- New session reset logic ---
    if message == '__new_session__':
        user_state[user_id] = {'step': 'greet'}
        save_user_state()
        # Start new chat history for this session
        chat_histories[user_id] = []
        append_to_chat_history(user_id, 'user', message)
        greeting = ("Hello! I'm PakBot, your PakWheels assistant. What would you like to do today?\n"
                    "1. Book a car service (oil change, tuning, detailing, etc.)\n"
                    "2. Search for cars to buy\n"
                    "3. Get information about a car\n"
                    "Please reply with 1, 2, or 3.")
        greeting = format_response_multiline(greeting)
        append_to_chat_history(user_id, 'bot', greeting)
        save_chat_histories()
        return greeting
    # Admin command: show all or recent feedback
    if user_id == 'admin' and message.lower().startswith('show feedback'):
        try:
            with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if 'all' in message.lower():
                return 'All feedback:\n' + ''.join(lines) if lines else 'No feedback yet.'
            else:
                return 'Recent feedback:\n' + ''.join(lines[-5:]) if lines else 'No feedback yet.'
        except Exception:
            return 'No feedback yet.'
    # User authentication (simple username-based)
    if user_id == 'default' and message.lower().startswith('login:'):
        username = message.split(':', 1)[-1].strip()
        user_id = username
        if user_id not in user_state:
            user_state[user_id] = {'step': 'greet'}
        save_user_state()
        return f"Welcome, {user_id}! How can I assist you today?"
    if user_id not in user_state:
        user_state[user_id] = {'step': 'greet'}
    is_urdu = detect_urdu(message)
    state = user_state.get(user_id, {'step': 'greet'})
    response = ""
    # Use ML intent/entity extraction for free text at main menu
    if state['step'] == 'main_menu' and not message.isdigit():
        intent = classify_intent(message)
        entities = extract_entities(message)
        # Auto-fill slots from entities
        if intent == 'book_service':
            state['step'] = 'service_car_details'
            # If car details found, skip to service type
            car_info = []
            if 'CAR_BRAND' in entities:
                car_info.append(entities['CAR_BRAND'])
            if 'MODEL' in entities:
                car_info.append(entities['MODEL'])
            if 'DATE' in entities:
                state['datetime'] = entities['DATE']
            if car_info:
                state['car_details'] = ' '.join(car_info)
                state['step'] = 'service_type'
                user_state[user_id] = state
                if 'SERVICE_TYPE' in entities:
                    state['service_type'] = entities['SERVICE_TYPE']
                    state['step'] = 'service_datetime'
                    user_state[user_id] = state
                    return "Please provide your preferred date and time for the service (e.g., Tomorrow 2:00 PM)."
                return "Which service do you want to book? (e.g., oil change, tuning, detailing)"
            user_state[user_id] = state
            return "Please provide your car's make, model, and year (e.g., Honda Civic 2018)."
        elif intent == 'search_car':
            # Auto-fill filters
            state['step'] = 'search_filters_brand'
            if 'CAR_BRAND' in entities:
                state['brand'] = entities['CAR_BRAND']
                state['step'] = 'search_filters_budget'
                if 'BUDGET' in entities:
                    state['budget'] = entities['BUDGET'] + ' lacs'
                    state['step'] = 'search_filters_year'
                if 'CITY' in entities:
                    state['city'] = entities['CITY']
            user_state[user_id] = state
            if state['step'] == 'search_filters_brand':
                return "Which car brand/model are you interested in? (e.g., Toyota Corolla) Or type 'any'."
            elif state['step'] == 'search_filters_budget':
                return "What is your budget range? (e.g., 10-20 lacs)"
            elif state['step'] == 'search_filters_year':
                return "Preferred year range? (e.g., 2015-2022)"
            elif state.get('city'):
                return "Preferred mileage (e.g., under 50,000 km)?"
        elif intent == 'car_info':
            state['step'] = 'car_info_query'
            if 'CAR_BRAND' in entities:
                state['car_info_name'] = entities['CAR_BRAND']
                user_state[user_id] = state
                return f"Fetching information about {entities['CAR_BRAND']}..."
            user_state[user_id] = state
            return "Please enter the car name you want information about (e.g., Suzuki Alto)."
        elif intent == 'help':
            state['step'] = 'greet'
            user_state[user_id] = state
            if is_urdu:
                return "Aap mujh se car service book karwa saktay hain, car search kar saktay hain, ya car ki maloomat hasil kar saktay hain. Kya aapko aur koi madad chahiye?"
            else:
                return "You can book a car service, search for cars, or get car information. Is there anything else I can help you with today?"
    # Greeting and main menu
    if state['step'] == 'greet':
        if is_urdu:
            response = "Assalam o Alaikum! Main PakBot hoon, aap ki madad ke liye hazir hoon. Aaj aap kya karna chahenge?\n1. Car service book karen\n2. Car khareedne ke لیے search karen\n3. Car ki maloomat حاصل کریں\nBarah-e-karam apna intikhab batain (1, 2, ya 3)."
        else:
            response = ("Hello! I'm PakBot, your PakWheels assistant. What would you like to do today?\n"
                        "1. Book a car service (oil change, tuning, detailing, etc.)\n"
                        "2. Search for cars to buy\n"
                        "3. Get information about a car\n"
                        "Please reply with 1, 2, or 3.")
        response = format_response_multiline(response)
        state['step'] = 'main_menu'
        user_state[user_id] = state
        append_to_chat_history(user_id, 'bot', response)
        return response
    # Main menu selection
    if state['step'] == 'main_menu':
        # Enhanced: always use intent/entity extraction for free-form questions
        if message.isdigit() or message.strip() in ['1', '2', '3']:
            if '1' in message or ('service' in message.lower()):
                state['step'] = 'service_car_details'
                user_state[user_id] = state
                response = "Please provide your car's make, model, and year (e.g., Honda Civic 2018)."
                response = format_response_multiline(response)
                append_to_chat_history(user_id, 'bot', response)
                return response
            elif '2' in message or ('search' in message.lower()):
                state['step'] = 'search_filters_brand'
                user_state[user_id] = state
                response = "Which car brand/model are you interested in? (e.g., Toyota Corolla) Or type 'any'."
                response = format_response_multiline(response)
                append_to_chat_history(user_id, 'bot', response)
                return response
            elif '3' in message or ('info' in message.lower() or 'maloomat' in message):
                state['step'] = 'car_info_query'
                user_state[user_id] = state
                response = "Please enter the car name you want information about (e.g., Suzuki Alto)."
                response = format_response_multiline(response)
                append_to_chat_history(user_id, 'bot', response)
                return response
            else:
                response = "Sorry, I didn't understand. Please reply with 1, 2, or 3."
                response = format_response_multiline(response)
                append_to_chat_history(user_id, 'bot', response)
                return response
        else:
            # Use ML intent/entity extraction for any free-form question
            intent = classify_intent(message)
            entities = extract_entities(message)
            # Auto-fill slots from entities
            if intent == 'book_service':
                state['step'] = 'service_car_details'
                car_info = []
                if 'CAR_BRAND' in entities:
                    car_info.append(entities['CAR_BRAND'])
                if 'MODEL' in entities:
                    car_info.append(entities['MODEL'])
                if 'DATE' in entities:
                    state['datetime'] = entities['DATE']
                if car_info:
                    state['car_details'] = ' '.join(car_info)
                    state['step'] = 'service_type'
                    user_state[user_id] = state
                    if 'SERVICE_TYPE' in entities:
                        state['service_type'] = entities['SERVICE_TYPE']
                        state['step'] = 'service_datetime'
                        user_state[user_id] = state
                        return "Please provide your preferred date and time for the service (e.g., Tomorrow 2:00 PM)."
                    return "Which service do you want to book? (e.g., oil change, tuning, detailing)"
                user_state[user_id] = state
                return "Please provide your car's make, model, and year (e.g., Honda Civic 2018)."
            elif intent == 'search_car':
                state['step'] = 'search_filters_brand'
                if 'CAR_BRAND' in entities:
                    state['brand'] = entities['CAR_BRAND']
                    state['step'] = 'search_filters_budget'
                    if 'BUDGET' in entities:
                        state['budget'] = entities['BUDGET'] + ' lacs'
                        state['step'] = 'search_filters_year'
                    if 'CITY' in entities:
                        state['city'] = entities['CITY']
                user_state[user_id] = state
                if state['step'] == 'search_filters_brand':
                    return "Which car brand/model are you interested in? (e.g., Toyota Corolla) Or type 'any'."
                elif state['step'] == 'search_filters_budget':
                    return "What is your budget range? (e.g., 10-20 lacs)"
                elif state['step'] == 'search_filters_year':
                    return "Preferred year range? (e.g., 2015-2022)"
                elif state.get('city'):
                    return "Preferred mileage (e.g., under 50,000 km)?"
            elif intent == 'car_info':
                state['step'] = 'car_info_query'
                if 'CAR_BRAND' in entities:
                    state['car_info_name'] = entities['CAR_BRAND']
                    user_state[user_id] = state
                    return f"Fetching information about {entities['CAR_BRAND']}..."
                user_state[user_id] = state
                return "Please enter the car name you want information about (e.g., Suzuki Alto)."
            elif intent == 'help':
                state['step'] = 'greet'
                user_state[user_id] = state
                if is_urdu:
                    return "Aap mujh se car service book karwa saktay hain, car search kar saktay hain, ya car ki maloomat hasil kar saktay hain. Kya aapko aur koi madad chahiye?"
                else:
                    return "You can book a car service, search for cars, or get car information. Is there anything else I can help you with today?"
            else:
                response = "Sorry, I didn't understand. Please reply with 1, 2, or 3."
                response = format_response_multiline(response)
                append_to_chat_history(user_id, 'bot', response)
                return response
    # Service booking flow
    if state['step'] == 'service_car_details':
        state['car_details'] = message
        state['step'] = 'service_type'
        user_state[user_id] = state
        response = f"Great! You want service for '{message}'. What type of service do you need? (e.g., oil change, tuning, detailing)"
        response = format_response_multiline(response)
        append_to_chat_history(user_id, 'bot', response)
        return response
    if state['step'] == 'service_type':
        state['service_type'] = message
        state['step'] = 'service_datetime'
        user_state[user_id] = state
        car_details = state.get('car_details', 'your car')
        response = f"You've selected '{message}' for {car_details}. When would you like to book this service? (e.g., Tomorrow 2:00 PM)"
        response = format_response_multiline(response)
        append_to_chat_history(user_id, 'bot', response)
        return response
    if state['step'] == 'service_datetime':
        # Validate date/time input
        def is_valid_datetime_input(dt_input):
            # Accepts common date/time phrases or patterns
            dt_input = dt_input.strip().lower()
            # Reject negative/ambiguous responses
            if any(x in dt_input for x in ["no offer", "other time", "not sure", "don't know", "later", "anytime", "no", "none", "nahi", "pata nahi"]):
                return False
            # Accept if contains a day, date, or time pattern
            date_patterns = [
                r"\b(tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
                r"\b(\d{1,2}[:\.]\d{2}\s?(am|pm)?)\b",
                r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b",
                r"\b(\d{1,2}-\d{1,2}-\d{2,4})\b",
                r"\b(\d{1,2}\s*(am|pm))\b",
                r"\b(\d{4})\b"  # year (not enough alone, but helps)
            ]
            for pat in date_patterns:
                if re.search(pat, dt_input):
                    return True
            return False
        if not is_valid_datetime_input(message):
            return ("Sorry, I couldn't understand the date and time you provided. "
                    "Please enter a valid date and time for your booking (e.g., Tomorrow 2:00 PM, 5 July 3pm, or 10/07/2025 11:00 AM). If you want to cancel, type 'cancel'.")
        state['datetime'] = message
        state['step'] = 'service_confirm'
        user_state[user_id] = state
        car_details = state.get('car_details','your car')
        service_type = state.get('service_type','the selected service')
        datetime = state.get('datetime','your chosen time')
        send_booking_email(user_id, {
            'car_details': car_details,
            'service_type': service_type,
            'datetime': datetime
        })
        save_user_state()
        response = (f"Thank you! Your booking for {car_details} ({service_type}) on '{datetime}' is confirmed. "
                f"Our team will contact you soon to finalize the details.\n\nIf you need to book another service or have any questions, just let me know!")
        response = format_response_multiline(response)
        append_to_chat_history(user_id, 'bot', response)
        return response
    # Car search flow
    if state['step'] == 'search_filters_brand':
        if not state.get('brand'):
            state['brand'] = message
        state['step'] = 'search_filters_budget'
        user_state[user_id] = state
        response = f"Awesome! You're interested in '{state['brand']}'. What's your budget range? (e.g., 10-20 lacs)"
        response = format_response_multiline(response)
        append_to_chat_history(user_id, 'bot', response)
        return response
    if state['step'] == 'search_filters_budget':
        if not state.get('budget'):
            # Validate budget (should be a number or range in lacs)
            budget_input = message.lower().replace('crore', '0000000').replace('million', '000000').replace('lacs', '').replace('lac', '').replace(' ', '').replace(',', '')
            import re
            range_match = re.match(r'^(\d+)[-–](\d+)$', budget_input)
            single_match = re.match(r'^(\d+)$', budget_input)
            if range_match:
                min_b, max_b = int(range_match.group(1)), int(range_match.group(2))
                if min_b < 1 or max_b > 1000 or min_b > max_b:
                    response = "That budget range seems unrealistic. Please enter a reasonable budget range in lacs (e.g., 10-20 lacs)."
                    response = format_response_multiline(response)
                    append_to_chat_history(user_id, 'bot', response)
                    return response
            elif single_match:
                val = int(single_match.group(1))
                if val < 1 or val > 1000:
                    response = "That budget seems unrealistic. Please enter a reasonable budget in lacs (e.g., 10-20 lacs)."
                    response = format_response_multiline(response)
                    append_to_chat_history(user_id, 'bot', response)
                    return response
            else:
                # If user input is a question or not a number, give a friendly, context-aware message
                if '?' in message or message.strip().endswith('?') or any(word in message.lower() for word in ['have', 'offer', 'available', 'stock', 'sell', 'buy']):
                    response = ("If you're asking about Hummer availability, I can check listings for you!<br>"
                                "But first, please tell me your budget range in lacs (e.g., 10-20 lacs) so I can show you relevant options.")
                else:
                    response = "Sorry, I couldn't understand your budget. Please enter a number or range in lacs (e.g., 10-20 lacs)."
                response = format_response_multiline(response)
                append_to_chat_history(user_id, 'bot', response)
                return response
            state['budget'] = message
        state['step'] = 'search_filters_year'
        user_state[user_id] = state
        response = f"Got it. Your budget is '{state['budget']}'. What year range are you looking for? (e.g., 2015-2022)"
        response = format_response_multiline(response)
        append_to_chat_history(user_id, 'bot', response)
        return response
    if state['step'] == 'search_filters_year':
        # Validate year (should be a year or range, not far in the future)
        import re
        year_input = message.replace(' ', '')
        year_match = re.match(r'^(\d{4})[-–](\d{4})$', year_input)
        single_year = re.match(r'^(\d{4})$', year_input)
        current_year = 2025
        if year_match:
            min_y, max_y = int(year_match.group(1)), int(year_match.group(2))
            if min_y < 1980 or max_y > current_year or min_y > max_y:
                response = f"That year range seems unrealistic. Please enter a valid year range between 1980 and {current_year} (e.g., 2015-2022)."
                response = format_response_multiline(response)
                append_to_chat_history(user_id, 'bot', response)
                return response
        elif single_year:
            y = int(single_year.group(1))
            if y < 1980 or y > current_year:
                response = f"That year seems unrealistic. Please enter a valid year between 1980 and {current_year}."
                response = format_response_multiline(response)
                append_to_chat_history(user_id, 'bot', response)
                return response
        else:
            response = f"Sorry, I couldn't understand the year. Please enter a year or range (e.g., 2015-2022)."
            response = format_response_multiline(response)
            append_to_chat_history(user_id, 'bot', response)
            return response
        state['year'] = message
        state['step'] = 'search_filters_mileage'
        user_state[user_id] = state
        response = f"Noted! Preferred year: '{state['year']}'. Any mileage preference? (e.g., under 50,000 km)"
        response = format_response_multiline(response)
        append_to_chat_history(user_id, 'bot', response)
        return response
    if state['step'] == 'search_filters_mileage':
        state['mileage'] = message
        state['step'] = 'search_filters_city'
        user_state[user_id] = state
        response = f"Thanks! Mileage: '{state['mileage']}'. Which city do you want to search in? (e.g., Karachi, Lahore, Islamabad)"
        response = format_response_multiline(response)
        append_to_chat_history(user_id, 'bot', response)
        return response
    if state['step'] == 'search_filters_city':
        if not state.get('city'):
            state['city'] = message
        csv_path = os.path.join('data', 'pakwheels_listings.csv')
        # car_knowledge can be kept for a few special cases, but fallback is always transformer
        car_knowledge = {
            'hummer h2': "The Hummer H2 is a luxury SUV, known for its off-road capability and bold design. It's very rare in Pakistan and usually imported as a used vehicle. If you don't see any listings, it's likely not available locally at the moment. Would you like to search for a similar SUV or another car?",
            # Add more car knowledge here as needed
        }
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if state['brand'].lower() != 'any':
                df = df[df['name'].str.lower().str.contains(state['brand'].lower())]
            budget_match = re.search(r'(\d+)[-–](\d+)', state['budget'].replace('lacs','').replace('lac','').replace(' ','').replace(',',''))
            if budget_match:
                min_b, max_b = int(budget_match.group(1)), int(budget_match.group(2))
                df = df[df['price'].str.replace('PKR','').str.replace('lacs','').str.replace('lac','').str.replace(',','').str.extract(r'(\d+)').astype(float)[0].between(min_b, max_b)]
            year_match = re.search(r'(\d{4})[-–](\d{4})', state['year'])
            if year_match:
                min_y, max_y = int(year_match.group(1)), int(year_match.group(2))
                df = df[df['name'].str.extract(r'(\d{4})').astype(float)[0].between(min_y, max_y)]
            mileage_match = re.search(r'(\d{1,3}[,\d]*)', state['mileage'].replace('km','').replace(' ','').replace(',',''))
            if mileage_match:
                max_m = int(mileage_match.group(1).replace(',',''))
                df = df[df['mileage'].str.replace('km','').str.replace(',','').astype(float) <= max_m]
            if state['city'].lower() != 'any':
                df = df[df['location'].str.lower().str.contains(state['city'].lower())]
            if not df.empty:
                cars = df.head(3)
                car_lines = []
                for _, row in cars.iterrows():
                    img_url = row.get('image_url', None)
                    line = f"<b>{row['name']}</b> | {row['price']} | {row['year']} | {row['mileage']} | {row['location']}<br><a href='{row['url']}' target='_blank'>View Listing</a>"
                    if img_url and isinstance(img_url, str) and img_url.strip():
                        line += f"<br><a href='{img_url}' target='_blank'><img src='{img_url}' alt='car image' style='max-width:120px;max-height:80px;border:1px solid #ccc;margin:4px 0;'></a>"
                    car_lines.append(line)
                response = "Here are some great options for you:<br>" + '<br><br>'.join(car_lines)
            else:
                # Always provide knowledge or transformer-based info for any car
                brand_query = state['brand']
                car_lower = brand_query.lower()
                if car_lower in car_knowledge:
                    response = car_knowledge[car_lower]
                elif USE_TRANSFORMER:
                    prompt = (
                        f"Give a detailed, car-enthusiast-level overview of the {brand_query} (all variants, all years, including history, specs, features, and market status in Pakistan and globally. "
                        f"If it's rare or upcoming, mention that. Include fun facts, legacy, and any notable records. Assume the user is a car enthusiast and wants extra value."
                    )
                    response = get_transformer_response(prompt, lang_hint='en')
                else:
                    response = f"Sorry, I couldn't find any cars matching your filters. Want to try different criteria or search another city?"
        else:
            response = "Car data isn't available right now. Please run the scraper first or try again later."
        state['step'] = 'greet'
        user_state[user_id] = state
        save_user_state()
        response = format_response_multiline(response)
        append_to_chat_history(user_id, 'bot', response)
        return response + "<br><br>Would you like to search again or do something else?"
    # Car info flow
    if state['step'] == 'car_info_query':
        car_name = state.get('car_info_name', message)
        csv_path = os.path.join('data', 'pakwheels_listings.csv')
        car_knowledge = {
            'hummer h2': "The Hummer H2 is a luxury SUV, known for its off-road capability and bold design. It's very rare in Pakistan and usually imported as a used vehicle. If you don't see any listings, it's likely not available locally at the moment.",
            # Add more car knowledge here as needed
        }
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            matches = df[df['name'].str.lower().str.contains(car_name.lower())]
            if not matches.empty:
                variants = matches['name'].unique()[:5]
                response = f"Here are some popular variants of {car_name.title()} found in listings:<br>" + '<br>'.join(variants)
            else:
                # Always provide knowledge or transformer-based info for any car
                car_lower = car_name.lower()
                if car_lower in car_knowledge:
                    response = car_knowledge[car_lower]
                elif USE_TRANSFORMER:
                    prompt = (
                        f"Give a detailed, car-enthusiast-level overview of the {car_name} (all variants, all years, including history, specs, features, and market status in Pakistan and globally. "
                        f"If it's rare or upcoming, mention that. Include fun facts, legacy, and any notable records. Assume the user is a car enthusiast and wants extra value."
                    )
                    response = get_transformer_response(prompt, lang_hint='en')
                else:
                    response = f"Sorry, I couldn't find any recent listings for {car_name.title()}. Want to try another car?"
        else:
            response = "Car data isn't available right now. Please run the scraper first or try again later."
        response += (f"<br><br>Common known issues for {car_name.title()} (for your awareness):<ul><li>Battery issues</li><li>Suspension noise</li><li>AC cooling problems</li></ul>")
        state['step'] = 'greet'
        user_state[user_id] = state
        response = format_response_multiline(response)
        append_to_chat_history(user_id, 'bot', response)
        return response + "<br><br>Would you like to ask about another car or do something else?"
# --- Flask API for chat history retrieval ---
# Add this at the bottom of the file (or wherever Flask app is defined)
try:
    from flask import Flask, jsonify, request
    app = Flask(__name__)
except ImportError:
    app = None

if app:
    @app.route('/api/chat_histories', methods=['GET'])
    def api_get_chat_histories():
        # Optionally, support ?user_id=... to get a single chat
        user_id = request.args.get('user_id')
        if user_id:
            return jsonify({user_id: get_chat_history(user_id)})
        return jsonify(get_all_chat_histories())
    @app.route('/api/chat_titles', methods=['GET'])
    def api_get_chat_titles():
        # Returns a list of chat/session IDs and a title (first user message or fallback)
        titles = []
        for user_id, history in chat_histories.items():
            # Find first user message (skip __new_session__)
            title = None
            for msg in history:
                if msg['sender'] == 'user' and msg['message'] != '__new_session__':
                    title = msg['message']
                    break
            if not title:
                title = f"Chat with {user_id}"
            titles.append({'user_id': user_id, 'title': title})
        return jsonify(titles)
    @app.route('/api/delete_chat', methods=['POST'])
    def api_delete_chat():
        data = request.get_json()
        user_id = data.get('user_id')
        if user_id and user_id in chat_histories:
            del chat_histories[user_id]
            save_chat_histories()
            # Also remove from user_state for a clean slate
            if user_id in user_state:
                del user_state[user_id]
                save_user_state()
            return jsonify({'success': True, 'message': f'Chat {user_id} deleted.'})
        return jsonify({'success': False, 'message': 'Chat not found.'}), 404
    @app.route('/api/rename_chat', methods=['POST'])
    def api_rename_chat():
        data = request.get_json()
        user_id = data.get('user_id')
        new_title = data.get('title')
        if user_id and new_title and user_id in chat_histories:
            # Store the title as a special system message at the start of the chat
            history = chat_histories[user_id]
            # Remove any previous system title
            history = [msg for msg in history if not (msg['sender'] == 'system' and msg.get('type') == 'title')]
            # Insert new title at the start
            history.insert(0, {'sender': 'system', 'type': 'title', 'message': new_title})
            chat_histories[user_id] = history
            save_chat_histories()
            return jsonify({'success': True, 'message': f'Chat {user_id} renamed.'})
        return jsonify({'success': False, 'message': 'Chat not found or invalid title.'}), 400
