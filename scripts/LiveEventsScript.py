from datetime import datetime, timezone
from collections import Counter
import requests
import time
import json
from datetime import datetime, timezone, timedelta


API_KEY = "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"  # Remplacez par votre clé API Riot Games
BASE_URL = "https://esports-api.lolesports.com/persisted/gw"
HEADERS = {"x-api-key": API_KEY}


def detect_events(prev_state, curr_state, game_id, match_id, starting_time):
    events = []
    timer = curr_state["rfc460Timestamp"]  # Timestamp actuel
    
    # Vérifier les kills par joueur
    for team_color in ["blueTeam", "redTeam"]:
        prev_team = prev_state[team_color]
        curr_team = curr_state[team_color]

        for prev_player, curr_player in zip(prev_team["participants"], curr_team["participants"]):
            if curr_player["kills"] > prev_player["kills"]:
                event = {
                    "timer": timer,
                    "type": "kill",
                    "team_id": team_color,
                    "player_id": curr_player["participantId"],
                    "opponent_team_id": "redTeam" if team_color == "blueTeam" else "blueTeam",
                    "opponent_player_id": None,  # On ne peut pas directement savoir qui est mort
                    "game_id": game_id,
                    "match_id": match_id    
                }
                events.append(event)

    # Vérifier les kills totaux pour estimer qui a subi la mort
    prev_kills = prev_state["blueTeam"]["totalKills"], prev_state["redTeam"]["totalKills"]
    curr_kills = curr_state["blueTeam"]["totalKills"], curr_state["redTeam"]["totalKills"]

    if curr_kills[0] > prev_kills[0]:# Blue a fait un kill
        events[-1]["opponent_team_id"] = "redTeam"
    elif curr_kills[1] > prev_kills[1]:  # Red a fait un kill
        events[-1]["opponent_team_id"] = "blueTeam"

    # Vérifier les tours tombées
    for team_color in ["blueTeam", "redTeam"]:
        prev_towers = prev_state[team_color]["towers"]
        curr_towers = curr_state[team_color]["towers"]
        if curr_towers < prev_towers:
            events.append({
                "timer": timer,
                "type": "tower_fall",
                "team_id": "redTeam" if team_color == "blueTeam" else "blueTeam",
                "player_id": None,
                "opponent_team_id": team_color,
                "opponent_player_id": None,
                "game_id": game_id,
                "match_id": match_id
            })

    # Vérifier les inhibiteurs tombés
    for team_color in ["blueTeam", "redTeam"]:
        prev_inhibitors = prev_state[team_color]["inhibitors"]
        curr_inhibitors = curr_state[team_color]["inhibitors"]
        if curr_inhibitors < prev_inhibitors:
            events.append({
                "timer": timer,
                "type": "inhibitor_fall",
                "team_id": "redTeam" if team_color == "blueTeam" else "blueTeam",
                "player_id": None,
                "opponent_team_id": team_color,
                "opponent_player_id": None,
                "game_id": game_id,
                "match_id": match_id
            })

    # Vérifier les barons tués
    for team_color in ["blueTeam", "redTeam"]:
        prev_barons = prev_state[team_color]["barons"]
        curr_barons = curr_state[team_color]["barons"]
        if curr_barons > prev_barons:
            events.append({
                "timer": timer,
                "type": "baron",
                "team_id": team_color,
                "player_id": None,
                "opponent_team_id": None,
                "opponent_player_id": None,
                "game_id": game_id,
                "match_id": match_id
            })

    # Vérifier les dragons tués
    for team_color in ["blueTeam", "redTeam"]:
        prev_count = Counter(prev_state[team_color]["dragons"])
        curr_count = Counter(curr_state[team_color]["dragons"])
    
        new_dragons = []
    
        for dragon, count in curr_count.items():
            if count > prev_count.get(dragon, 0):  # Vérifie s'il y a plus d'occurrences dans curr
                new_dragons.append(dragon)
        #prev_dragons = set(prev_state[team_color]["dragons"])
        #curr_dragons = set(curr_state[team_color]["dragons"])
        #new_dragons = list(curr_dragons - prev_dragons)
        for dragon in new_dragons:
            events.append({
                "timer": timer,
                "type": dragon + " drake",
                "team_id": team_color,
                "player_id": None,
                "opponent_team_id": None,
                "opponent_player_id": None,
                "game_id": game_id,
                "match_id": match_id
            })
            
    if(curr_state["gameState"]=='finished' and curr_state["rfc460Timestamp"].replace(microsecond=0)):
        events.append({
                "timer": timer,
                "type": "Game ended",
                "team_id": None,
                "player_id": None,
                "opponent_team_id": None,
                "opponent_player_id": None,
                "game_id": game_id,
                "match_id": match_id
            })

    return events



