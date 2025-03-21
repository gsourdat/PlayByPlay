from flask import Flask, jsonify, request
import requests
from datetime import date
from datetime import datetime
from flask_cors import CORS  # Importer Flask-CORS
import json
import mysql.connector
from flask_socketio import SocketIO
import time
import threading
from flask_socketio import SocketIO, emit
import random
from flask import render_template, jsonify
from main import main


import ssl
print(ssl.OPENSSL_VERSION)


app = Flask(__name__)
app.register_blueprint(main)

CORS(app)  # Autoriser les requêtes cross-origin
socketio = SocketIO(app, cors_allowed_origins="*")  # Initialiser SocketIO avec CORS autorisé

# Configuration de la base de données
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "play_by_play"
}


def get_db_connection():
    """ Établit une connexion avec la base de données. """
    return mysql.connector.connect(**DB_CONFIG)


def get_matches_between(starting_time, ending_time):
    """ Récupère les matchs entre deux dates depuis la BDD. """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT cm.match_id, cm.start_time, cm.status, 
            t1.name AS team1_name, t1.logo_url AS team1_logo,
            t2.name AS team2_name, t2.logo_url AS team2_logo,
            l.name AS league_name, l.image_url AS league_logo,
            cm.score_team1, cm.score_team2
        FROM competition_match cm
        LEFT JOIN team t1 ON cm.team1_id = t1.team_id
        LEFT JOIN team t2 ON cm.team2_id = t2.team_id
        LEFT JOIN league l ON cm.league_id = l.league_id
        WHERE cm.start_time BETWEEN %s AND %s
        ORDER BY cm.start_time ASC;
    """
    
    cursor.execute(query, (starting_time, ending_time))
    matches = cursor.fetchall()
    for match in matches:
        match["match_id"] = str(match["match_id"])  # Convertit en string pour éviter la perte de précision
    
    
    conn.close()
    return matches

def get_match_detail_opsolete(match_id):
    """ Récupère les détails d'un match depuis la BDD. """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT cm.match_id, cm.start_time, cm.status, 
               t1.name AS team1_name, t1.logo_url AS team1_logo,
               t2.name AS team2_name, t2.logo_url AS team2_logo,
               l.name AS league_name, l.image_url AS league_logo,
               cm.score_team1, cm.score_team2
        FROM competition_match cm
        JOIN team t1 ON cm.team1_id = t1.team_id
        JOIN team t2 ON cm.team2_id = t2.team_id
        JOIN league l ON cm.league_id = l.league_id
        WHERE cm.match_id = %s;
    """
    

    
    cursor.execute(query, (match_id,))  # Ajout de la virgule pour créer un tuple
    match = cursor.fetchone()  # fetchone() pour récupérer un seul match
    print(match)
    conn.close()
    return match  # Retourne un dictionnaire au lieu d'une liste de dictionnaires


def get_match_detail(match_id):
    """ Récupère les détails d'un match depuis la BDD. """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Récupérer les détails du match
    query = """
        SELECT cm.match_id, cm.start_time, cm.status,t1.team_id AS team1_id,  
               t1.name AS team1_name, t1.logo_url AS team1_logo, t2.team_id AS team2_id,
               t2.name AS team2_name, t2.logo_url AS team2_logo,
               l.name AS league_name, l.image_url AS league_logo,
               cm.score_team1, cm.score_team2
        FROM competition_match cm
        LEFT JOIN team t1 ON cm.team1_id = t1.team_id
        LEFT JOIN team t2 ON cm.team2_id = t2.team_id
        LEFT JOIN league l ON cm.league_id = l.league_id
        WHERE cm.match_id = %s;
    """
    cursor.execute(query, (match_id,))
    match = cursor.fetchone()

    if not match:
        conn.close()
        return None

    # Récupérer la composition des équipes
    def get_team_players(team_id):
        print(team_id)
        player_query = """
      
            SELECT team.team_id, team.name, player.player_id, player.first_name, player.last_name, player.image_url, player.summoner_name, player.role
            FROM team LEFT JOIN player_team ON team.team_id = player_team.team_id LEFT JOIN player ON player_team.player_id = player.player_id
            WHERE team.team_id = %s ORDER BY FIELD(player.role, 'top', 'jungle', 'mid', 'bottom', 'support', 'none');
        """
        cursor.execute(player_query, (team_id,))
        return cursor.fetchall()
    
    team1_players = get_team_players(match['team1_id'])
    print(team1_players)
    team2_players = get_team_players(match['team2_id'])

    conn.close()

    # Construire le JSON de réponse
    match_detail = {
        "team1_name": match["team1_name"],
        "team2_name": match["team2_name"],
        "status": match["status"],
        "start_time": match["start_time"],
        "score_team1": match["score_team1"],
        "score_team2": match["score_team2"],
        "team1_logo": match["team1_logo"],
        "team2_logo": match["team2_logo"],
        "league_name": match["league_name"],
        "league_logo": match["league_logo"],
        "team1_players": [
            {
                "name": f"{player['first_name']} {player['last_name']}",
                "photo": player["image_url"],
                "summoner_name": player["summoner_name"],
                "role": player["role"]
            } for player in team1_players
        ],
        "team2_players": [
            {
                "name": f"{player['first_name']} {player['last_name']}",
                "photo": player["image_url"],
                "summoner_name": player["summoner_name"],
                "role": player["role"]
            } for player in team2_players
        ]
    }
    print(match_detail)
    return match_detail

