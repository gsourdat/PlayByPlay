import os
import requests
import mysql.connector
from mysql.connector import errorcode

# Configuration de la connexion à la base de données
config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "play_by_play"
}

# URL de la version actuelle de Data Dragon
URL_CHAMPIONS = "https://ddragon.leagueoflegends.com/cdn/15.5.1/data/fr_FR/champion.json"
DOSSIER_IMAGES = "images/champions"

def telecharger_image(url, chemin):
    """Télécharge une image depuis une URL et l'enregistre à l'emplacement spécifié."""
    try:
        reponse = requests.get(url)
        reponse.raise_for_status()
        with open(chemin, 'wb') as fichier:
            fichier.write(reponse.content)
        print(f"Téléchargement réussi : {chemin}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement de {url} : {e}")

def creer_table_si_non_existante(conn):
    """Crée la table 'champions' si elle n'existe pas déjà."""
    try:
        curseur = conn.cursor()
        curseur.execute('''
            CREATE TABLE IF NOT EXISTS champions (
                id VARCHAR(100) PRIMARY KEY,
                photo VARCHAR(255) NOT NULL
            );
        ''')
        conn.commit()
        print("Table 'champions' vérifiée/créée avec succès.")
    except mysql.connector.Error as e:
        print(f"Erreur lors de la création de la table : {e}")

def inserer_donnees(conn, id_champion, chemin_photo):
    """Insère ou met à jour les informations du champion dans la table 'champions'."""
    try:
        curseur = conn.cursor()
        curseur.execute('''
            INSERT INTO champions (id, photo)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE photo = VALUES(photo);
        ''', (id_champion, chemin_photo))
        conn.commit()
        print(f"Données insérées/mises à jour pour {id_champion}.")
    except mysql.connector.Error as e:
        print(f"Erreur lors de l'insertion des données pour {id_champion} : {e}")

def main():
    # Création du dossier pour les images si nécessaire
    os.makedirs(DOSSIER_IMAGES, exist_ok=True)

    # Connexion à la base de données
    try:
        conn = mysql.connector.connect(**config)
        creer_table_si_non_existante(conn)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erreur : Nom d'utilisateur ou mot de passe incorrect.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Erreur : La base de données n'existe pas.")
        else:
            print(err)
        return

    # Récupération de la liste des champions
    try:
        reponse = requests.get(URL_CHAMPIONS)
        reponse.raise_for_status()
        data = reponse.json()
        champions = data.get("data", {})

        for id_champion in champions:
            nom_fichier = f"{id_champion}.png"
            chemin_image = os.path.join(DOSSIER_IMAGES, nom_fichier)
            url_image = f"https://ddragon.leagueoflegends.com/cdn/15.5.1/img/champion/{nom_fichier}"

            telecharger_image(url_image, chemin_image)
            inserer_donnees(conn, id_champion, chemin_image)

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des données des champions : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
