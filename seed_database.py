# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Bundle, Links, User, Base

engine = create_engine('sqlite:///bundly.db')

# Clear database
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create a user
nimit = User(name="Nimit Bhargava", email="nimitbhargava@gmail.com")
session.add(nimit)
session.commit()

bundle1 = Bundle(title="Top Movies", creator=1)
session.add(bundle1)
session.commit()

# URLs for Bundle1(Top Movies)
gwtdt = Links(url="http://www.imdb.com/title/tt0068646/", bundle_id=1)
session.add(gwtdt)
session.commit()

gwtdt = Links(url="http://www.imdb.com/title/tt0108052/", bundle_id=1)
session.add(gwtdt)
session.commit()

bundle2 = Bundle(title="Top Self Driving car tutorial", creator=1)
session.add(bundle2)
session.commit()

# URLs for Bundle2(Top Movies)
gwtdt = Links(url="https://udacity.com/course/intro-to-self-driving-cars--nd113", bundle_id=2)
session.add(gwtdt)
session.commit()

gwtdt = Links(url="https://github.com/mikesprague/udacity-nanodegrees#front-end-web-developer-nanodegree", bundle_id=2)
session.add(gwtdt)
session.commit()

print "Seeded database with categories and their items!"
