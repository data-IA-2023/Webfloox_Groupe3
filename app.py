from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLALchemy
from dotenv import load_dotenv
import os


load_dotenv('BDD_URL.env')
BDD_URL = os.environ['BDD_URL']


app= Flask(__name__,template_folder='template')
app.config['SQLALchemy_DATABASE_URI'] = BDD_URL
db= SQLALchemy(app)

class Todo(db.Model):
    id=db.Column(db.Integer, primary_key=True )
    content=db.Column(db.String(200), nullable=False)
    

@app.route('/')
def index():
    return render_template('index.html')

if __name__=="__main__":
    app.run(debug=True)