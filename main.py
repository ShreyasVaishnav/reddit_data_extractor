from ast import Pass
import email
# from crypt import methods
from enum import unique
import flask 
from flask import render_template, Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import input_required, length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from pushshift_functions import PushshiftFunc
import time
import datetime
import datetime as dt  
import pandas as pd
from flask import make_response

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = "thisisasecretkey"
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(25), nullable = False)
    username = db.Column(db.String(20), nullable = False, unique = True)
    password = db.Column(db.String(100), nullable = False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    name = StringField(validators=[input_required(), length(min=4, max=30,)], render_kw={"placeholder": "Name"})
    username = StringField(validators=[input_required(), length(min=4, max=20,)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[input_required(), length(min=4, max=20,)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField(validators=[input_required(), length(min=4, max=20,)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[input_required(), length(min=4, max=20,)], render_kw={"placeholder": "Password"})
    remember = BooleanField("Remember me!")
    submit = SubmitField("Login")

@app.route("/home")
@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data) and user.username == form.username.data:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        return render_template("login_error.html", login_form = form)

    return render_template("login.html", login_form = form)

@app.route("/register", methods = ['GET', 'POST'])
def signup():
    form = RegistrationForm()

    if form.validate_on_submit():
        existing_username = User.query.filter_by(username = form.username.data).first()
        if existing_username:
            return render_template("register_username_error.html", signup_form = form)
        else:
            hashed_password = generate_password_hash(form.password.data, method="sha256")
            # new_user = User(name = form.name.data, username = form.username.data, password = form.password.data)
            new_user = User(name = form.name.data, username = form.username.data, password = hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return render_template("register_success.html", signup_form = form)
    
    return render_template("register.html", signup_form = form)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name = current_user.username )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route("/reddit_posts")
@login_required
def reddit_posts():
    return render_template("posts.html")

@app.route('/extract_posts', methods=['GET', 'POST'])
@login_required
def extract_posts():
    subreddit = request.form.get("subreddit")
    start_year = request.form.get("start_year") 
    start_month = request.form.get("start_month") 
    start_day = request.form.get("start_day")               

    end_year = request.form.get("end_year") 
    end_month = request.form.get("end_month") 
    end_day = request.form.get("end_day")

    start_time = int(dt.datetime(int(start_year), int(start_month), int(start_day)).timestamp())
    end_time = int(dt.datetime(int(end_year), int(end_month), int(end_day)).timestamp())

    filters = []                                           # We don´t want specific filters
    limit = 1000  

    extract_posts = PushshiftFunc()
    result = extract_posts.data_prep_posts(subreddit, start_time, end_time, filters, limit)

    global df_posts 
    df_posts = pd.DataFrame(result)
    result_list = []
    for items in result:
        result_list.append(items[8])

    return render_template('output_posts.html', tables = result_list)

@app.route('/download_posts')
def download_csv_posts():
    resp = make_response(df_posts.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

@app.route("/download_comments")
def download_csv_comments():
    resp = make_response(df_comments.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

    
@app.route("/reddit_comments")
@login_required
def reddit_comments():
    return render_template("comments.html")

@app.route('/extract_comments', methods=['GET', 'POST'])
@login_required
def extract_comments():
    subreddit = request.form.get("subreddit")
    start_year = request.form.get("start_year") 
    start_month = request.form.get("start_month") 
    start_day = request.form.get("start_day")               

    end_year = request.form.get("end_year") 
    end_month = request.form.get("end_month") 
    end_day = request.form.get("end_day")

    start_time = int(dt.datetime(int(start_year), int(start_month), int(start_day)).timestamp())
    end_time = int(dt.datetime(int(end_year), int(end_month), int(end_day)).timestamp())

    filters = []                                           # We don´t want specific filters
    limit = 1000  

    extract_posts = PushshiftFunc()
    result = extract_posts.data_prep_comments(subreddit, start_time, end_time, filters, limit)

    global df_comments 
    df_comments = pd.DataFrame(result)
    result_list = []
    for items in result:
        result_list.append(items[7])

    return render_template('output_comments.html', tables = result_list)

@app.route("/reddit_media")
@login_required
def reddit_media():
    return render_template("media.html")

if __name__=="__main__":
    app.run(debug=True)
