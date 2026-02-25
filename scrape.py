import json
import re
import requests
from bs4 import BeautifulSoup
import os

def get_job_description(url):
    print(f"Rufe Seite ab...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"⚠ Fehler beim Abrufen der Seite: {e}")
        return None

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
                
                jobcheck_path = 'jobcheck_prompt.md'
                
                if os.path.exists(jobcheck_path):
                    with open(jobcheck_path, 'r', encoding='utf-8') as file:
                        template_content = file.read()
                    
                    final_prompt = template_content.replace('[Hier Stellenanzeige einfügen]', job_text)
                    print(f"✅ Job gefunden: {title} bei {company}")
                    return final_prompt
                else:
                    print(f"✅ Job gefunden: {title} bei {company}")
                    print("⚠️ 'jobcheck_prompt.md' fehlt. Gebe nur rohen Jobtext an KI weiter.")
                    return job_text
                
        except json.JSONDecodeError:
            continue

    print("❌ Keine strukturierte Job-Beschreibung gefunden.\n")
    return None

if __name__ == "__main__":
    print("\n" + "="*40)
    print("Jobcheck Scraper (Loop Mode)")
    print("="*40)
    print("Tippe 'exit' ein oder drücke Strg+C zum Beenden.\n")
    
    while True:
        try:
            user_url = input("🔗 Füge den Stepstone-Link hier ein (ohne Anführungszeichen!):\n> ").strip()
            
            if user_url.lower() in ['exit', 'quit', 'q']:
                print("Scraper beendet. Viel Erfolg bei der Bewerbung! \n")
                break
                
            if not user_url:
                continue
                
            get_job_description(user_url)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nScraper durch Strg+C beendet. Bis zum nächsten Mal! \n")
            break
        except Exception as e:
            print(f"❌ Ein unerwarteter Fehler ist aufgetreten: {e}\n")
