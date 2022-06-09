from flask import Flask, render_template, url_for, redirect
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

def distance(lat1, lat2, lon1, lon2):
     
    # The math module contains a function named radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
      
    # calculate the result
    return(c * r)

def return_garage_data(coordinates):
    con = sql.connect('../Merchant/database.db')
    c =  con.cursor() 
    c.execute("SELECT id,latitude,longitude FROM user")
    records=c.fetchall()
    print(records);
    min_distance= 13592
    id_of_closest_merchant=0
    # print(float(current_user.latitude), float(current_user.longitude))
    for merchant in records:
        # print(f"Latitude {merchant[1]}, Longitude{merchant[2]}")
        user_merchant_distance = distance(float(current_user.latitude), float(merchant[1]), float(current_user.longitude) ,  float(merchant[2]))
        # print(f"Merchant number {merchant[0]} distance: {user_merchant_distance}")
        if user_merchant_distance < min_distance:
            min_distance = user_merchant_distance
            id_of_closest_merchant = merchant[0]

    print(id_of_closest_merchant)

    for merchant in records:
        if(merchant[0]==id_of_closest_merchant):
            return merchant;



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

@app.route('/get-coordinates/<string:sender>', methods=['POST'])
def processCoordinates(sender):
    geoInfo= json.loads(sender)
    print(f"Latitude {geoInfo['Latitude']}")
    print(f"longitude {geoInfo['Longitude']}")

    form = LoginForm()
    con = sql.connect('database.db')
    c =  con.cursor() 
    # print(current_user.username)
    c.execute("UPDATE user SET latitude ='%s', longitude = '%s' WHERE username = '%s' " %(geoInfo['Latitude'], geoInfo['Longitude'], current_user.username))
    # AND longitude=%s , geoInfo['Longitude']
    con.commit() 
    con.close()
    
    closest_garage = return_garage_data(geoInfo)
    URL= "http://www.google.com/maps/place/" + str(closest_garage[1])+"," + str(closest_garage[2])

    con = sql.connect('../Merchant/database.db')
    c =  con.cursor() 
    c.execute("SELECT name,address,phone_number,can_send_person FROM user where id = '%s'" %(closest_garage[0])) 
    # closest_garage[0] is the id of the garage
    records=c.fetchall()
    # print(records);
    myDict={}
    myDict['Name'] = records[0][0];
    myDict['Address'] = records[0][1];
    myDict['Phone'] = records[0][2];
    myDict['Person'] = records[0][3];
    myDict['URL']=URL;
    print(myDict)
    return json.dumps(myDict);


if __name__ == "__main__":
    app.run(debug=True)