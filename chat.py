import json
import urllib.request
import os
from scrape import get_job_description

# ANSI-Colorcodes for terminal
COLOR_USER = '\033[94m'  # Blue
COLOR_AI = '\033[92m'    # Green
COLOR_RESET = '\033[0m' 

# Local Ollama API
URL = "http://localhost:11434/api/chat"
# IMPORTANT: Exact name of the created model
MODEL_NAME = "jobagent" 

# Permanent mind
system_messages = []
profile_path = "masterprofile.md"

# Inject Masterprofil
if os.path.exists(profile_path):
    with open(profile_path, "r", encoding="utf-8") as f:
        profile_text = f.read()

    injection = f"Hier ist mein aktuelles Masterprofil als Hintergrundwissen. Nutze diese Fakten ab sofort für alle Jobchecks:\n\n{profile_text}"
    system_messages.append({"role": "system", "content": injection})
    print(f"{COLOR_AI}✅  Masterprofil ({len(profile_text)} Zeichen) erfolgreich ins Gedächtnis geladen.{COLOR_RESET}")
else:
    print(f"{COLOR_USER}⚠️ Warnung: Keine '{profile_path}' gefunden. Chatte ohne Profil-Kontext.{COLOR_RESET}")

print(f"{COLOR_AI}--- JobAgent Chat ('exit' to quit) ---{COLOR_RESET}")

while True:
    user_input = input(f"\n{COLOR_USER}You: {COLOR_RESET}")
    
    if user_input.lower() == 'exit':
        break

    # Copy system message for the current check
    current_messages = system_messages.copy()

    if user_input.lower().startswith("/check "):
        url = user_input[7:].strip()
        print(f"{COLOR_AI} Lade Scraper...{COLOR_RESET}")
        
        job_description = get_job_description(url)
        
        if job_description:
            user_input = job_description
            print(f"{COLOR_AI}✅  Job-Daten an Agent übergeben. Analyse läuft...{COLOR_RESET}")
        else:
            print(f"{COLOR_USER}⚠️ Fehler: Der Scraper konnte keine Daten finden.{COLOR_RESET}")
            continue

    current_messages.append({"role": "user", "content": user_input})
    data = {
        "model": MODEL_NAME,
        "messages": current_messages,
        "stream": True  # Dont wait for full respons
    }
    
    req = urllib.request.Request(URL, data=json.dumps(data).encode('utf-8'))
    
    print(f"{COLOR_USER}Agent: {COLOR_RESET}", end="", flush=True)
    full_response = ""
    
    try:
        # Call API for response
        with urllib.request.urlopen(req) as response:
            for line in response:
                if line:
                    chunk = json.loads(line)
                    content = chunk['message']['content']
                    # Coloring response
                    print(f"{COLOR_AI}{content}{COLOR_RESET}", end="", flush=True)
                    full_response += content
        
        print() # New line
        
    except Exception as e:
        print(f"\nError while connecting to Ollama: {e}")