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

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)

    level = Column(String(20))  # Beginner, Intermediate, Advanced
    url = Column(String(250))
    image_url = Column(String(250))
    description = Column(String(250))
    provider = Column(String(30))

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship(Category)

    @property
    def serialize(self):
        return {
            'category': self.category.name,
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'url': self.url,
            'image_url': self.image_url,
            'description': self.description,
            'provider': self.provider,
        }

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
