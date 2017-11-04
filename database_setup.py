from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Bundle(Base):
    __tablename__ = 'bundle'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    creator = Column(Integer, ForeignKey('user.email'))
    user = relationship(User)


class Links(Base):
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    url = Column(String(512))
    bundle_id = Column(Integer, ForeignKey('bundle.id'))
    bundle = relationship(Bundle)


engine = create_engine('sqlite:///bundly.db')
Base.metadata.create_all(engine)
