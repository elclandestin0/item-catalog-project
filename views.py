from models import Base, User, Item, Category
from flask import Flask, jsonify, request, url_for, abort, g, render_template, redirect, flash
from flask import session as login_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, asc

from flask.ext.httpauth import HTTPBasicAuth
import json, random, string

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


# login and google connect
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    print "the secret key is" + state
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    # request.get_data()
    code = request.data.decode('utf-8')
    try:
        # Upgrade the authorization code into a credentials object
        print "flow from clientsecrets"
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    print access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    print "getting user info "

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
        print "new user created! Hello cl" + login_session['username']
    login_session['user_id'] = user_id

    print access_token

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    print access_token
    if access_token is None:
        print "no access token"
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        print "successfully disconnected"
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print "Can't revoke token for user"
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            print "successfully disconnected"
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['provider']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        flash("You have successfully been logged out.")
        print("Successfully logged out")
        return redirect(url_for('showSportCategories'))
    else:
        print "No provider"
        return redirect(url_for('showSportCategories'))


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], image=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

@app.route('/login_session')
def printLoginSession():
    return jsonify(login_session)

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

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
    if 'username' not in login_session:
        print ("you are now in the main page and you are not logged in")
        return render_template('public_categories.html', categories=categories)
    else:
        print ("You are logged in")
        return render_template('all_categories.html', categories = categories)

# add login required here
@app.route('/categories/newcategory', methods=['GET','POST'])
def newSportCategory():
    """
    In newCatalog(), we want to create a new catalog with a name. It should be
    noted that a user must be logged in to create a new catalog.
    """
    # add logic gate  to check user name
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_sport = Category(name = request.form['name'],
                             description =request.form['description'],
                             user_id = login_session['user_id']
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
    if 'username' not in login_session:
        return redirect('/login')
    if edit_category.user_id != login_session['user_id']:
        return "Unauthorized! Go back to sport categories."
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
    if 'username' not in login_session:
        return redirect('/login')
    if delete_category.user_id != login_session['user_id']:
        return "Unauthorized! Go back to sport categories."
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return "Unauthorized! Go back to items page."
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
    if 'username' not in login_session:
        return redirect('/login')
    if category.user_id != login_session['user_id']:
        return "Unauthorized! Go back to items page."
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

@app.route('/users/JSON')
def showCategoriesJSON():
    """This method serializes all the restaurants in the database into a JSON
    file"""
    users = session.query(User).all()
    return jsonify(users=[user.serialize for user in users])



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
