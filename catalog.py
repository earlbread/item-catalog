"""Server code for item-catalog app
"""
from flask import Flask
from flask import redirect, url_for
from flask import render_template
from flask import request

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import Base, Category, Course

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)
app.url_map.strict_slashes = False

@app.route('/')
@app.route('/category')
def index():
    return redirect(url_for('all_courses'))

@app.route('/category/all/')
def all_courses():
    """Show courses of all category"""
    categories = session.query(Category).all()
    courses = session.query(Course).all()

    return render_template('course_list.html',
                           current_category='all',
                           categories=categories,
                           courses=courses)


@app.route('/category/all/json/')
def all_courses_json():
    return 'Show JSON for all courses'


@app.route('/category/<int:category_id>/')
def course_in_category(category_id):
    """Show courses in category"""
    try:
        current_category = session.query(Category).filter_by(
            id=category_id).one()
    except NoResultFound:
        return redirect(url_for('all_courses'))

    categories = session.query(Category).all()
    courses = session.query(Course).filter_by(category_id=category_id).all()

    return render_template('course_list.html',
                           current_category=current_category.name,
                           categories=categories,
                           courses=courses)


@app.route('/category/<int:category_id>/json/')
def category_in_category_json(category_id):
    return 'Show JSON for courses in category'


@app.route('/category/new/', methods=['GET', 'POST'])
def new_category():
    """Create a new category"""
    if request.method == 'POST':
        return redirect(url_for('all_courses'))
    else:
        return render_template('new_category.html')


@app.route('/category/<int:category_id>/edit/',
           methods=['GET', 'POST'])
def edit_category(category_id):
    """Edit a category"""
    try:
        category = session.query(Category).filter_by(
            id=category_id).one()
    except NoResultFound:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        return redirect(url_for('all_courses'))
    else:
        return render_template('edit_category.html',
                               category=category)


@app.route('/category/<int:category_id>/delete/',
           methods=['POST'])
def delete_category(category_id):
    """Delete a category"""
    if request.method == 'POST':
        return redirect(url_for('all_courses'))


@app.route('/category/<int:category_id>/course/new/',
           methods=['GET', 'POST'])
def new_course(category_id):
    """Create a new course"""
    try:
        category = session.query(Category).filter_by(
            id=category_id).one()
    except NoResultFound:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        return redirect(url_for('all_courses'))
    else:
        return render_template('new_course.html',
                               category=category)


@app.route('/category/<int:category_id>/course/<int:course_id>/edit/',
           methods=['GET', 'POST'])
def edit_course(category_id, course_id):
    """Edit a course"""
    try:
        category = session.query(Category).filter_by(id=category_id).one()
        course = session.query(Course).filter_by(id=course_id).one()
    except NoResultFound:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        return redirect(url_for('all_courses'))
    else:
        return render_template('new_course.html',
                               category=category,
                               course=course)


@app.route('/category/<int:category_id>/course/<int:course_id>/delete/',
           methods=['POST'])
def delete_course(category_id, course_id):
    """Delete a course"""
    if request.method == 'POST':
        return redirect(url_for('all_courses'))


@app.route('/category/<int:category_id>/course/<int:course_id>/json/')
def course_json(category_id, course_id):
    return 'Show JSON for specific course'


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
