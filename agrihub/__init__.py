from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app=Flask(__name__)
app.config['SECRET_KEY']='795e3ffa6939417dbd3dc4625a334330'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://user_5y15_user:SYmsYVJjPsbDWRhp5TWpxkBjbcP9naUB@dpg-cnp9d7nsc6pc73fqcvi0-a/user_5y15'
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view= 'login'
login_manager.login_message_category='info'

from agrihub.models import Farmer,Buyer, Crop

with app.app_context():
    db.create_all()

from agrihub import routes