def get_valid_timestamp():
    now = datetime.now(timezone.utc)
    rounded_seconds = now.second - (now.second % 10)  # Arrondi au multiple de 10
    valid_time = now.replace(second=rounded_seconds, microsecond=0)  # Supprime les millisecondes
    
    # Appliquer un décalage de 20 secondes dans le passé
    valid_time -= timedelta(seconds=30)
    
    return valid_time.strftime("%Y-%m-%dT%H:%M:%S.00Z")  # Format ISO avec .00Z




def get_live_events():
    url = f"{BASE_URL}/getLive?hl=fr-FR"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return None

def extract_match_info(live_data):
    if not live_data or "data" not in live_data or "schedule" not in live_data["data"]:
        print("Aucune donnée de match en direct trouvée.")
        return
    idMatchTab = []
    idGameTab = []
    events = live_data["data"]["schedule"]["events"]
    for event in events:
        if event.get("state") == "inProgress":
            
            if "match" not in event:
                continue
            #print("event :")
            #print(json.dumps(event, indent=4))
            match_id = event["match"]["id"]
            idMatchTab.append(match_id)
            teams = event["match"]["teams"]
            blue_team = teams[0]["name"]
            red_team = teams[1]["name"]
            #print(f"Match en cours: {blue_team} vs {red_team} (ID: {match_id})")
            games = event["match"]["games"]
            for game in games:
                if game.get("state") == "inProgress":
                    idGameTab.append(game["id"])

                

    return idMatchTab, idGameTab


def get_window(game_id, starting_time=None):
    url = f"https://feed.lolesports.com/livestats/v1/window/{game_id}"
    
    if starting_time:
        url += f"?startingTime={starting_time}"
    
    
    response = requests.get(url, headers=HEADERS)
    
    # Vérifier si le statut HTTP est OK avant de traiter la réponse
    if response.status_code != 200:
        print("pb get_window")
        print(f"Erreur HTTP: {response.status_code}")
        print(response.text)
        return None
    
    # Si la réponse est correcte, tenter de la convertir en JSON
    try:
        return response.json(), starting_time
    except ValueError as e:
        print(f"Erreur lors de la conversion en JSON: {e}")
        return None

def ajouter_metadonnees(data):
    # Extraction des métadonnées
    blue_team_metadata = data['gameMetadata']['blueTeamMetadata']
    red_team_metadata = data['gameMetadata']['redTeamMetadata']
    esports_game_id = data['esportsGameId']
    esports_match_id = data['esportsMatchId']
    
    # Parcours de chaque frame pour ajouter les métadonnées
    for frame in data['frames']:
        # Ajout des métadonnées de l'équipe bleue
        frame['esportsGameId'] = esports_game_id
        frame['esportsMatchId'] = esports_match_id
        
        for participant in frame['blueTeam']['participants']:
            for blue_participant in blue_team_metadata['participantMetadata']:
                if blue_participant['participantId'] == participant['participantId']:
                    # Intégrer directement les données dans le participant
                    participant.update(blue_participant)
        frame['blueTeam']['esportsTeamId'] = blue_team_metadata['esportsTeamId']
        
        # Ajout des métadonnées de l'équipe rouge
        for participant in frame['redTeam']['participants']:
            for red_participant in red_team_metadata['participantMetadata']:
                if red_participant['participantId'] == participant['participantId']:
                    # Intégrer directement les données dans le participant
                    participant.update(red_participant)
        frame['redTeam']['esportsTeamId'] = red_team_metadata['esportsTeamId']
    
    return data

