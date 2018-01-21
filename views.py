from models import Base, User, Item, Category
from flask import Flask, jsonify, request, url_for, abort, g, render_template, redirect
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
@app.route('/categories/')
def showSportCategories():
    """
    In showCategories() we query all the categories in the catalog.db, fetch
    them by name and ID, store it in an output string then return that output
    string to be rendered in the URI path '/' or '/catalog'
    """
    categories = session.query(Category).order_by(asc(Category.name))
    # add logic gate to check for username logging in here. if true, then
    # show only public categories!
    return render_template('all_categories.html', categories = categories)

# add login required here
@app.route('/categories/new', methods=['GET','POST'])
def newSportCategory():
    """
    In newCatalog(), we want to create a new catalog with a name. It should be
    noted that a user must be logged in to create a new catalog.
    """
    # add logic gate to check user name
    if request.method == 'POST':
        new_sport = Category(name = request.form['name'])
        session.add(new_sport)
        session.commit()
        return redirect(url_for('showSportCategories'))
    else:
        return render_template('new_category.html')

@app.route('/categories/<int:category_id>/edit/', methods=['GET','POST'])
def editSportCategory(category_id):
    """
    In editSportCategory(), a user can edit the name of their sport category
    only if they're logged in, of course.
    """
    # add user login logic gate here.
    edit_category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edit_category.name = request.form['name']
            return redirect(url_for('showSportCategories'))
    else:
        return render_template('edit_category.html', category = edit_category)


@app.route('/catalog/category/<int:category_id>')
def showItems(category_id):
    """
    In showItems() we query the category that we click (by ID). After
    successfully fetching that category in question, we then query all the
    items that belong in that category (by category_id) then fetch the name and
    description of each item before returning the output. This output is
    rendered in the path '/catalog/category/<int:category_id>'.
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
