import pymysql
import requests
import time
from datetime import datetime
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

# URL de l'API non officielle de LoLEsports
base_api_url = 'https://esports-api.lolesports.com/persisted/gw/'
api_key = '0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z'  # Clé API publique

# En-têtes de la requête
headers = {
    'x-api-key': api_key
}

# ID du LEC (League of Legends European Championship)
lec_league_id = '100695891328981122'

# 1. Récupération des matchs prévus via getSchedule
schedule_url = f"{base_api_url}getSchedule?hl=fr-FR&leagueId={lec_league_id}"
response = requests.get(schedule_url, headers=headers)

if response.status_code == 200:
    print("Connected to the API")
    data = response.json()
    events = data['data']['schedule']['events']
    for event in events:
        if event['type'] == 'match' and event['state'] == 'unstarted':
            match_id = int(event['match']['id'])
            start_time = event['startTime']
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

            match_type = 'BO' + str(event['match']['strategy']['count'])  # À ajuster si nécessaire
            if event['match']['teams'][0]['result']==None:
                score_team1 = 0
            else:
                score_team1 = event['match']['teams'][0]['result']['gameWins']
            if event['match']['teams'][1]['result']==None:
                score_team2 = 0
            else:
                score_team2 = event['match']['teams'][1]['result']['gameWins']
            status = event['state']
            tournament_id = None  # À ajuster

            # 2. Récupération des détails du match via getEventDetails
            event_details_url = f"{base_api_url}getEventDetails?hl=fr-FR&id={match_id}"
            event_response = requests.get(event_details_url, headers=headers)

            if event_response.status_code == 200:
                event_data = event_response.json()
                print(event_data)
                match_info = event_data['data']['event']['match']

                #print(json.dumps(match_info, indent=4))

                if 'teams' in match_info and len(match_info['teams']) == 2:
                    if(match_info['teams'][0]['id']=='0'):
                        team1_id = None
                    else:
                        team1_id = int(match_info['teams'][0]['id'])
                    if(match_info['teams'][1]['id']=='0'):
                        team2_id = None
                    else:
                        team2_id = int(match_info['teams'][1]['id'])
                else:
                    team1_id = None
                    team2_id = None
                if 'league' in event_data['data']['event']:
                    league_id = int(event_data['data']['event']['league']['id'])
                else:
                    league_id = None
                    # 3. Insertion des données dans la base MariaDB
                insert_query = """
                        INSERT INTO competition_match (
                            match_id, start_time, type, team1_id, team2_id,
                            score_team1, score_team2, status, tournament_id, league_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            start_time = VALUES(start_time),
                            type = VALUES(type),
                            team1_id = VALUES(team1_id),
                            team2_id = VALUES(team2_id),
                            score_team1 = VALUES(score_team1),
                            score_team2 = VALUES(score_team2),
                            status = VALUES(status),
                            tournament_id = VALUES(tournament_id),
                            league_id = VALUES(league_id)
                    """

                cursor.execute(insert_query, (
                        match_id, start_time, match_type, team1_id, team2_id,
                        score_team1, score_team2, status, tournament_id, league_id
                    ))
                
                for game in match_info['games']:
                    game_id = int(game['id'])
                    game_number = int(game['number'])
                    status = game['state']
                    team1_id = int(game['teams'][0]['id'])
                    team2_id = int(game['teams'][1]['id'])
                    if 'teams' in match_info and len(match_info['teams']) == 2:
                        if(match_info['teams'][0]['id']=='0'):
                            team1_id = None
                        else:
                            team1_id = int(match_info['teams'][0]['id'])
                        if(match_info['teams'][1]['id']=='0'):
                            team2_id = None
                        else:
                            team2_id = int(match_info['teams'][1]['id'])
                    else:
                        team1_id = None
                        team2_id = None
                    
                    insert_query = """
                        INSERT INTO game (
                            game_id, match_id, start_time, end_time, game_number,
                            team1_id, team2_id, score_team1, score_team2, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            game_id = VALUES(game_id),
                            match_id = VALUES(match_id),
                            start_time = VALUES(start_time),
                            end_time = VALUES(end_time),
                            game_number = VALUES(game_number),
                            team1_id = VALUES(team1_id),
                            team2_id = VALUES(team2_id),
                            score_team1 = VALUES(score_team1),
                            score_team2 = VALUES(score_team2),
                            status = VALUES(status)
                    """
                    cursor.execute(insert_query, (
                        game_id, match_id, None, None, game_number, team1_id, team2_id, 0, 0, status
                    ))

                print(f"Match {match_id} ajouté avec succès.")


                
                    # Pause pour éviter d'être bloqué par l'API (rate limit)
                time.sleep(1)
                
            else:
                print(f"Échec de récupération des détails du match {match_id}. Code HTTP: {event_response.status_code}")

    # Validation des transactions
    connection.commit()
    print("Tous les matchs prévus ont été ajoutés avec succès.")
else:
    print(f"Erreur lors de la récupération des matchs : {response.status_code}")

# Fermeture de la connexion à la base de données
cursor.close()
connection.close()
