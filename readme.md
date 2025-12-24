# 🚀 AI Lead Agent

A full-stack automated Sales Development Representative (SDR) agent that intelligently finds businesses, scrapes contact details, and generates personalized cold outreach emails directly into Gmail.

## ✨ Features

- **Lead Generation**: Search for businesses using keywords and location via Serper Dev API
- **Hybrid Scraping Engine**: 
  - Fast Mode using `requests` for static websites
  - Stealth Mode using `Selenium` (Headless Chrome) to bypass Cloudflare and handle JavaScript-heavy sites
  - Blocks images and ads for optimal performance
- **AI Personalization**: Analyzes lead website content to generate hyper-personalized emails using Llama 3 (via Groq)
- **Gmail Integration**: Automatically creates formatted email drafts in your Gmail inbox (OAuth2)
- **CRM Export**: Saves leads, contact information, and status to Google Sheets
- **Anti-Spam Logic**: Includes human-like delays and intelligent subject line generation for better deliverability

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python (Flask) |
| **Frontend** | HTML5, Tailwind CSS, Alpine.js |
| **Automation** | Selenium, BeautifulSoup4 |
| **AI/LLM** | Groq API (Llama-3.3-70b-versatile) |
| **APIs** | Google Gmail API, Google Sheets API, Serper Dev API |

## 📂 Project Structure

```
AI_Lead_Agent/
│
├── app.py                # Main Flask Backend Application
├── scraper.py            # Hybrid Scraping Module (Requests + Selenium)
├── requirements.txt      # Python dependencies
│
├── client_secret.json    # Google OAuth2 Credentials (for Gmail)
├── credentials.json      # Google Service Account Key (for Sheets)
│
├── config.json           # Stores API keys (Auto-generated)
├── token.json            # Stores Gmail User Token (Auto-generated)
│
└── templates/            # Frontend UI
    └── index.html
```

## ⚙️ Prerequisites & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI_Lead_Agent
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Google Cloud Configuration

#### Step 1: Set Up OAuth2 for Gmail
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Gmail API** and **Google Sheets API**
4. Create an **OAuth 2.0 Client ID** (Desktop application)
5. Download the JSON file and rename it to `client_secret.json`
6. Place `client_secret.json` in the root directory

#### Step 2: Set Up Service Account for Google Sheets
1. In Google Cloud Console, create a **Service Account**
2. Generate a JSON key for the service account
3. Rename it to `credentials.json`
4. Place `credentials.json` in the root directory
5. Share your target Google Sheet with the service account email

### 4. Obtain API Keys

You'll need the following API keys:
- **Serper Dev API Key** - For business lead search
- **Groq API Key** - For AI email generation

Store these safely; you'll enter them in the application settings.

## 🚀 How to Run

### 1. Start the Flask Server

```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
```

### 2. Access the Application

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### 3. Configure Settings

1. Click **Settings** in the top right corner
2. Enter your API keys:
   - Serper API Key
   - Groq API Key
   - Google Sheet ID (where leads will be exported)
3. Click **Save Settings**

### 4. Authenticate Gmail

1. Click **Authenticate Gmail** button
2. Follow the OAuth2 flow to authorize the application
3. Once authorized, you're ready to start generating leads and emails

### 5. Start Generating Leads

1. Enter your target **keywords** (e.g., "software development agencies")
2. Enter your **location** or leave blank for global results
3. Click **Search Leads**
4. Review the found businesses
5. Click **Generate Email** for each lead to create a personalized draft in Gmail
6. Leads are automatically exported to your Google Sheet

## 📋 Configuration File Structure

### config.json (Auto-generated)
```json
{
  "serper_api_key": "your_serper_key",
  "groq_api_key": "your_groq_key",
  "google_sheet_id": "your_sheet_id"
}
```

### token.json (Auto-generated)
Stores your Gmail OAuth2 token for authenticated API requests.

## 🔮 Future Improvements

We're actively working on expanding the capabilities of this agent:

- **Direct Email Sending**: Automate the final step to send emails immediately after generation (with user approval safeguards)
- **Service-Matched Outreach**: Enhance AI prompt engineering to dynamically match your specific service offerings to client needs discovered on their website
- **RAG Chatbot Support**: Implement Retrieval-Augmented Generation (RAG) pipeline for intelligent chatbot support, allowing natural language queries against your lead database

## ⚖️ Legal & Compliance

**Disclaimer**: This tool is for educational and legitimate business outreach purposes only.

When using this application, ensure full compliance with:
- **CAN-SPAM Act** (United States)
- **GDPR** (European Union)
- **CASL** (Canada)
- Local and regional email marketing regulations

Always obtain proper consent before sending cold emails and respect unsubscribe requests.

## 🐛 Troubleshooting

### Gmail OAuth2 Issues
- Clear your browser cookies and cache
- Delete `token.json` and re-authenticate
- Ensure Gmail API is enabled in Google Cloud Console

### Scraping Failures
- Check if the target website has robots.txt restrictions
- Try using Stealth Mode (Selenium) instead of Fast Mode
- Add a longer delay between requests in settings

### API Rate Limits
- Serper: Check your API quota
- Groq: Verify your API key and rate limits
- Gmail: Google enforces send rate limits; space out email generation

## 📞 Support & Feedback

For issues, feature requests, or contributions, please open an issue on the GitHub repository or contact the development team.

## 📄 License

[MIT]

---

**Built with ❤️ for sales and marketing automation**