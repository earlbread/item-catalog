"""Server code for item-catalog app
"""
from flask import Flask
from flask import redirect, url_for
from flask import render_template

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import Base, Category, Course

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

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
    return 'Create a new category'


@app.route('/category/<int:category_id>/edit/',
           methods=['GET', 'POST'])
def edit_category(category_id):
    return 'Edit a category'


@app.route('/category/<int:category_id>/delete/',
           methods=['GET', 'POST'])
def delete_category(category_id):
    return 'Delete a category'


@app.route('/category/<int:category_id>/course/new/',
           methods=['GET', 'POST'])
def new_course(category_id):
    return 'Create a new course'


@app.route('/category/<int:category_id>/course/<int:course_id>/edit/',
           methods=['GET', 'POST'])
def edit_course(category_id, course_id):
    return 'Edit a course'


@app.route('/category/<int:category_id>/course/<int:course_id>/delete/',
           methods=['GET', 'POST'])
def delete_course(category_id, course_id):
    return 'Delete a course'


@app.route('/category/<int:category_id>/course/<int:course_id>/json/')
def course_json(category_id, course_id):
    return 'Show JSON for specific course'


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
