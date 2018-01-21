from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import  Category, Item, User, Base
engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create basketball as a category and assign a basketball shoes as  an item in
#the basketball category to test if database is running properly
items = session.query(Item).all()
