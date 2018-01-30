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
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
print CLIENT_ID

@app.route('/')
@app.route('/categories/')
def showSportCategories():
    """
    In showCategories() we query all the categories in the catalog.db, fetch
    them by name and ID, store it in an output string then return that output
    string to be rendered in the URI path '/' or '/catalog'
    """
    categories = session.query(Category).all()
    # add logic gate to check for username logging in here. if true, then
    # show only public categories!
    return render_template('all_categories.html', categories = categories)

# add login required here
@app.route('/categories/newcategory', methods=['GET','POST'])
def newSportCategory():
    """
    In newCatalog(), we want to create a new catalog with a name. It should be
    noted that a user must be logged in to create a new catalog.
    """
    # add logic gate  to check user name
    if request.method == 'POST':
        new_sport = Category(name = request.form['name'],
                             description =request.form['description']
                             )
        session.add(new_sport)
        session.commit()
        return redirect(url_for('showSportCategories'))
    else:
        return render_template('new_category.html')

@app.route('/categories/<int:category_id>/editcategory/', methods=['GET','POST'])
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
        if request.form['description']:
            edit_category.description = request.form['description']
            return redirect(url_for('showSportCategories'))
    else:
        return render_template('edit_category.html', category = edit_category)

@app.route('/categories/<int:category_id>/deletecategory/', methods=['GET','POST'])
def deleteSportCategory(category_id):
    """
    In deleteSportCategory(), a user can delete the sport category they wish if
    they are logged in to the web application.
    """
    # add user login logic gate here.
    delete_category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        session.delete(delete_category)
        session.commit()
        return redirect(url_for('showSportCategories',
                                category_id = category_id)
                                )
    else:
        return render_template('delete_category.html', category = delete_category)

@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items')
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
    # add logic gate for user login
    return render_template('show_items.html',
                            items = items,
                            category = category)

@app.route('/categories/<int:category_id>/createitem/', methods=['GET','POST'])
def newItem(category_id):
    """
    In newItem(), we query the category_id that we selected, render the html
    template to 'new_item.html', add a new name, description and image, then
    return to the category item menu to show the new item we just created!
    """
    # add username logic here
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        new_item = Item(
            name = request.form['name'],
            description = request.form['description'],
            category = category
            # add image here to be parsed from form here
            )
        session.add(new_item)
        session.commit()
        return redirect(url_for('showItems', category_id = category_id))
    else:
        return render_template('new_item.html', category = category)

@app.route('/categories/<int:category_id>/edititem/<int:item_id>',
            methods=['GET','POST'])
def editItem(category_id, item_id):
    """
    In editItem() we query the category the item is in and the item that we
    clicked on. When we are done editing (done in the editItem.html), we parse
    the name, description and photo into the item from the request and
    go back to the list of items in that category to show us the new edited
    item.
    """

    # add user login logic here
    category = session.query(Category).filter_by(id = category_id).one()
    item = session.query(Item).filter_by(id = item_id).one()
    if request.method == "POST":
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        # add photo gate here
        return redirect(url_for('showItems', category_id = category_id))
    else:
        return render_template('edit_item.html',
                               category = category,
                               item = item)

@app.route('/categories/<int:category_id>/deleteitem/<int:item_id>',
            methods=['GET','POST'])
def deleteItem(category_id, item_id):
    """
    In deleteItem() we query the category the item is in and the item that we
    clicked on. This takes us to a html page that asks us a question (whether
    we want to delete the item or not). If we hit yes, the session.delete(item)
    method is invoked, and we commit it to the database. This takes us back to
    the showItems page, showing us that the item has been successfully deleted.
    """
    # add user login logic here
    category = session.query(Category).filter_by(id = category_id).one()
    item = session.query(Item).filter_by(id = item_id).one()
    if request.method == "POST":
        session.delete(item)
        session.commit()
        return redirect(url_for('showItems', category_id = category_id))
    else:
        return render_template('delete_item.html',
                               category = category,
                               item = item)

@app.route('/categories/<int:category_id>/items/JSON')
def showItemsJSON(category_id):
    """This method serializes the sport items of a category into a JSON file"""
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[item.serialize for item in items])


@app.route('/categories/JSON')
def showCategoriesJSON():
    """This method serializes all the restaurants in the database into a JSON
    file"""
    categories = session.query(Category).all()
    return jsonify(categories=[category.serialize for category in categories])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