@app.route("/matchesBetween", methods=["GET"])
def matches_between2():
    """ Endpoint pour récupérer les matchs entre deux dates. """
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Récupération des paramètres ou valeurs par défaut
    starting_time = request.args.get('starting_time', default=f"{today} 00:00:00", type=str)
    ending_time = request.args.get('ending_time', default=f"{today} 23:59:59", type=str)
    print("Date :  " + str(starting_time))

    data = get_matches_between(starting_time, ending_time)
    
    return jsonify(data)


@app.route("/matchesStartTimes", methods=["GET"])
def matches_start_times2():
    """ Endpoint pour récupérer uniquement les horaires de début des matchs. """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    starting_time = request.args.get('starting_time', default=f"{today} 00:00:00", type=str)
    ending_time = request.args.get('ending_time', default=f"{today} 23:59:59", type=str)

    matches = get_matches_between(starting_time, ending_time)
    start_times = [match["start_time"] for match in matches]
    
    return jsonify(start_times)
""

@app.route("/matchDetail", methods=["GET"])
def match_detail():
    """ Endpoint pour récupérer les détails d'un match. """
    match_id = request.args.get('id', default=None, type=int)
    if match_id is None:
        return jsonify({"error": "Paramètre 'match_id' manquant."})
    
    match = get_match_detail(int(match_id))
    if not match:
        return jsonify({"error": "Match non trouvé."}), 404

    return jsonify(match)


