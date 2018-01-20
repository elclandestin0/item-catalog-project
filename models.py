from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
Base = declarative_base()

class User(Base):
    """
    Here, we initialize the 'User' relation. It consists of the following
    tables:
        - ID (primary_key)
        - Name
        - email
        - password_hash
        - image
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), index=True)
    email = Column(String(250))
    image = Column(String(250))
    # for maximum security, we store a hashed password so that in the
    # event of a hacker compromising a database, they will have a hard
    # time decoding the users' passwords
    password_hash = Column(String(64))
    # the hashing algorithm takes in the user's password as input, and then
    # proceed to encrypt it and store it as the user's hashed password in
    # the database in question.
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)
    # the verify password algorithm takes in the user's password as input,
    # and then it proceeds to verify if the hashed password is = to the
    # password (after decrypting it using the SHA-256 algorithm)
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

class Item(Base):

class Category(Base):

engine = create_engine('sqlite://catalog.db')
Base.metadata.create_all(engine)
