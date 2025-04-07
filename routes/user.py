from flask import Blueprint, render_template
import mysql.connector
#from appPLaybPlay import bcrypt
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
from flask import abort
import requests
from flask import Flask, request, redirect, url_for

user = Blueprint('user', __name__)
bcrypt = Bcrypt()  # Initialisez Bcrypt avec l'application Flask



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



@user.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']
        pseudo = request.form['pseudo']
        profile_pic = request.files['profile_pic']  # Récupération de la photo de profil

        # Hachage du mot de passe
        mot_de_passe_hache = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

        # Gestion de l'upload de la photo de profil
        profile_pic_url = None
        if profile_pic:
            profile_pic_filename = f"profile_{email}.png"
            profile_pic.save(f"static/uploads/{profile_pic_filename}")
            profile_pic_url = f"uploads/{profile_pic_filename}"

        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérification si l'email existe déjà
        cursor.execute("SELECT * FROM utilisateurs WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur:
            return "Cet email est déjà utilisé !"

        # Insertion du nouvel utilisateur avec le rôle par défaut 'user'
        cursor.execute(
            "INSERT INTO utilisateurs (email, mot_de_passe, role, pseudo, profile_pic) VALUES (%s, %s, 'user', %s, %s)",
            (email, mot_de_passe_hache, pseudo, profile_pic_url)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('user.connexion'))

    return render_template('inscription.html')



@user.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Recherche de l'utilisateur par email
        cursor.execute("SELECT * FROM utilisateurs WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur and bcrypt.check_password_hash(utilisateur['mot_de_passe'], mot_de_passe):
            # Création d'un objet User avec le rôle et la photo de profil
            user = User(
                id=utilisateur['id'],
                email=utilisateur['email'],
                role=utilisateur['role'],
                pseudo=utilisateur['pseudo'],
                profile_pic=utilisateur['profile_pic']
            )
            login_user(user)
            return redirect(url_for('main.app'))  # Redirige vers une page protégée
        else:
            return "Identifiants incorrects"

    return render_template('connexion.html')





class User(UserMixin):
    def __init__(self, id, email, role, pseudo, profile_pic=None):
        self.id = id
        self.email = email
        self.role = role
        self.pseudo = pseudo
        self.profile_pic = profile_pic


def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.role != role:
                print("Vous n'avez pas la permission d'accéder à cette page.")
                print(current_user.role)
                abort(403)  # Forbidden
            return func(*args, **kwargs)
        return wrapper
    return decorator



@user.route('/modifier_role/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def modifier_role(user_id):
    nouveau_role = request.form['role']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Modification du rôle dans la base de données
    cursor.execute("UPDATE utilisateurs SET role = %s WHERE id = %s", (nouveau_role, user_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('gestion_utilisateurs'))


@user.route('/deconnexion')
@login_required
def deconnexion():
    """Déconnecte l'utilisateur et redirige vers la page de connexion."""
    logout_user()
    return redirect(url_for('main.app'))


@user.route('/gestion_utilisateurs')
@login_required
@role_required('admin')
def gestion_utilisateurs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Récupérer tous les utilisateurs
    cursor.execute("SELECT id, email, role FROM utilisateurs")
    utilisateurs = cursor.fetchall()
    conn.close()
    
    return render_template('gestion_utilisateurs.html', utilisateurs=utilisateurs)


@user.route('/supprimer/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def supprimer_utilisateur(user_id):
    # Vérifie si l'utilisateur à supprimer est l'utilisateur connecté
    if user_id == current_user.id:
        return "Vous ne pouvez pas supprimer votre propre compte.", 403  # Retourne une erreur 403 (Forbidden)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Supprimer l'utilisateur de la base de données
    cursor.execute("DELETE FROM utilisateurs WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    
    return '', 204  # Retourne une réponse vide avec un statut HTTP 204 (No Content)