def add_match(team1_id, team2_id, league_id, score_team1, score_team2):
    """ Ajoute un match à la base de données avec la date du jour. """
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    query = """
        INSERT INTO competition_match (match_id, team1_id, team2_id, league_id, start_time, score_team1, score_team2, status, type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(query, (random.getrandbits(16), int(team1_id), int(team2_id), int(league_id), today, score_team1, score_team2, 'unstarted', 'BO3'))
    conn.commit()
    conn.close()

    # Émettre un événement SocketIO pour mettre à jour les matchs du jour
    socketio.emit('update_matches', {'message': 'Nouveau match ajouté'})

    return {"message": "Match ajouté avec succès"}

@app.route("/addMatch", methods=["POST"])
def add_match_endpoint():
    """ Endpoint pour ajouter un match à la base de données. """
    data = request.json
    team1_id = data.get('team1_id')
    team2_id = data.get('team2_id')
    league_id = data.get('league_id')
    score_team1 = data.get('score_team1', 0)
    score_team2 = data.get('score_team2', 0)

    if not team1_id or not team2_id or not league_id:
        return jsonify({"error": "Paramètres manquants"}), 400
    print("data : ")
    print(data)
    result = add_match(team1_id, team2_id, league_id, score_team1, score_team2)
    return jsonify(result)


@app.route("/teams", methods=["GET"])
def get_teams():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT team_id, name FROM team")
    teams = cursor.fetchall()
    conn.close()
    for team in teams:
        team["team_id"] = str(team["team_id"])  # Convertit en string pour éviter la perte de précision
    return jsonify(teams)

@app.route("/leagues", methods=["GET"])
def get_leagues():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT league_id, name FROM league")
    leagues = cursor.fetchall()
    conn.close()
    for league in leagues:
        league["league_id"] = str(league["league_id"])  # Convertit en string pour éviter la perte de précision
    return jsonify(leagues)

@app.route('/champions', methods=['GET'])
def get_champions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Utilisation de dictionary=True pour récupérer les résultats sous forme de dictionnaires
    cursor.execute('SELECT id, photo FROM champions')
    champions = cursor.fetchall()
    conn.close()
    return jsonify(champions)

@app.route("/matchGames", methods=["GET"])
def match_games():
    """ Endpoint pour récupérer les games d'un match avec les détails des équipes et des joueurs. """
    match_id = request.args.get('match_id', default=None, type=int)
    if match_id is None:
        return jsonify({"error": "Paramètre 'match_id' manquant."})

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Récupérer les games du match
    query = """
        SELECT g.game_id, g.game_number, g.start_time, g.end_time, g.score_team1, g.score_team2, g.status,
               t1.team_id AS team1_id, t1.name AS team1_name, t1.logo_url AS team1_logo,
               t2.team_id AS team2_id, t2.name AS team2_name, t2.logo_url AS team2_logo
        FROM game g
        LEFT JOIN team t1 ON g.team1_id = t1.team_id
        LEFT JOIN team t2 ON g.team2_id = t2.team_id
        WHERE g.match_id = %s
        ORDER BY g.game_number ASC;
    """
    cursor.execute(query, (match_id,))
    games = cursor.fetchall()

    # Récupérer les joueurs et leurs stats pour chaque game
    for game in games:
        game_id = game['game_id']
        
        def get_team_players(team_id):
            player_query = """
            SELECT p.player_id, p.first_name, p.last_name, p.image_url, p.summoner_name, p.role,
                pgs.champion, pt.team_id
            FROM player p
            JOIN player_game_stat pgs ON p.player_id = pgs.player_id AND pgs.game_id = %s
            LEFT JOIN player_team pt ON p.player_id = pt.player_id
            WHERE pt.team_id = %s ORDER BY FIELD(p.role, 'top', 'jungle', 'mid', 'bottom', 'support', 'none');
            """
            cursor.execute(player_query, (game_id, team_id))
            return cursor.fetchall()
        
        team1_players = get_team_players(game['team1_id'])
        team2_players = get_team_players(game['team2_id'])
        # Séparer les joueurs par équipe
        #team1_players = [player for player in players if player['team_id'] == game['team1_id']]
        #team2_players = [player for player in players if player['team_id'] == game['team2_id']]
        
        game['team1_players'] = team1_players
        game['team2_players'] = team2_players
    print(json.dumps(games, indent=4))

    conn.close()
    return jsonify(games)


@app.route("/matchGames2", methods=["GET"])
def match_games2():
    """ Endpoint pour récupérer les games d'un match. """
    match_id = request.args.get('match_id', default=None, type=int)
    if match_id is None:
        return jsonify({"error": "Paramètre 'match_id' manquant."})

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT game_id, game_number, start_time, end_time, score_team1, score_team2, status
        FROM game
        WHERE match_id = %s
        ORDER BY game_number ASC;
    """
    cursor.execute(query, (match_id,))
    games = cursor.fetchall()
    conn.close()

    return jsonify(games)


if __name__ == "__main__":
    socketio.run(app, debug=True)





