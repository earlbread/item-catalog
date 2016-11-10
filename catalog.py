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
                           current_category='All',
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
def create_category():
    """Create a new category"""
    if request.method == 'POST':
        category_name = request.form['name']

        if category_name:
            new_category = Category(name=category_name)
            session.add(new_category)
            session.commit()
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
        category_name = request.form['name']

        if category_name:
            category.name = category_name
            session.add(category)
            session.commit()
        return redirect(url_for('all_courses'))
    else:
        return render_template('edit_category.html',
                               category=category)


@app.route('/category/<int:category_id>/delete/',
           methods=['GET', 'POST'])
def delete_category(category_id):
    """Delete a category"""
    try:
        category = session.query(Category).filter_by(
            id=category_id).one()
    except NoResultFound:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        courses_in_category = session.query(Course).filter_by(
            category_id=category.id)
        courses_in_category.delete()
        category = session.query(Category).filter_by(id=category_id)
        category.delete()
        session.commit()
        return redirect(url_for('all_courses'))
    else:
        return render_template('delete_category.html', category=category)


@app.route('/category/<int:category_id>/course/new/',
           methods=['GET', 'POST'])
def create_course(category_id):
    """Create a new course"""
    try:
        category = session.query(Category).filter_by(
            id=category_id).one()
    except NoResultFound:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        course_name = request.form['name']

        if course_name:
            course_level = request.form['level']
            course_url = request.form['url']
            course_image_url = request.form['image_url']
            course_description = request.form['description']
            course_provider = request.form['provider']

            new_course = Course(name=course_name,
                                level=course_level,
                                url=course_url,
                                image_url=course_image_url,
                                description=course_description,
                                provider=course_provider,
                                category_id=category_id)
            session.add(new_course)
            session.commit()

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
        course_name = request.form['name']

        if course_name:
            course.name = course_name
            course.level = request.form['level']
            course.url = request.form['url']
            course.image_url = request.form['image_url']
            course.description = request.form['description']
            course.provider = request.form['provider']

            session.add(course)
            session.commit()

        return redirect(url_for('all_courses'))
    else:
        return render_template('edit_course.html',
                               category=category,
                               course=course)


@app.route('/category/<int:category_id>/course/<int:course_id>/delete/',
           methods=['GET', 'POST'])
def delete_course(category_id, course_id):
    """Delete a course"""
    try:
        course = session.query(Course).filter_by(
            id=course_id).one()
        category = session.query(Category).filter_by(
            id=category_id).one()
    except NoResultFound:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        course = session.query(Course).filter_by(id=course_id)
        course.delete()
        session.commit()
        return redirect(url_for('all_courses'))
    else:
        return render_template('delete_course.html',
                               category=category,
                               course=course)


@app.route('/category/<int:category_id>/course/<int:course_id>/json/')
def course_json(category_id, course_id):
    return 'Show JSON for specific course'


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
