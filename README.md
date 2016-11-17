# Item Catalog

This is the fourth project of Full Stack Web Develper Nanodegree by Udacity.

Users can sign in with google or facebook. After sign in, they can create, edit, delete category or course.

You can check live version of this project [here](https://my-courses.herokuapp.com).

## Getting started

To get started with the app, you need to install [Virtualenv][1].
Then make a virtual environment.

    $ git clone https://github.com/earlbread/item-catalog.git
    $ cd item-catalog
    $ virtualenv ENV
    $ source ENV/bin/activate

After that, you need to install some requirements.

    $ pip install -r requirements.txt

Finally, you can use it after finish database setup.

    $ python database_setup.py
    $ python catalog.py


## Social login

To use social login, you need to get client id from google and facebook and set environment variables.

    $ export GOOGLE_CLIENT_ID='YOUR_GOOGLE_CLIENT_ID'
    $ export GOOGLE_CLIENT_SECRET='YOUR_GOOGLE_CLIENT_SECRET'
    $ export FB_CLIENT_ID='YOUR_FACEBOOK_CLIENT_ID'
    $ export FB_CLIENT_SECRET='YOUR_FACEBOOK_CLIENT_SECRET'


[1]: https://virtualenv.pypa.io/en/stable/installation/

## Used skills

### Languages

 - HTML / CSS
 - JavaScript
 - Python

### Frameworks
 - [Flask][2]
 - [Bootstrap][3]
 - [Heroku][4]
 - [Simple Blog Template][5]
 - [Jinja2][6]

[2]: http://flask.pocoo.org/
[3]: http://getbootstrap.com/
[4]: https://www.heroku.com/
[5]: https://github.com/earlbread/simple-blog-template
[6]: http://jinja.pocoo.org/docs/dev/
