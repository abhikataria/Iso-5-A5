import os
import base64
from io import BytesIO
from flask import Flask, request, render_template, redirect, url_for, flash, session, \
    abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
    current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, Length, EqualTo
import warnings
import itertools
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
# create application instance
app = Flask(__name__)
app.config.from_object('config')

# initialize extensions
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager(app)



class User(UserMixin, db.Model):
    """User model."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    contact = db.Column(db.String(64),index=True)
    email = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@lm.user_loader
def load_user(user_id):
    """User loader callback for Flask-Login."""
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    """Registration form."""
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    email = StringField('Email', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    password_again = PasswordField('Password again',
                                   validators=[Required(), EqualTo('password')])
    contact = StringField('Contact', validators=[Required()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    #token = StringField('Token', validators=[Required(), Length(6, 6)])
    submit = SubmitField('Login')


@app.route('/dashboard')
def dashboard():
    """User login route."""
    if not current_user.is_authenticated:
        # if user is logged in we get out of here  or not user.verify_totp(form.token.data)
        return redirect(url_for('index'))
    return render_template('home.html')


@app.route('/')
def index():
    """User login route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here  or not user.verify_totp(form.token.data)
        return redirect(url_for('dashboard'))

    return render_template('signupget.html')

@app.route('/', methods=[ 'POST'])
def index_post():
    """User login route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here  or not user.verify_totp(form.token.data)
        return redirect(url_for('dashboard'))
    form = LoginForm()
    contact = request.form['contact']
    password = request.form['password']
    user = User.query.filter_by(contact=contact).first()
    if user is None or not user.verify_password(password) :
        flash('Invalid username, password or token.')
        return redirect(url_for('index'))
    # log user in
    login_user(user)
    #flash('You are now logged in!')
    return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)
    return render_template('login.html')

@app.route('/register' )
def register():
    """User registration route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('dashboard'))
    return render_template('signup.html')



@app.route('/register', methods=[ 'POST'])
def register_post():
    form = RegisterForm();
    """User registration route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here
        return redirect(url_for('dashboard'))
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    contact = request.form['contact']
    user = User.query.filter_by(username=username).first()
    if user is not None:
        flash('Username already exists.')
        return redirect(url_for('register'))
    # add new user to the database
    user = User(username=username, email=email, password=password, contact=contact)
    db.session.add(user)
    db.session.commit()
    # redirect to the two-factor auth page, passing username in session
    session['username'] = user.username
    return redirect(url_for('dashboard'))
    return render_template('signup.html', form=form)


@app.route('/profile')
def profile():
    return render_template('profile.html');

@app.route('/retailer')
def retailer():
    return render_template('retailer.html');

@app.route('/supplier')
def supplier():
    return render_template('supplier.html');

@app.route('/mandi')
def mandi():
    return render_template('mandi.html');

@app.route('/weatherinfo/weather')
def weather():
    if current_user.is_authenticated:
        # if user is logged in we get out of here  or not user.verify_totp(form.token.data)
        return render_template('weather.html');
        
    return render_template('signupget.html')

@app.route('/soil')
def soil():
        fields = ['Modal_Price', 'Price_Date']
        df= pd.read_csv("wheat.csv",skipinitialspace=True, usecols=fields)
        df.Price_Date = pd.to_datetime(df.Price_Date, errors='coerce')
        df=df.set_index('Price_Date')
        data = df.copy()
        y = data
        y = y['Modal_Price'].resample('MS').mean()
        y = y.fillna(y.bfill())
        y.plot(figsize=(15, 6))
        p = d = q = range(0, 2)
        pdq = list(itertools.product(p, d, q))
        seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
        warnings.filterwarnings("ignore")
        for param in pdq:
            for param_seasonal in seasonal_pdq:
                try:
                    mod = sm.tsa.statespace.SARIMAX(y,
                                                    order=param,
                                                    seasonal_order=param_seasonal,
                                                    enforce_stationarity=False,
                                                    enforce_invertibility=False)

                    results = mod.fit()
                except:
                    continue
        pred = results.get_prediction(start=pd.to_datetime('2016-01-01'), dynamic=False)
        pred_ci = pred.conf_int()
        ax = y['1990':].plot(label='observed')
        pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7)
        y_forecasted = pred.predicted_mean
        y_truth = y['2016-01-01':]
        mse = ((y_forecasted - y_truth) ** 2).mean()
        ax = y['1990':].plot(label='observed')
        pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7)
        y_forecasted = pred.predicted_mean
        y_truth = y['2016-01-01':]
        mse = ((y_forecasted - y_truth) ** 2).mean()
        pred_dynamic = results.get_prediction(start=pd.to_datetime('2016-01-01'), dynamic=True, full_results=True)
        pred_dynamic_ci = pred_dynamic.conf_int()
        ax = y['1990':].plot(label='observed', figsize=(20, 15))
        pred_dynamic.predicted_mean.plot(label='Dynamic Forecast', ax=ax)
        y_forecasted = pred_dynamic.predicted_mean
        y_truth = y['2016-01-01':]
        mse = ((y_forecasted - y_truth) ** 2).mean()
        pred_uc = results.get_forecast(steps=20)
        pred_ci = pred_uc.conf_int()
        return render_template('soil.html',data=pred_ci)

@app.route('/faq')
def faq():
    """User login route."""
    if current_user.is_authenticated:
        # if user is logged in we get out of here  or not user.verify_totp(form.token.data)
        return render_template('faq.html')

    return render_template('signupget.html')


@app.route('/logout')
def logout():
    """User logout route."""
    logout_user()
    return redirect(url_for('index'))


# create database tables if they don't exist yet
db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
