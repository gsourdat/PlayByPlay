import requests
import time
import json

API_KEY = "4U7wGr3jRBL5Nq3_aFbAGegMFlqzsnfwIJQLc3HPBzho04dIqMI"
BASE_URL = "https://api.pandascore.co"

def get_match_status(match_id):
    url = f"{BASE_URL}/matches/{match_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("status")  # "running", "finished", etc.
    else:
        print(f"Erreur: {response.status_code} - {response.text}")
        return None

def get_match_events(match_id):
    url = f"{BASE_URL}/matches/{match_id}/events"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Liste des événements
    else:
        print(f"Erreur: {response.status_code} - {response.text}")
        return []

def listen_match_events(match_id, interval=10):
    print(f"Écoute du match {match_id} en cours...")
    
    while True:
        status = get_match_status(match_id)
        
        if status == "running":
            events = get_match_events(match_id)
            print(f"Événements en direct ({len(events)} reçus) :")
            for event in events:
                print(event)
        
        elif status == "finished":
            print("Le match est terminé.")
            break
        
        elif status is None:
            print("Impossible de récupérer le statut du match.")
            break
        
        time.sleep(interval)  # Vérifie toutes les X secondes

def get_live_match_ids():
    url = f"{BASE_URL}/matches"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"filter[status]": "running"}  # Filtrer les matchs en cours
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        matches = response.json()
        return matches
        #return [match["id"] for match in matches]  # Liste des IDs des matchs
    else:
        print(f"Erreur: {response.status_code} - {response.text}")
        return []
    
    
    
def get_live_lol_match_ids():
    url = f"{BASE_URL}/matches"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {
        "filter[status]": "running",  # Matchs en cours
        "filter[videogame_id]": "1"   # Seulement League of Legends
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        matches = response.json()
        return [match["id"] for match in matches]  # Retourne uniquement les IDs des matchs
    else:
        print(f"Erreur: {response.status_code} - {response.text}")
        return []

# Exemple d'utilisation
live_match_ids = get_live_lol_match_ids()

#print(live_match_ids)
print(json.dumps(live_match_ids, indent=4))

# Exemple d'utilisation
#match_id = 123456  # Remplace par l'ID d'un match réel
#listen_match_events(live_match_ids[0])

