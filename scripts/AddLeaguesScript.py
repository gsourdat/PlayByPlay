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

def get_leagues():
    url = f"{BASE_URL}/getLeagues?hl=fr-FR"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", {}).get("leagues", [])
    else:
        print("Erreur API:", response.status_code, response.text)
        return []


    

def insert_leagues(leagues):
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    insert_query = """
    INSERT INTO league (league_id, name, image_url, region)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        image_url = VALUES(image_url),
        region = VALUES(region);
    """
    print(leagues)
    for league in leagues:
        cursor.execute(insert_query, (
            int(league["id"]), league["name"], league["image"], league.get("region", "Unknown")
        ))
    
    connection.commit()
    cursor.close()
    connection.close()
    print("Leagues insérées avec succès !")

if __name__ == "__main__":
    leagues = get_leagues()
    if leagues:
        insert_leagues(leagues)
    else:
        print("Aucune ligue récupérée.")
