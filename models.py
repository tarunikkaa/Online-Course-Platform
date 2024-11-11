from flask_sqlalchemy import SQLAlchemy
# Initialize the database
db = SQLAlchemy()

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    # One-to-many relationship with Enrollment and Progress
    enrollments = db.relationship('Enrollment', back_populates='user', cascade="all, delete-orphan")
    progress = db.relationship('Progress', back_populates='user', cascade="all, delete-orphan")

# Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # One-to-many relationship with Enrollment and Progress
    enrollments = db.relationship('Enrollment', back_populates='course', cascade="all, delete-orphan")
    progress = db.relationship('Progress', back_populates='course', cascade="all, delete-orphan")

# Enrollment model (Many-to-Many relationship between User and Course)
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    user = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

# Progress model
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    completed_lessons = db.Column(db.Integer, default=0)
    completed_assignments = db.Column(db.Integer, default=0)
    test_scores = db.Column(db.Float, nullable=True)

    user = db.relationship('User', back_populates='progress')
    course = db.relationship('Course', back_populates='progress')
