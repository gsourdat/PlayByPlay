from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
import mysql.connector
from flask import request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from flask import flash  # Importez flash pour afficher un message


commentaire = Blueprint('commentaire', __name__)

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

@commentaire.route('/commentaires', methods=['POST'])
@login_required
def ajouter_commentaire():
    # Récupérer les données du formulaire
    event_id = request.form.get('event_id')
    contenu = request.form.get('contenu')
    gif_url = request.form.get('gif_url')  # URL du GIF
    photo = request.files.get('photo')  # Fichier photo
    parent_id = request.form.get('parent_id')  # ID du commentaire parent (pour les réponses)

    # Vérifier les champs obligatoires
    if not event_id or not contenu:
        return jsonify({"error": "event_id et contenu sont requis"}), 400

    # Gérer le téléchargement de la photo
    photo_path = None
    if photo:
        filename = secure_filename(photo.filename)
        upload_folder = os.path.join('static', 'uploads')  # Dossier dans 'static'
        os.makedirs(upload_folder, exist_ok=True)  # Créer le dossier s'il n'existe pas
        photo_path = os.path.join('uploads', filename)  # Chemin relatif à 'static'
        photo.save(os.path.join('static', photo_path))

    # Insérer le commentaire dans la base de données
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO commentaires (user_id, event_id, contenu, gif_url, photo_path, parent_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (current_user.id, event_id, contenu, gif_url, photo_path, parent_id)
    )
    conn.commit()
    conn.close()

    flash("Commentaire ajouté avec succès", "success")  # Message flash
    return redirect(url_for('commentaire.afficher_event', event_id=event_id))  # Redirection

@commentaire.route('/commentaires/<int:event_id>', methods=['GET'])
def obtenir_commentaires(event_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        "SELECT c.id, c.contenu, c.date_creation, c.parent_id, u.pseudo FROM commentaires c "
        "JOIN utilisateurs u ON c.user_id = u.id "
        "WHERE c.event_id = %s ORDER BY c.date_creation DESC", (event_id,)
    )
    commentaires = cursor.fetchall()
    conn.close()
    
    return jsonify(commentaires)

@commentaire.route('/commentaires/<int:comment_id>', methods=['DELETE'])
@login_required
def supprimer_commentaire(comment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérifier si le commentaire appartient à l'utilisateur connecté
    cursor.execute("SELECT user_id FROM commentaires WHERE id = %s", (comment_id,))
    commentaire = cursor.fetchone()
    
    if not commentaire or commentaire[0] != current_user.id:
        return jsonify({"error": "Action non autorisée"}), 403
    
    # Supprimer les réponses associées d'abord
    cursor.execute("DELETE FROM commentaires WHERE parent_id = %s", (comment_id,))
    cursor.execute("DELETE FROM commentaires WHERE id = %s", (comment_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Commentaire supprimé avec succès"}), 200

@commentaire.route('/event/<int:event_id>', methods=['GET'])
def afficher_event(event_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
                SELECT e.event_id, e.event_time, e.game_id, e.match_id, e.type, e.team_color, e.team_id, 
                    t.name AS team_name, t.logo_url AS team_logo, 
                    e.player_id, p.first_name AS player_first_name, p.last_name AS player_last_name, p.image_url AS player_image_url, p.summoner_name AS player_summoner_name, p.role AS player_role,
                    e.opponent_team_color, e.opponent_team_id, 
                    ot.name AS opponent_team_name, ot.logo_url AS opponent_team_logo, 
                    e.opponent_player_id, op.first_name AS opponent_player_first_name, op.last_name AS opponent_player_last_name, op.image_url AS opponent_player_image_url, op.summoner_name AS opponent_player_summoner_name, op.role AS opponent_player_role,
                    e.details
                FROM event e
                LEFT JOIN team t ON e.team_id = t.team_id
                LEFT JOIN player p ON e.player_id = p.player_id
                LEFT JOIN team ot ON e.opponent_team_id = ot.team_id
                LEFT JOIN player op ON e.opponent_player_id = op.player_id
                WHERE e.event_id = %s
            """
    cursor.execute(query, (event_id,))
    # Récupérer les détails de l'événement
    #cursor.execute("SELECT * FROM event WHERE event_id = %s", (event_id,))
    event = cursor.fetchone()
    
    if not event:
        return "Événement introuvable", 404
    
    # Récupérer les commentaires associés
    cursor.execute(
        "SELECT c.id, c.contenu, c.date_creation, c.parent_id, c.gif_url, c.photo_path, u.pseudo, u.profile_pic FROM commentaires c "
        "JOIN utilisateurs u ON c.user_id = u.id "
        "WHERE c.event_id = %s ORDER BY c.date_creation DESC", (event_id,)
    )
    commentaires = cursor.fetchall()
    conn.close()
    print(commentaires)
    print(event)    
    return render_template('event.html', event=event, commentaires=commentaires)

@commentaire.route('/image_popup')
def image_popup():
    image_src = request.args.get('image_src', '')
    previous_title = request.args.get('title', 'Image Popup')  # Titre par défaut si non fourni
    return render_template('event/popups/image_popup.html', image_src=image_src, title=previous_title)
