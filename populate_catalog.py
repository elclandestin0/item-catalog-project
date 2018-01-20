from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import  Category, Item, User, Base
engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

basketball_category = Category(name = "Basketball")
session.add(basketball_category)
session.commit()

basketball_shoes = Item(name="Air Jordan",
                        description = "Fly high!",
                        category = basketball_category
                        )
session.add(basketball_shoes)
session.commit()
