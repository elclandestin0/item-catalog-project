#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Code written by: Memo Khoury, with the generous
#   help of the Udacity team.

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random
import string
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired
)

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase +
                     string.digits) for x in xrange(32))


class User(Base):

    """
    Here, we initialize the 'User' relation. It consists of the following
    tables:
        - id (primary_key)
        - name
        - email
        - password_hash
        - image
    """

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    image = Column(String(250))
    password_hash = Column(String(64))

    def hash_password(self, password):

        # The hashing algorithm takes in the user's password as input, and then
        # proceed to encrypt it and store it as the user's hashed password in
        # the catalog database.

        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):

        # The verify password algorithm takes in the user's password as input,
        # and then it proceeds to verify if the hashed password is = to the
        # password (after decrypting it using the SHA-256 algorithm)

        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):

        # If the user favours using an authorization token through OAuth 2.0,
        # we proceed to serialize the secret_key that is randomly generated
        # upon the user signing in via his/her favourite social media account.
        # We set the expiration date to 10 minutes (600 seconds), and we parse
        # the user id to assign it to the serialized data.

        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):

        # To verify the auth_token we generated, we serialize the secret_key,
        # and fetch the token. If the Signature is expired or it is an invalid
        # token, we return nothing. Else we allocate the user_id to data['id']
        # and return it back from the method (to be used in views.py)

        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        user_id = data['id']
        return user_id

    @property
    def serialize(self):
        """Return User object data in easily serializeable format"""

        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password_hash': self.password_hash,
            'image': self.image,
            }


class Category(Base):

    """
    We initialize the Category relation here. It contains two attributes:
        - name
        - id
    The ID acts as a primary_key to category and as a foreign key to
    the Item class. This is done with regards to sorting the items by category.
    With regards to db design, consider this an open-source catalog project:
    A user can login and create his/her own sport categories, edit them
    and delete them. A user can add as many categories as they want, as long
    as they are logged in!

    For instance, A user can add 4 categories:
        - Boxing
        - Hiking
        - Football
        - Basketball
    If a user isn't logged in, then he/she will only see the public categories
    as examples.
    """

    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    item = relationship('Item', cascade='all, delete-orphan')

    @property
    def serialize(self):
        """Return Category object data in easily serializeable format"""

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
            }


class Item(Base):

    """
    For the Item relation, we have the following attributes:
        - id
        - name
        - description
        - image
        - category_id (foreign_key for the id in Category)
        - user_id (foreign_key for the id in User)

    For this relation, the item can be owned by users! This means that each
    item belongs in a certain category and to a certain user. An example would
    be:
        - User creates 3 categories: Basketball, Boxing, Football
        - User creates 3 items: Basketball shoes, Boxing gloves, Football shoes
    """

    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    description = Column(String(250))
    image = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return Item object data in easily serializeable format"""

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
