"""Add initial data
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, SubCategory, Course

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

categories_courses = {
    'Programming Language': {
        'Python': ['Programming with python'],
        'C++': ['Introduction to C++'],
    },
    'Math': {
        'Linear Algebra': ['Linear Algebra Refresher Course'],
        'Calculus': ['Single Variable Calculus'],
        'Statistics': ['Intro to Statistics'],
    },
    'Physics': {
        'Physics': ['Intro to Physics'],
    },
    'Deep Learning': {
        'Deep Learning': ['Deep Learning'],
        'Machine Learning': ['Intro to Machine Learning'],
        'Neural Network': ['Neural Networks'],
        'Artificial Intelligence': ['Intro to AI'],
        'Computer Vision': ['Introduction to Computer Vision'],
        'Robotics': ['Robotics'],
    },
    'Frameworks': {
        'Open CV': ['OpenCV with Python for Image and Video Analysis'],
        'Tensor Flow': ['TensorFlow in a Nutshell'],
    },
}

for category_name, sub_categories in categories_courses.viewitems():
    new_category = Category(name=category_name)
    session.add(new_category)
    session.flush()

    for sub_category_name, courses in sub_categories.viewitems():
        new_sub_category = SubCategory(name=sub_category_name,
                                       category_id=new_category.id)
        session.add(new_sub_category)
        session.flush()

        for course_name in courses:
            new_course = Course(name=course_name,
                                sub_category_id=new_sub_category.id)
            session.add(new_course)
            session.flush()

session.commit()

for course in session.query(Course).all():
    print course.id, course.name, 'in', course.sub_category.category.name
