import pymysql
import requests

# Configuration de la base de données
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "play_by_play",
    "charset": "utf8mb4"
}

# URL de l'API
BASE_URL = "https://esports-api.lolesports.com/persisted/gw"
HEADERS = {"x-api-key": "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z"}

def get_teams():
    url = f"{BASE_URL}/getTeams?hl=fr-FR"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", {}).get("teams", [])
    else:
        print("Erreur API:", response.status_code, response.text)
        return []

def insert_teams_and_players(teams):
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()

    # Insérer les équipes
    team_insert_query = """
    INSERT INTO team (team_id, name, abbreviation, logo_url) 
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        abbreviation = VALUES(abbreviation),
        logo_url = VALUES(logo_url);
    """
    
    # Insérer les joueurs
    player_insert_query = """
    INSERT INTO player (player_id, first_name, last_name, image_url, summoner_name, role) 
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        first_name = VALUES(first_name),
        last_name = VALUES(last_name),
        image_url = VALUES(image_url),
        summoner_name = VALUES(summoner_name),
        role = VALUES(role);
    """
    
    player_team_insert_query = """
    INSERT INTO player_team (player_id, team_id) values (%s, %s)
    ON DUPLICATE KEY UPDATE
        player_id = VALUES(player_id),
        team_id = VALUES(team_id);
    """
    
    for team in teams:
        team_id = team["id"]
        team_name = team["name"]
        team_abbreviation = team["code"]
        team_logo_url = team["image"]
        
        # Insérer l'équipe
        cursor.execute(team_insert_query, (
            team_id, team_name, team_abbreviation, team_logo_url
        ))

        # Insérer les joueurs de l'équipe
        for player in team["players"]:
            player_id = int(player["id"])
            first_name = player["firstName"]
            last_name = player["lastName"]
            image_url = player["image"]
            summoner_name = player["summonerName"]
            role = player["role"]
            
            # Insérer le joueur
            cursor.execute(player_insert_query, (
                player_id, first_name, last_name, image_url, summoner_name, role
            ))
            cursor.execute(player_team_insert_query, (
                player_id, team_id
            ))

    # Valider et fermer la connexion
    connection.commit()
    cursor.close()
    connection.close()
    print("Équipes et joueurs insérés avec succès !")

if __name__ == "__main__":
    teams = get_teams()
    for team in teams:
        print(team["id"], team["name"], team["code"])
    if teams:
        insert_teams_and_players(teams)
    else:
        print("Aucune équipe récupérée.")


