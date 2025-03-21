# Matchs League of Legends

## Description
Ce projet est une application web permettant de visualiser les matchs de League of Legends. Les utilisateurs peuvent consulter les matchs programmés, les détails des matchs, ainsi que les compositions des équipes.

## Structure du Projet
```
├── .gitignore
├── appPLaybPlay.py
├── main.py
├── bordel/
│   ├── db.txt
│   ├── main.html
│   ├── pandasTests.py
│   ├── play.py
│   ├── script2.js
├── scripts/
│   ├── AddChampsScript.py
│   ├── AddLeaguesScript.py
│   ├── AddMatchsScheduledForLeagueScript.py
│   ├── AddMatchsScheduledScript.py
│   ├── AddTeamsPlayersScript.py
│   ├── TournamentScript.py
├── static/
│   ├── css/
│   │   ├── base.css
│   │   ├── match.css
│   │   ├── styles.css
│   │   ├── fonts/
│   │       ├── Rajdhani-Bold.ttf
│   │       ├── Rajdhani-Light.ttf
│   │       ├── Rajdhani-Medium.ttf
│   │       ├── Rajdhani-Regular.ttf
│   │       ├── Rajdhani-SemiBold.ttf
│   │       ├── OFL.txt
│   ├── images/
│   │   ├── bottom.png
│   │   ├── bottom.webp
│   │   ├── eyeBarre.png
│   │   ├── jungle.png
│   ├── js/
│       ├── app.js
│       ├── match.js
│       ├── script2.js
├── templates/
│   ├── app.html
│   ├── base.html
│   ├── champions.html
│   ├── match.html
```

## Installation

1. Clonez le dépôt :
    ```sh
    git clone <URL_DU_DEPOT>
    cd playbyplay
    ```

2. Créez un environnement virtuel et activez-le :
    ```sh
    python -m venv venv
    source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
    ```

3. Installez les dépendances :
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. Configurez la base de données dans `appPLaybPlay.py` :
    ```python
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "root",
        "database": "play_by_play"
    }
    ```

2. Assurez-vous que votre base de données est configurée et que les tables nécessaires sont créées.

## Utilisation

1. Lancez l'application :
    ```sh
    flask --app appPLaybPlay.py run
    ```

2. Ouvrez votre navigateur et accédez à `http://127.0.0.1:5000`.

## Scripts

- `scripts/AddChampsScript.py` : Ajoute les champions à la base de données.
- `scripts/AddLeaguesScript.py` : Ajoute les ligues à la base de données.
- `scripts/AddMatchsScheduledForLeagueScript.py` : Ajoute les matchs programmés pour une ligue spécifique.
- `scripts/AddMatchsScheduledScript.py` : Ajoute les matchs programmés.
- `scripts/AddTeamsPlayersScript.py` : Ajoute les équipes et les joueurs à la base de données.
- `scripts/TournamentScript.py` : Ajoute les tournois à la base de données.


## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.


## API Utilisée

Ce projet utilise l'API [LoL Esports API](https://vickz84259.github.io/lolesports-api-docs/) pour obtenir les données des matchs de League of Legends. Assurez-vous de consulter la documentation de l'API pour comprendre comment elle fonctionne et comment l'intégrer dans votre projet.