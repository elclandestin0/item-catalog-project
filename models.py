from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
Base = declarative_base()

class User(Base):

class Item(Base):

class Category(Base):

engine = create_engine('sqlite://catalog.db')
Base.metadata.create_all(engine)
