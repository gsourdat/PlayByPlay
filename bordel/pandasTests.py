
API_KEY = "4U7wGr3jRBL5Nq3_aFbAGegMFlqzsnfwIJQLc3HPBzho04dIqMI"
BASE_URL = "https://api.pandascore.co/lol"


def get_lol_matches(starting_time, ending_time):
    print(starting_time)
    print(ending_time)
    #url = f"{BASE_URL}/matches?filter[match_type][0]=all_games_played&filter[status][0]=canceled&filter[videogame][0]=1&filter[winner_type][0]=Player&range[begin_at][0]={starting_time}&range[begin_at][1]={ending_time}&sort=&page=1&per_page=50"
    url = f"https://api.pandascore.co/lol/matches?range[begin_at]={starting_time},{ending_time}"

    #url += f"&range[begin_at][0]={starting_time}&range[begin_at][1]={ending_time}"
    headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
    }
    response = requests.get(url, headers=headers)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        print("nombre de matchs: " + str(len(response.json())))  # Suppose que la réponse contient une liste de matchs
        return response.json()
    else:
        return {"error": f"Erreur API: {response.status_code} - {response.text}"}


@app.route("/matchesBetween", methods=["GET"])
def matchesBetween():

    # Obtenir la date d'aujourd'hui
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Formater les heures
    start_time = f"{today}T00%3A00%3A00"
    end_time = f"{today}T23%3A59%3A59"
    starting_time = request.args.get('starting_time', default = start_time, type = str)
    ending_time = request.args.get('ending_time', default = end_time, type = str)
    print(starting_time)
    print(ending_time)
    data = get_lol_matches(starting_time, ending_time)
    return jsonify(data)


  

@app.route("/matchesStartTimes", methods=["GET"])
def matchesStartTimes():
    # Obtenir la date d'aujourd'hui
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Formater les heures
    start_time = f"{today}T00%3A00%3A00"
    end_time = f"{today}T23%3A59%3A59"
    
    # Récupérer les paramètres de requête
    starting_time = request.args.get('starting_time', default=start_time, type=str)
    ending_time = request.args.get('ending_time', default=end_time, type=str)
    
    # Obtenir les matchs
    data = get_lol_matches(starting_time, ending_time)
    
    # Extraire uniquement les horaires de début
    start_times = [match["scheduled_at"] for match in data if "id" in match]
    print(start_times)
    return jsonify(start_times)