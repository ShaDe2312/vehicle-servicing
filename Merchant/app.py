from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import json
import sqlite3 as sql
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    latitude = db.Column(db.String(10), nullable=True)
    longitude = db.Column(db.String(10), nullable=True)
    name = db.Column(db.String(35), nullable=True)    
    phone_number = db.Column(db.String(10), nullable=True)
    address = db.Column(db.String(150), nullable=True)    
    can_send_person =  db.Column(db.String(3), nullable=True)    





class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/merchant-info', methods=['GET', 'POST'])
@login_required
def getinfo():
    return render_template('infoform.html')

@app.route('/record-info', methods=['GET', 'POST'])
@login_required  
def recordinfo():
    if request.method == 'POST':
        name = request.form.get("personname")
        address = request.form.get("address")
        phonenumber = request.form.get("phonenumber")
        pickup = request.form.get("pickup")

        if pickup=="on":
            pickup = "Yes"
        else:
            pickup = "No"        
        print(name,address,phonenumber,pickup)
        con = sql.connect('database.db')
        c =  con.cursor() 
        c.execute("UPDATE user SET name ='%s', phone_number = '%s', address='%s', can_send_person='%s' WHERE username = '%s' " %(name, phonenumber,address,pickup, current_user.username))
        con.commit() 
        con.close()
    return redirect('dashboard')

#
@app.route('/get-coordinates/<string:sender>', methods=['GET','POST'])
def processCoordinates(sender):
    geoInfo= json.loads(sender)
    print(f"Latitude {geoInfo['Latitude']}")
    print(f"longitude {geoInfo['Longitude']}")

    form = LoginForm()
    con = sql.connect('database.db')
    c =  con.cursor() 
    # print(current_user.username)
    c.execute("UPDATE user SET latitude ='%s', longitude = '%s' WHERE username = '%s' " %(geoInfo['Latitude'], geoInfo['Longitude'], current_user.username))
    con.commit() 
    con.close()
    # redirect(url_for('getinfo'))
    # return render_template('infoform.html')
    return '0'
if __name__ == "__main__":
    app.run(debug=True)