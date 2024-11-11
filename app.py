from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # For session management, flashing messages

# Initialize the database
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Create the database (Run this only once to initialize the database)
with app.app_context():
    db.create_all()

# Route for the signup/signin page
@app.route('/')
def index():
    return render_template('login.html')

# Sign up route
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if the user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists. Please sign in.')
            return redirect(url_for('index'))
        
        # Add new user to the database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Sign up successful!')
        return redirect(url_for('student_profile'))  # Redirect to the profile page

# Sign in route
@app.route('/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query user from the database
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # Store the user data in session
            session['username'] = user.username
            session['email'] = user.email

            flash('Welcome back, ' + username + '!')
            return redirect(url_for('student_profile'))  # Redirect to the profile page
        else:
            flash('Invalid username or password. Please try again.')
            return redirect(url_for('index'))

# Route for student profile
@app.route('/studentprofile')
def student_profile():
    if 'username' in session and 'email' in session:
        username = session['username']
        email = session['email']
        return render_template('studentprofile.html', username=username, email=email)
    else:
        flash('Please sign in to view your profile.')
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)