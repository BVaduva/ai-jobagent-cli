import json
import re
from bs4 import BeautifulSoup
import pyperclip
import os
from curl_cffi import requests 

def get_job_description(url):
    match = re.search(r'([0-9]{7,10})-inline\.html', url)
    if match:
        job_id = match.group(1)
        url = f"https://www.stepstone.de/stellenangebote----{job_id}-inline.html"
        print(f"Link bereinigt (Job-ID: {job_id}) 🛠️")

    print("Rufe Seite ab... ⏳")
    
    try:
        response = requests.get(url, impersonate="chrome", timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Fehler: Stepstone hat mit Statuscode {response.status_code} geantwortet.")
            return
            
    except Exception as e:
        print(f"❌ Fehler: Netzwerk-Timeout oder Blockade.")
        print(f"Details: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    json_scripts = soup.find_all('script', type='application/ld+json')

    for script in json_scripts:
        try:
            if not script.string: continue
                
            data = json.loads(script.string)
            
            if isinstance(data, list):
                job_posting = next((item for item in data if item.get('@type') == 'JobPosting'), None)
            else:
                job_posting = data if data.get('@type') == 'JobPosting' else None
                
            if job_posting and 'description' in job_posting:
                raw_description = job_posting.get('description', '')
                
                clean_text = re.sub(r'<br\s*/?>|</p>', '\n', raw_description)
                clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
                clean_text = re.sub(r' {2,}', ' ', clean_text)
                clean_text = clean_text.replace('&nbsp;', ' ')
                
                title = job_posting.get('title', 'Unbekannter Titel')
                company = job_posting.get('hiringOrganization', {}).get('name', 'Unbekanntes Unternehmen')
                
                job_text = f"Titel: {title}\nUnternehmen: {company}\n\nBeschreibung:\n{clean_text.strip()}"
                
                template_path = 'prompt_template.md'
                
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as file:
                        template_content = file.read()
                    
                    final_prompt = template_content.replace('[Hier Stellenanzeige einfügen]', job_text)
                    pyperclip.copy(final_prompt)
                    
                    print(f"✅ MEGA! Job gefunden: {title} bei {company}")
                    print("Prompt ist in der ZWISCHENABLAGE. Du kannst ihn direkt einfügen (Strg+V).\n")
                else:
                    pyperclip.copy(job_text)
                    print("\n⚠️ 'prompt_template.md' fehlt. Nur Jobtext wurde kopiert.\n")
                
                return
                
        except json.JSONDecodeError:
            continue

    print("❌ Keine strukturierte Job-Beschreibung gefunden.\n")

if __name__ == "__main__":
    print("\n" + "="*40)
    print("🚀 Ultimate Jobcheck Scraper (Stealth Mode)")
    print("="*40)
    print("Tippe 'exit' ein oder drücke Strg+C zum Beenden.\n")
    
    while True:
        try:
            user_url = input("🔗 Füge den Stepstone-Link hier ein:\n> ").strip()
            
            if user_url.lower() in ['exit', 'quit', 'q']:
                print("Scraper beendet. Viel Erfolg bei der Bewerbung! 🚀\n")
                break
                
            if not user_url:
                continue
                
            get_job_description(user_url)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nScraper durch Strg+C beendet. Bis zum nächsten Mal! 👋\n")
            break
        except Exception as e:
            print(f"❌ Ein unerwarteter Fehler ist aufgetreten: {e}\n")