# Exemple d'utilisation avec les données que tu as fournies
data = {
    'esportsGameId': '113990327983174559',
    'esportsMatchId': '113990327983174555',
    'gameMetadata': {
        'patchVersion': '15.5.662.5311',
        'blueTeamMetadata': {
            'esportsTeamId': '105515219038427019',
            'participantMetadata': [
                {'participantId': 1, 'esportsPlayerId': '105700869624784693', 'summonerName': 'KCB Maynter', 'championId': 'Renekton', 'role': 'top'},
                {'participantId': 2, 'esportsPlayerId': '107464179845128878', 'summonerName': 'KCB ISMA', 'championId': 'Nocturne', 'role': 'jungle'},
                {'participantId': 3, 'esportsPlayerId': '106302003665923326', 'summonerName': 'KCB SlowQ', 'championId': 'Akali', 'role': 'mid'},
                {'participantId': 4, 'esportsPlayerId': '113741971222479798', 'summonerName': 'KCB 3XA', 'championId': 'Aphelios', 'role': 'bottom'},
                {'participantId': 5, 'esportsPlayerId': '109710705987430108', 'summonerName': 'KCB Nsurr', 'championId': 'Karma', 'role': 'support'}
            ]
        },
        'redTeamMetadata': {
            'esportsTeamId': '107128093558481418',
            'participantMetadata': [
                {'participantId': 6, 'esportsPlayerId': '110467144044264674', 'summonerName': 'ZNT Whip', 'championId': 'Garen', 'role': 'top'},
                {'participantId': 7, 'esportsPlayerId': '107693484400882014', 'summonerName': 'ZNT shibi', 'championId': 'Sejuani', 'role': 'jungle'},
                {'participantId': 8, 'esportsPlayerId': '109146898089227862', 'summonerName': 'ZNT Marty', 'championId': 'Neeko', 'role': 'mid'},
                {'participantId': 9, 'esportsPlayerId': '112458338268604979', 'summonerName': 'ZNT Afriibi', 'championId': 'Draven', 'role': 'bottom'},
                {'participantId': 10, 'esportsPlayerId': '110494684110133175', 'summonerName': 'ZNT J3rkie', 'championId': 'Renata', 'role': 'support'}
            ]
        }
    },
    'frames': [
        {'rfc460Timestamp': '2025-03-20T19:07:39.834Z', 'gameState': 'in_game', 'blueTeam': {'totalGold': 53699, 'inhibitors': 1, 'towers': 10, 'barons': 0, 'totalKills': 30, 'dragons': ['mountain', 'chemtech'], 'participants': [{'participantId': 1, 'totalGold': 11869, 'level': 16, 'kills': 4, 'deaths': 0, 'assists': 4, 'creepScore': 233, 'currentHealth': 2383, 'maxHealth': 3893}, {'participantId': 2, 'totalGold': 11326, 'level': 14, 'kills': 12, 'deaths': 1, 'assists': 10, 'creepScore': 147, 'currentHealth': 0, 'maxHealth': 2962}, {'participantId': 3, 'totalGold': 10461, 'level': 15, 'kills': 7, 'deaths': 1, 'assists': 7, 'creepScore': 204, 'currentHealth': 1725, 'maxHealth': 2844}, {'participantId': 4, 'totalGold': 12850, 'level': 15, 'kills': 7, 'deaths': 0, 'assists': 16, 'creepScore': 231, 'currentHealth': 2183, 'maxHealth': 2183}, {'participantId': 5, 'totalGold': 7193, 'level': 12, 'kills': 0, 'deaths': 1, 'assists': 26, 'creepScore': 19, 'currentHealth': 1595, 'maxHealth': 2368}]}, 'redTeam': {'totalGold': 36302, 'inhibitors': 0, 'towers': 1, 'barons': 0, 'totalKills': 3, 'dragons': ['cloud'], 'participants': [{'participantId': 6, 'totalGold': 9820, 'level': 14, 'kills': 2, 'deaths': 4, 'assists': 1, 'creepScore': 195, 'currentHealth': 0, 'maxHealth': 2770}, {'participantId': 7, 'totalGold': 6562, 'level': 12, 'kills': 0, 'deaths': 4, 'assists': 2, 'creepScore': 130, 'currentHealth': 0, 'maxHealth': 3639}, {'participantId': 8, 'totalGold': 7519, 'level': 12, 'kills': 1, 'deaths': 7, 'assists': 1, 'creepScore': 156, 'currentHealth': 611, 'maxHealth': 2188}, {'participantId': 9, 'totalGold': 7135, 'level': 12, 'kills': 0, 'deaths': 8, 'assists': 2, 'creepScore': 168, 'currentHealth': 1479, 'maxHealth': 1843}, {'participantId': 10, 'totalGold': 5266, 'level': 10, 'kills': 0, 'deaths': 7, 'assists': 2, 'creepScore': 23, 'currentHealth': 630, 'maxHealth': 1976}]}}
    ]
}

#data_avec_metadonnees = ajouter_metadonnees(get_window(113990327983174559,get_valid_timestamp()))


#print(json.dumps(data_avec_metadonnees["frames"][0]["redTeam"], indent=4))


import time

def main():
    interval = 10  # Intervalle en secondes
    next_run = time.time()

    while True:
        live_data = get_live_events()
        a, b = extract_match_info(live_data)

        for bb in b:
            tmp, st = get_window(bb, get_valid_timestamp())
            if tmp is not None:
                tmp = ajouter_metadonnees(tmp)
                for i in range(len(tmp["frames"]) - 1):
                    event = detect_events(tmp["frames"][i], tmp["frames"][i+1], 123, 123, st)
                    if event:
                        print(event)

        # Attendre jusqu'à la prochaine itération
        next_run += interval
        time.sleep(max(0, next_run - time.time()))


if __name__ == "__main__":
    main()
