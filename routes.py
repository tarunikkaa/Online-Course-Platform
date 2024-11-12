from flask import Blueprint, render_template, flash, redirect, url_for, session
from models import db, User, Course, Enrollment, Progress
from sqlalchemy.orm import joinedload

# Create a blueprint
course_bp = Blueprint('course_bp', __name__)

# Route for viewing all courses
@course_bp.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

# Route for enrolling in a course
@course_bp.route('/enroll/<int:course_id>')
def enroll(course_id):
    # Ensure user is logged in
    if 'username' not in session:
        flash('Please log in to enroll in a course.')
        return redirect(url_for('index'))
    
    # Get the user from the database based on session data
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('User not found. Please log in again.')
        return redirect(url_for('index'))

    # Check if the user is already enrolled in the course
    existing_enrollment = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).first()
    if existing_enrollment:
        flash('You are already enrolled in this course.')
        return redirect(url_for('course_bp.courses'))

    # Add enrollment if not already enrolled
    new_enrollment = Enrollment(user_id=user.id, course_id=course_id)
    db.session.add(new_enrollment)

    # Create a progress entry for the user in this course
    new_progress = Progress(user_id=user.id, course_id=course_id)
    db.session.add(new_progress)

    # Commit changes to the database
    db.session.commit()

    flash('Enrollment successful! Your progress has been initialized.')
    return redirect(url_for('student_profile'))

# Route for tracking progress
@course_bp.route('/progress/<int:course_id>')
def track_progress(course_id):
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        progress = Progress.query.filter_by(user_id=user.id, course_id=course_id).first()
        return render_template('progress.html', progress=progress)
    else:
        flash('Please sign in to view your progress.')
        return redirect(url_for('index'))
    
@course_bp.route('/course/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_details.html', course=course)

@course_bp.route('/unenroll/<int:course_id>', methods=['POST'])
def unenroll(course_id):
    # Ensure the user is logged in
    if 'username' not in session:
        flash('Please log in to unenroll from a course.')
        return redirect(url_for('index'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('User not found. Please log in again.')
        return redirect(url_for('index'))

    # Find the enrollment record and eagerly load the associated course
    enrollment = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).options(joinedload(Enrollment.course)).first()
    if not enrollment:
        flash('You are not enrolled in this course.')
        return redirect(url_for('student_profile'))

    # Remove the enrollment and associated progress
    progress = Progress.query.filter_by(user_id=user.id, course_id=course_id).first()
    if progress:
        db.session.delete(progress)

    db.session.delete(enrollment)
    db.session.commit()

    # Now you can safely access enrollment.course.title
    flash(f'You have successfully unenrolled from {enrollment.course.title}.')
    return redirect(url_for('student_profile'))
    
@course_bp.route('/add-sample-data')
def add_sample_data():
    # Check if sample data already exists
    existing_course = Course.query.first()
    if existing_course:
        return "Sample data already exists."

    # Create sample courses
    course1 = Course(title="Introduction to Python", description="Learn the basics of Python programming.")
    course2 = Course(title="Web Development with Flask", description="Build web applications using Flask framework.")
    course3 = Course(title="Data Analysis with Pandas", description="Analyze data efficiently using Pandas library.")
    
    db.session.add_all([course1, course2, course3])
    db.session.commit()

    # Create sample users
    user1 = User(username="student1", email="student1@example.com", password="password123")
    user2 = User(username="student2", email="student2@example.com", password="password456")
    
    db.session.add_all([user1, user2])
    db.session.commit()

    # Create sample enrollments
    enrollment1 = Enrollment(user_id=user1.id, course_id=course1.id)
    enrollment2 = Enrollment(user_id=user1.id, course_id=course2.id)
    enrollment3 = Enrollment(user_id=user2.id, course_id=course3.id)
    
    db.session.add_all([enrollment1, enrollment2, enrollment3])
    db.session.commit()

    # Create sample progress entries
    progress1 = Progress(user_id=user1.id, course_id=course1.id, completed_lessons=5, completed_assignments=2, test_scores=85.0)
    progress2 = Progress(user_id=user1.id, course_id=course2.id, completed_lessons=3, completed_assignments=1, test_scores=78.5)
    progress3 = Progress(user_id=user2.id, course_id=course3.id, completed_lessons=8, completed_assignments=4, test_scores=92.0)
    
    db.session.add_all([progress1, progress2, progress3])
    db.session.commit()

    return "Sample data added successfully!"
