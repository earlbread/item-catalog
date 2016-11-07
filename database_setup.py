"""Database configuration
"""

from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)


class SubCategory(Base):
    __tablename__ = 'sub_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)


class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)

    level = Column(String(20))  # Beginner, Intermediate, Advanced
    url = Column(String(250))
    image_url = Column(String(250))
    description = Column(String(250))
    provider = Column(String(30))

    sub_category_id = Column(Integer, ForeignKey('sub_category.id'))
    sub_category = relationship(SubCategory)

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
