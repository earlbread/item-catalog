"""Server code for item-catalog app
"""
import os
import json
import httplib2
import requests

from flask import Flask, redirect, url_for, render_template, request, \
                  jsonify, flash, make_response, session as login_session
from flaskext.csrf import csrf, csrf_exempt

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError, \
                                OAuth2WebServerFlow

from functools import wraps

app = Flask(__name__)
app.url_map.strict_slashes = False

env = os.environ.get('CATALOG_ENV', 'prod')
app.config.from_object('catalog.config.%sConfig' % env.capitalize())

csrf(app)

from models import *
from sqlalchemy.orm.exc import NoResultFound


@app.route('/login')
def login():
    return render_template('login.html')


def make_response_and_header(msg, status_code):
    response = make_response(json.dumps(msg), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response


def get_user_id(email):
    try:
        user = db.session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


def create_user(login_session):
    user = User(name=login_session['username'],
                email=login_session['email'])
    db.session.add(user)
    db.session.commit()
    return user.id


def login_required(f):
    @wraps(f)
    def decoreated_function(*args, **kwargs):
        if login_session.get('username') is None:
            flash('You need to login.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decoreated_function


def csrf_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # There is no form data in AJAX, so use get parameter.
        csrf_token = login_session.pop('_csrf_token', None)
        if not csrf_token or csrf_token != request.args.get('_csrf_token'):
            msg = 'CSRF validation failed'
            status_code = 400
            flash('CSRF validation failed', 'danger')
            return make_response_and_header(msg, status_code)
        return f(*args, **kwargs)
    return decorated_function


@csrf_exempt
@app.route('/fbconnect', methods=['POST'])
@csrf_login
def fbconnect():
    access_token = request.data
    print "access token received %s " % access_token

    app_id = app.config['FB_CLIENT_ID']
    app_secret = app.config['FB_CLIENT_SECRET']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout,
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # see if user exists
    user_id = get_user_id(login_session['email'])

    if user_id is None:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    flash("You are now logged in as %s" % login_session['username'], 'success')
    msg = 'User is successfully logged in'
    status_code = 200
    return make_response_and_header(msg, status_code)


@csrf_exempt
@app.route('/gconnect', methods=['POST'])
@csrf_login
def gconnect():
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = OAuth2WebServerFlow(
                client_id=app.config['GOOGLE_CLIENT_ID'],
                client_secret=app.config['GOOGLE_CLIENT_SECRET'],
                scope='')

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
    if result['issued_to'] != app.config['GOOGLE_CLIENT_ID']:
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

    login_session['provider'] = 'google'
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

    if result['status'] == '200':
        msg = 'Successfully disconnected.'
        status_code = 200
        return make_response_and_header(msg, status_code)
    else:
        msg = 'Failed to revoke token for given user.'
        status_code = 400
        return make_response_and_header(msg, status_code)


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout.
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
            facebook_id, access_token)
    h = httplib2.Http()
    h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/logout')
def disconnect():
    provider = login_session.pop('provider', None)

    if provider is None:
        flash("You're not logged in.", 'danger')
        return redirect(url_for('all_courses'))

    if provider == 'google':
        gdisconnect()
    elif provider == 'facebook':
        fbdisconnect()

    flash('You are now logged out.', 'success')
    login_session.clear()

    return redirect(url_for('all_courses'))


def get_category(category_id):
    """Get category which has category_id and return it.

    If the category_id doesn't exist, return None.
    """
    try:
        category = db.session.query(Category).filter_by(id=category_id).one()
        return category
    except NoResultFound:
        return None


def get_course(course_id):
    """Get course which has given id and return it.

    If the course doesn't exist, return None.
    """
    try:
        course = db.session.query(Course).filter_by(id=course_id).one()
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
    categories = db.session.query(Category).all()
    courses = db.session.query(Course).all()

    return render_template('course_list.html',
                           categories=categories,
                           courses=courses)


@app.route('/category/all/json/')
def all_courses_json():
    """Show JSON for all courses"""
    courses = db.session.query(Course).all()

    return jsonify(Course=[course.serialize for course in courses])


@app.route('/category/<int:category_id>/')
def course_in_category(category_id):
    """Show courses in category"""
    current_category = get_category(category_id)

    if current_category is None:
        return redirect(url_for('all_courses'))

    categories = db.session.query(Category).all()
    courses = db.session.query(Course).filter_by(category_id=category_id).all()

    return render_template('course_list.html',
                           current_category=current_category,
                           categories=categories,
                           courses=courses)


@app.route('/category/<int:category_id>/json/')
def courses_in_category_json(category_id):
    """Show JSON for courses in category"""
    courses = db.session.query(Course).filter_by(category_id=category_id).all()

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
            db.session.add(new_category)
            db.session.commit()

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
            db.session.add(category)
            db.session.commit()
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
        courses_in_category = db.session.query(Course).filter_by(
            category_id=category.id)
        courses_in_category.delete()
        category = db.session.query(Category).filter_by(id=category_id)
        category.delete()
        db.session.commit()
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
            db.session.add(new_course)
            db.session.commit()
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

            db.session.add(course)
            db.session.commit()
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
        course = db.session.query(Course).filter_by(id=course_id)
        course.delete()
        db.session.commit()
        flash('Course is successfully deleted', 'success')
        return redirect(url_for('all_courses'))
    else:
        return render_template('delete_course.html',
                               course=course)


@app.route('/category/<int:category_id>/course/<int:course_id>/json/')
def course_json(category_id, course_id):
    """Show JSON for specific course"""
    course = db.session.query(Course).filter_by(id=course_id).one()

    return jsonify(Course=course.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', port=5000)
