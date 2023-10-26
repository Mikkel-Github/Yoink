from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yoink.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    # Implement a function to get the user object based on user_id
    return User(user_id)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    yoinks = db.relationship('Yoink', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')

class Yoink(db.Model):
    __tablename__ = 'yoink'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='yoinks')
    likes = db.relationship('Like', backref='yoink')
    comments = db.relationship('Comment', backref='yoink', lazy=True)

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(280), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    yoink_id = db.Column(db.Integer, db.ForeignKey('yoink.id'))

class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    yoink_id = db.Column(db.Integer, db.ForeignKey('yoink.id'), nullable=False)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class YoinkForm(FlaskForm):
    content = StringField('Your Yoink', validators=[DataRequired()])
    submit = SubmitField('Yoink It')

@app.route('/')
def home():
    if current_user.is_authenticated:
        # User is logged in
        form = YoinkForm()
        if form.validate_on_submit():
            content = form.content.data
            user_id = get_current_user_id()  # Implement a function to get the current user's ID
            create_yoink(content, user_id)  # Function to create a yoink
            flash('Yoink posted', 'success')
            return redirect(url_for('home'))
        yoinks = get_yoinks()  # Implement a function to get yoinks
        return render_template('home_authenticated.html', form=form, yoinks=yoinks)  # Render the authenticated home page
    else:
        # User is not logged in
        return render_template('home_welcome.html')  # Render the welcome page for non-logged-in users

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        create_user(form.username.data, form.email.data, form.password.data)  # Function to create user
        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Handle user login and session management here
        # Authenticate the user and obtain the user_id
        user_id = authenticate_user()
        user = User(user_id)  # Create a User object
        login_user(user)

        flash('Login successful', 'success')
        return redirect(url_for('home'))
    return render_template('login.html', form=form)

def create_user(username, email, password):
    with app.app_context():
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

# Function to create a yoink and add it to the database
def create_yoink(content, user_id):
    with app.app_context():
        new_yoink = Yoink(content=content, user_id=user_id)
        db.session.add(new_yoink)
        db.session.commit()

# Function to get yoinks from the database
def get_yoinks():
    with app.app_context():
        return Yoink.query.all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
