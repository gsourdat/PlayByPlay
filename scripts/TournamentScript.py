import requests
import pymysql

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

def get_tournaments(league_id):
    url = f"{BASE_URL}/getTournamentsForLeague?hl=fr-FR&leagueId={league_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        leagues_data = response.json().get("data", {}).get("leagues", [])
        if leagues_data:
            return leagues_data[0].get("tournaments", [])
    else:
        print(f"Erreur API ({league_id}):", response.status_code, response.text)
    return []

def insert_tournaments(tournaments, league_id):
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    insert_query = """
    INSERT INTO tournament (tournament_id, league_id, name, start_time, end_time)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        start_time = VALUES(start_time),
        end_time = VALUES(end_time);
    """
    
    for tournament in tournaments:
        cursor.execute(insert_query, (
            int(tournament["id"]),
            league_id,
            tournament["slug"],
            tournament["startDate"],
            tournament["endDate"]
        ))
    
    connection.commit()
    cursor.close()
    connection.close()
    print(f"Tournois pour la ligue {league_id} insérés avec succès !")

if __name__ == "__main__":
    # Récupérer les ligues existantes dans la base
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("SELECT league_id FROM league")
    leagues = cursor.fetchall()
    cursor.close()
    connection.close()
    
    for (league_id,) in leagues:
        tournaments = get_tournaments(league_id)
        if tournaments:
            insert_tournaments(tournaments, league_id)
        else:
            print(f"Aucun tournoi récupéré pour la ligue {league_id}.")
