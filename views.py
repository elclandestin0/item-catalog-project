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
    categories = session.query(Category).order_by(asc(Category.name))
    output = ''
    for category in categories:
        output += category.name
        output += "<br>"
        output += str(category.id)
    return output

@app.route('/catalog/category/<int:category_id>')
def showItems(category_id):
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
