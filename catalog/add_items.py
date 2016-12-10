"""Add initial data
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Course, User

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(name='Seunghun Lee',
             email='waydi1@gmail.com')

session.add(user1)
session.commit()

categories = [
    'Programming Language',
    'Math',
    'Physics',
    'Deep Learning',
]


# Add Categories
for category_name in categories:
    new_category = Category(name=category_name, user_id=1)
    session.add(new_category)
    session.flush()

course = Course(name='Programming Foundations with Python',
                level='Beginner',
                url='https://www.udacity.com/course/programming-foundations-with-python--ud036',
                image_url='https://s3-us-west-1.amazonaws.com/udacity-content/course/images/ud036-0619766.jpg',
                description='Learn Object-Oriented Programming',
                provider='Udacity',
                category_id=1,
                user_id=1)
session.add(course)

course = Course(name='Linear Algebra Refresher Course',
                level='Intermediate',
                url='https://www.udacity.com/course/linear-algebra-refresher-course--ud953',
                image_url='https://s3-us-west-1.amazonaws.com/udacity-content/course/images/ud953-d95e68e.jpg',
                description='A Brief Refresher (with Python!)',
                provider='Udacity',
                category_id=2,
                user_id=1)
session.add(course)

course = Course(name='Intro to Physics',
                level='Beginner',
                url='https://www.udacity.com/course/intro-to-physics--ph100',
                image_url='https://lh6.ggpht.com/9xDuLEr_4CuXcBZVbMQPagaUOvdUOH_T8V4I9Nm9XvDogvR4_yudI60v5_0tWedKx2LInYQiV6KOGqNPXuo=s0#w=436&h=268',
                description='Landmarks in Physics',
                provider='Udacity',
                category_id=3,
                user_id=1)
session.add(course)

course = Course(name='Deep Learning',
                level='Advanced',
                url='https://www.udacity.com/course/deep-learning--ud730',
                image_url='https://s3-us-west-1.amazonaws.com/udacity-content/course/images/ud730-b3af4bf.jpg',
                description='Take machine learning to the next level',
                provider='Udacity',
                category_id=4,
                user_id=1)
session.add(course)

session.commit()

for course in session.query(Course).all():
    print course.id, course.name, 'in', course.category.name
