from flask import Flask, redirect, request, jsonify, render_template
from models import HybridRecommender
from users import db,User 
import pandas as pd
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/database_name'  # Mettez à jour avec vos informations
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Crée un nouvel utilisateur
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            return redirect('/login')
        except IntegrityError:
            db.session.rollback()
            return "Ce nom d'utilisateur existe déjà. Veuillez choisir un autre nom d'utilisateur."

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vérifie les informations d'identification
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Connecte l'utilisateur (vous pouvez ajouter la gestion de session ici)
            return redirect('/profile')
        else:
            return "Nom d'utilisateur ou mot de passe incorrect."

    return render_template('login.html')

# Autres routes et configuration restent inchangées...

if __name__ == '__main__':
    app.run(debug=True)
