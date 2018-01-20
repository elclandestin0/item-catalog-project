from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase() +
                string.digits) for x in xrange(32))

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
        s = Serializer(secret_key, expires_in = expiration)
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
    		#Valid Token, but expired
            print "Expired token!"
    		return None
    	except BadSignature:
    		#Invalid Token
            print "Invalid token!"
    		return None
    	user_id = data['id']
    	return user_id

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key = true)

class Category(Base):

engine = create_engine('sqlite://catalog.db')
Base.metadata.create_all(engine)
