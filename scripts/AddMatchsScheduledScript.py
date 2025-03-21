import pymysql
import requests
import json

# Informations de connexion à la base de données
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'play_by_play'
}

# Connexion à la base de données
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

# URL de l'API non officielle de LoLEsports pour récupérer le calendrier

api_url = 'https://esports-api.lolesports.com/persisted/gw/getSchedule?leagueId=98767991302996019'  # ID du LEC
api_key = '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'  # Clé API publique

BASE_URL = "https://esports-api.lolesports.com/persisted/gw"
HEADERS = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}
url = f"{BASE_URL}/getSchedule?hl=fr-FR&leagueId=100695891328981122&pageToken=10"

response = requests.get(url, headers=HEADERS)

# Vérification du statut de la réponse
if response.status_code == 200:
    data = response.json()
    events = data['data']['schedule']['events']

    for event in events:
        print(json.dumps(event, indent=4))

        print(f"Équipe 1 : {event['match']['teams'][0]['name']}, Équipe 2 : {event['match']['teams'][1]['name']}, Date : {event['startTime']}" )
        if event['type'] == 'match': #and event['state'] == 'unstarted':
            start_time = event['startTime']
            end_time = None  # L'heure de fin peut être estimée ou laissée nulle
            match_type = 'BO1'  # Par défaut, les matchs du LEC sont en Best of 1
            team1_id = event['match']['teams'][0]['id']
            team2_id = event['match']['teams'][1]['id']
            score_team1 = 0
            score_team2 = 0
            status = 'scheduled'
            tournament_id = 1  # À adapter selon votre schéma de base de données
            league_id = 1  # À adapter selon votre schéma de base de données

            # Requête SQL pour insérer les données dans la table competition_match
            insert_query = """
                INSERT INTO competition_match (
                    start_time, end_time, type, team1_id, team2_id,
                    score_team1, score_team2, status, tournament_id, league_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(insert_query, (
                start_time, end_time, match_type, team1_id, team2_id,
                score_team1, score_team2, status, tournament_id, league_id
            ))

    # Validation des transactions
    connection.commit()
    print("Les matchs prévus ont été ajoutés avec succès à la base de données.")
else:
    print(f"Erreur lors de la récupération des données : {response.status_code}")

# Fermeture de la connexion à la base de données
cursor.close()
connection.close()
