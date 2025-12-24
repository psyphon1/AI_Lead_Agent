import os
import json
import base64
import requests
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify

# --- MODULES ---
from scraper import ContactScraper
from groq import Groq
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- GMAIL ---
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)

# --- CONFIG FILES ---
CREDENTIALS_FILE = 'credentials.json'
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'
CONFIG_FILE = 'config.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

# --- HELPERS ---
def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {"serper_api_key": "", "groq_api_key": "", "google_sheet_id": "", "my_service_description": ""}
        with open(CONFIG_FILE, 'w') as f: json.dump(default, f, indent=4)
        return default
    with open(CONFIG_FILE, 'r') as f: return json.load(f)

def save_config_file(data):
    with open(CONFIG_FILE, 'w') as f: json.dump(data, f, indent=4)

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try: creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except: os.remove(TOKEN_FILE)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE): return None
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token: token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_draft(to_email, subject, body_html):
    try:
        service = get_gmail_service()
        if not service: return "Auth Required"
        message = MIMEText(body_html, 'html')
        message['to'] = to_email
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft = service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()
        return "Draft Created ✅"
    except Exception as e: return f"Error: {str(e)[:20]}"

def generate_ai_email(company, location, context):
    config = load_config()
    if not config.get('groq_api_key'): return "Config Missing"
    
    my_offer = config.get('my_service_description', 'services')
    
    client = Groq(api_key=config['groq_api_key'])
    # NON-SPAMMY PROMPT
    prompt = f"""
    You are a professional business partner.
    My Offer: {my_offer}
    Target: {company}, {location}.
    Target Website Context: {context[:2000]}
    
    Task: Write a short HTML cold email body (no subject).
    1. Start with a specific compliment based on their website text (be genuine).
    2. Briefly mention how I can help them.
    3. Soft Call to Action (e.g., "Open to a chat?").
    
    Constraints:
    - Keep it under 80 words.
    - NO placeholder brackets like [Your Name].
    - Return ONLY HTML body (<p> tags).
    """
    try:
        chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
        return chat.choices[0].message.content
    except Exception as e: return f"AI Error: {str(e)}"

# --- ROUTES ---
@app.route('/')
def home(): return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        save_config_file(request.json)
        return jsonify({"status": "success"})
    return jsonify(load_config())

@app.route('/api/auth-gmail', methods=['POST'])
def auth_gmail():
    try:
        service = get_gmail_service()
        return jsonify({"status": "success" if service else "error"})
    except Exception as e: return jsonify({"status": "error", "message": str(e)})

@app.route('/api/search', methods=['POST'])
def search_places():
    config = load_config()
    if not config.get('serper_api_key'): return jsonify({"status": "error", "message": "API Key Missing"}), 500
    
    data = request.json
    payload = {"q": f"{data['keywords']} in {data['location']}", "num": 20}
    headers = {'X-API-KEY': config['serper_api_key'], 'Content-Type': 'application/json'}
    
    try:
        resp = requests.post("https://google.serper.dev/places", headers=headers, json=payload)
        return jsonify({"status": "success", "results": resp.json().get('places', [])})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/scrape', methods=['POST'])
def scrape_site():
    data = request.json
    url = data.get('url')
    if not url: return jsonify({"status": "skipped"})
    
    scraper = ContactScraper()
    emails, phones, text = scraper.get_contacts(url)
    
    # Just return data, do NOT draft yet
    return jsonify({
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "context": text[:3000] # Return text for AI
    })

@app.route('/api/draft', methods=['POST'])
def create_draft_endpoint():
    data = request.json
    
    if not data.get('email'): return jsonify({"status": "error", "msg": "No Email"})
    
    # Generate AI Content
    body = generate_ai_email(data.get('name'), data.get('location'), data.get('context', ''))
    
    # Human-like subject line
    subject = f"Question about {data.get('name')}"
    
    # Create Draft
    status = create_draft(data.get('email'), subject, f"<html>{body}</html>")
    
    return jsonify({"status": "success", "msg": status})

@app.route('/api/save-sheets', methods=['POST'])
def save_to_sheets():
    config = load_config()
    if not config.get('google_sheet_id'): return jsonify({"status": "error", "message": "Sheet ID Missing"}), 500
    
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(config['google_sheet_id']).sheet1
        
        vals = [[str(r.get(k, '')) for k in ['name','address','website','email','phone','draft_status']] for r in request.json['rows']]
        sheet.append_rows(vals)
        return jsonify({"status": "success"})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    load_config()
    app.run(debug=True, port=5000)