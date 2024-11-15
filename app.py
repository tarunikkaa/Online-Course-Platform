from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Course, Enrollment, Progress  # Import the Course, Enrollment, and Progress models
from routes import course_bp  # Import the blueprint
import os

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # For session management, flashing messages
db.init_app(app)

# Create the database file if it doesn't exist
with app.app_context():
    if not os.path.exists('users.db'):
        db.create_all()
        print("Database created successfully!")

# Register the blueprint
app.register_blueprint(course_bp)

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

@app.route('/studentprofile')
def student_profile():
    if 'username' in session and 'email' in session:
        user = User.query.filter_by(username=session['username']).first()
        
        # Fetch enrolled courses and progress
        enrolled_courses = db.session.query(Course, Progress).join(Progress).filter(
            Progress.user_id == user.id
        ).all()

        # Structure the data to be used in the template
        courses_data = [{'id': course.id, 'title': course.title, 'progress': progress.completed_lessons}
                        for course, progress in enrolled_courses]

        # Sample recent activities and upcoming events
        recent_activities = ["Enrolled in 'Math 101'", "Submitted 'Homework 2'"]
        upcoming_events = ["Math 101 Midterm on Oct 5", "Project Deadline on Oct 15"]

        return render_template('studentprofile.html', 
                               username=user.username, 
                               email=user.email, 
                               enrolled_courses=courses_data,
                               recent_activities=recent_activities,
                               upcoming_events=upcoming_events)
    else:
        flash('Please sign in to view your profile.')
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.after_request
def add_cache_control_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True)
