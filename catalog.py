"""Server code for item-catalog app
"""
import json
import httplib2
import requests

from flask import Flask, redirect, url_for, render_template, request, \
                  jsonify, flash, make_response, session as login_session
from flaskext.csrf import csrf, csrf_exempt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import Base, Category, Course, User

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from functools import wraps

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = 'test_secret_key'

csrf(app)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


@app.route('/login')
def login():
    return render_template('login.html')


def make_response_and_header(msg, status_code):
    response = make_response(json.dumps(msg), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


def create_user(login_session):
    user = User(name=login_session['username'],
                email=login_session['email'])
    session.add(user)
    session.commit()
    return user.id


def login_required(f):
    @wraps(f)
    def decoreated_function(*args, **kwargs):
        if login_session.get('username') is None:
            flash('You need to login.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decoreated_function


@csrf_exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # There is no form data in AJAX, so use get parameter.
    csrf_token = login_session.pop('_csrf_token', None)
    if not csrf_token or csrf_token != request.args.get('_csrf_token'):
        msg = 'CSRF validation failed'
        status_code = 400
        return make_response_and_header(msg, status_code)

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        msg = 'Failed to upgrade the authorization code.'
        status_code = 401
        return make_response_and_header(msg, status_code)

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        msg = 'error'
        status_code = 500
        return make_response_and_header(msg, status_code)

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        msg = "Token's user ID doesn't match given user ID."
        status_code = 401
        return make_response_and_header(msg, status_code)

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        msg = "Token's client ID does not match app's."
        status_code = 401
        print "Token's client ID does not match app's."
        return make_response_and_header(msg, status_code)

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        msg = 'Current user is already connected.'
        status_code = 200
        return make_response_and_header(msg, status_code)

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    user_id = get_user_id(login_session['email'])

    if user_id is None:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    flash("You are now logged in as %s" % login_session['username'], 'success')
    msg = 'User is successfully logged in'
    status_code = 200
    return make_response_and_header(msg, status_code)


def gdisconnect():
    access_token = login_session.get('access_token')

    if access_token is None:
        msg = 'Current user not connected.'
        status_code = 401
        return make_response_and_header(msg, status_code)

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    login_session.clear()
    flash('You are now logged out.', 'success')

    if result['status'] == '200':
        msg = 'Successfully disconnected.'
        status_code = 200
        return make_response_and_header(msg, status_code)
    else:
        msg = 'Failed to revoke token for given user.'
        status_code = 400
        return make_response_and_header(msg, status_code)


@app.route('/logout')
def disconnect():
    gdisconnect()

    return redirect(url_for('all_courses'))


def get_category(category_id):
    """Get category which has category_id and return it.

    If the category_id doesn't exist, return None.
    """
    try:
        category = session.query(Category).filter_by(id=category_id).one()
        return category
    except NoResultFound:
        return None


def get_course(course_id):
    """Get course which has given id and return it.

    If the course doesn't exist, return None.
    """
    try:
        course = session.query(Course).filter_by(id=course_id).one()
        return course
    except NoResultFound:
        return None


@app.route('/')
@app.route('/category')
def index():
    """Redirect to 'all_courses'"""
    return redirect(url_for('all_courses'))


@app.route('/category/all/')
def all_courses():
    """Show courses of all category"""
    categories = session.query(Category).all()
    courses = session.query(Course).all()

    return render_template('course_list.html',
                           categories=categories,
                           courses=courses)


@app.route('/category/all/json/')
def all_courses_json():
    """Show JSON for all courses"""
    courses = session.query(Course).all()

    return jsonify(Course=[course.serialize for course in courses])


@app.route('/category/<int:category_id>/')
def course_in_category(category_id):
    """Show courses in category"""
    current_category = get_category(category_id)

    if current_category is None:
        return redirect(url_for('all_courses'))

    categories = session.query(Category).all()
    courses = session.query(Course).filter_by(category_id=category_id).all()

    return render_template('course_list.html',
                           current_category=current_category,
                           categories=categories,
                           courses=courses)


@app.route('/category/<int:category_id>/json/')
def courses_in_category_json(category_id):
    """Show JSON for courses in category"""
    courses = session.query(Course).filter_by(category_id=category_id).all()

    return jsonify(Course=[course.serialize for course in courses])


def is_owner(user_id):
    return user_id == login_session.get('user_id')


@app.route('/category/new/', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create a new category"""
    if request.method == 'POST':
        category_name = request.form['name']

        if category_name:
            new_category = Category(name=category_name,
                                    user_id=login_session['user_id'])
            session.add(new_category)
            session.commit()

            flash('New category is successfully created', 'success')
        return redirect(url_for('all_courses'))
    else:
        return render_template('new_category.html')


@app.route('/category/<int:category_id>/edit/',
           methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Edit a category"""
    category = get_category(category_id)

    if not is_owner(category.user_id):
        flash("You don't have permission.", 'danger')
        return redirect(url_for('all_courses'))

    if category is None:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        category_name = request.form['name']

        if category_name:
            category.name = category_name
            session.add(category)
            session.commit()
            flash('Category is successfully edited', 'success')
        return redirect(url_for('all_courses'))
    else:
        return render_template('edit_category.html',
                               category=category)


@app.route('/category/<int:category_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    """Delete a category"""
    category = get_category(category_id)

    if not is_owner(category.user_id):
        flash("You don't have permission.", 'danger')
        return redirect(url_for('all_courses'))

    if category is None:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        courses_in_category = session.query(Course).filter_by(
            category_id=category.id)
        courses_in_category.delete()
        category = session.query(Category).filter_by(id=category_id)
        category.delete()
        session.commit()
        flash('Category is successfully deleted', 'success')
        return redirect(url_for('all_courses'))
    else:
        return render_template('delete_category.html', category=category)


@app.route('/category/<int:category_id>/course/new/',
           methods=['GET', 'POST'])
@login_required
def create_course(category_id):
    """Create a new course"""
    category = get_category(category_id)

    if not is_owner(category.user_id):
        flash("You don't have permission.", 'danger')
        return redirect(url_for('all_courses'))

    if category is None:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        course_name = request.form['name']

        if course_name:
            course_level = request.form['level']
            course_url = request.form['url']
            course_image_url = request.form['image_url']
            course_description = request.form['description']
            course_provider = request.form['provider']

            if not course_level:
                course_level = 'Unknown'

            if not course_description:
                course_description = 'Course about %s' % course_name

            if not course_provider:
                course_provider = 'Unknown'

            new_course = Course(name=course_name,
                                level=course_level,
                                url=course_url,
                                image_url=course_image_url,
                                description=course_description,
                                provider=course_provider,
                                category_id=category_id,
                                user_id=login_session['user_id'])
            session.add(new_course)
            session.commit()
            flash('New course is successfully created', 'success')

        return redirect(url_for('all_courses'))
    else:
        return render_template('new_course.html', category=category)


@app.route('/category/<int:category_id>/course/<int:course_id>/edit/',
           methods=['GET', 'POST'])
@login_required
def edit_course(category_id, course_id):
    """Edit a course"""
    course = get_course(course_id)

    if not is_owner(course.user_id):
        flash("You don't have permission.", 'danger')
        return redirect(url_for('all_courses'))

    if course is None:
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

            if not course.level:
                course.level = 'Unknown'

            if not course.description:
                course.description = 'Course about %s' % course_name

            if not course.provider:
                course.provider = 'Unknown'

            session.add(course)
            session.commit()
            flash('Course is successfully edited', 'success')

        return redirect(url_for('all_courses'))
    else:
        return render_template('edit_course.html',
                               category=course.category,
                               course=course)


@app.route('/category/<int:category_id>/course/<int:course_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def delete_course(category_id, course_id):
    """Delete a course"""
    course = get_course(course_id)

    if not is_owner(course.user_id):
        flash("You don't have permission.", 'danger')
        return redirect(url_for('all_courses'))

    if course is None:
        return redirect(url_for('all_courses'))

    if request.method == 'POST':
        course = session.query(Course).filter_by(id=course_id)
        course.delete()
        session.commit()
        flash('Course is successfully deleted', 'success')
        return redirect(url_for('all_courses'))
    else:
        return render_template('delete_course.html',
                               course=course)


@app.route('/category/<int:category_id>/course/<int:course_id>/json/')
def course_json(category_id, course_id):
    """Show JSON for specific course"""
    course = session.query(Course).filter_by(id=course_id).one()

    return jsonify(Course=course.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', port=5000)
