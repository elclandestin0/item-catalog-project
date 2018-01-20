from models import Base, User, Item, Category
from flask import Flask, jsonify, request, url_for, abort, g, render_template
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, asc

from flask.ext.httpauth import HTTPBasicAuth
import json

#OAuth imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

auth = HTTPBasicAuth()
engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

# LOAD CLIENT_ID BY PARSING IT FROM CLIENT_SECRETS.JSON (from google)

# Show categories
@app.route('/')
@app.route('/catalog')
def showCategories():
    """
    In showCategories() we query all the categories in the catalog.db, fetch
    them by name and ID, store it in an output string then return that output
    string to be rendered in the URI path '/' or '/catalog'
    """
    categories = session.query(Category).order_by(asc(Category.name))
    output = ''
    for category in categories:
        output += category.name
        output += "<br>"
        output += str(category.id)
    return output

@app.route('/catalog/category/<int:category_id>')
def showItems(category_id):
    """
    In showItems() we query the category that we click (by ID). After
    successfully fetching that category in question, we then query all the
    items that belong in that category (by category_id) then fetch the name and
    description of each item before returning the output. This output is
    rendered in the path '/catalog/category/<int:category_id>'
    """
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category.id).all()
    output = ''
    for item in items:
        output += item.name
        output += "<br>"
        output += item.description
        output += "<br>"
        output += str(item.id)
    return output


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
