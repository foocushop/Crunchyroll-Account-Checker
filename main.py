import os
import threading
from flask import Flask

app = Flask(__name__)

# Ta logique de checking (simplifiée ici)
def run_checker():
    print("Démarrage du Crunchyroll Checker...")
    # Ici, insère le code original du repo pour le checking
    # Attention : sans proxies, Railway sera banni très vite.
    pass

@app.route('/')
def home():
    return "Checker is running!"

if __name__ == "__main__":
    # On lance le checker dans un thread séparé pour ne pas bloquer le serveur web
    threading.Thread(target=run_checker).start()
    
    # Railway injecte automatiquement la variable PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
