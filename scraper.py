import re
import time
import requests
import urllib3
from urllib.parse import urljoin, unquote
from bs4 import BeautifulSoup

# --- SELENIUM ---
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Disable SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ContactScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
        }

    def clean_email(self, email):
        if not email: return None
        email = str(email).lower()
        email = unquote(email)
        email = email.replace(' ', '').replace('[at]', '@').replace('(at)', '@').replace('[dot]', '.')
        email = email.strip(".,;:\"'()[]{}<>|\\/-")
        
        invalid_ext = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.js', '.css', '.webp', '.woff']
        invalid_terms = ['sentry.io', 'wixpress.com', 'noreply', 'email@', 'name@', 'example.com', 'u003e']
        
        if len(email) < 5 or '@' not in email or '.' not in email: return None
        if any(email.endswith(ext) for ext in invalid_ext): return None
        if any(term in email for term in invalid_terms): return None
        return email

    def clean_phone(self, phone):
        if not phone: return None
        clean = re.sub(r'[^0-9+]', '', str(phone))
        if len(clean) < 8 or len(clean) > 15: return None
        return clean

    def extract_data(self, soup):
        emails = set()
        phones = set()
        
        # 1. Cloudflare Decode
        for cf in soup.find_all(class_="__cf_email__"):
            try:
                r = int(cf["data-cfemail"][:2], 16)
                decoded = ''.join([chr(int(cf["data-cfemail"][i:i+2], 16) ^ r) for i in range(2, len(cf["data-cfemail"]), 2)])
                cleaned = self.clean_email(decoded)
                if cleaned: emails.add(cleaned)
            except: pass

        # 2. Regex
        text = soup.get_text(separator=' ', strip=True) + " " + str(soup)
        
        for match in re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,10}', text):
            cleaned = self.clean_email(match)
            if cleaned: emails.add(cleaned)
            
        for match in re.findall(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text):
            cleaned = self.clean_phone(match)
            if cleaned: phones.add(cleaned)
            
        return emails, phones

    def _scrape_fast(self, url):
        """Requests based scraping (Fast)"""
        try:
            print(f"   ⚡ Fast Scrape: {url}")
            resp = requests.get(url, headers=self.headers, timeout=10, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')
            emails, phones = self.extract_data(soup)
            
            # Check subpages if empty
            if not emails:
                for a in soup.find_all('a', href=True):
                    if any(x in a.get_text().lower() for x in ['contact', 'about']):
                        link = urljoin(url, a['href'])
                        print(f"   🔎 Checking Subpage: {link}")
                        try:
                            sub = requests.get(link, headers=self.headers, timeout=10, verify=False)
                            e, p = self.extract_data(BeautifulSoup(sub.text, 'html.parser'))
                            emails.update(e); phones.update(p)
                            break
                        except: pass
            
            return emails, phones, soup.get_text()[:5000]
        except: return set(), set(), ""

    def _scrape_selenium(self, url):
        """Selenium based scraping (Optimized for Speed)"""
        print(f"   🐢 Selenium Scrape: {url}")
        driver = None
        emails = set()
        phones = set()
        text = ""
        
        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-extensions")
            options.add_argument("--blink-settings=imagesEnabled=false") # ⚡ BLOCK IMAGES
            options.page_load_strategy = 'eager' # ⚡ Do not wait for full load
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Set a hard limit for page loading (5 seconds max)
            driver.set_page_load_timeout(5)
            
            try: driver.get(url)
            except: 
                # If timeout, we still try to scrape what loaded
                driver.execute_script("window.stop();")
            
            # Reduced sleep time
            time.sleep(1) 
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            emails, phones = self.extract_data(soup)
            text = soup.get_text()[:5000]
            
        except Exception as e: print(f"Selenium Error: {e}")
        finally: 
            if driver: driver.quit()
            
        return emails, phones, text
    def get_contacts(self, url):
        if not url.startswith('http'): url = 'http://' + url
        
        # Try Fast
        emails, phones, text = self._scrape_fast(url)
        
        # Try Slow if no emails
        if not emails:
            e_slow, p_slow, t_slow = self._scrape_selenium(url)
            emails.update(e_slow)
            phones.update(p_slow)
            if not text: text = t_slow
            
        return list(emails), list(phones), text