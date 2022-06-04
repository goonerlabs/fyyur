from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), default='')
    facebook_link = db.Column(db.String(500), default='')
    website = db.Column(db.String(500), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), default='')
    genres = db.Column(db.ARRAY(db.String))

    artists = db.relationship('Artist', secondary='shows')
    shows = db.relationship('Show', backref='venues')

    def __repr__(self):
      return '<Venue {}, {}>'.format(self.id, self.name)
    

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), default='', nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500), default='')
    facebook_link = db.Column(db.String(120), default='')
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), default='')
    website = db.Column(db.String(120))

    venues = db.relationship('Venue', secondary='shows')
    shows = db.relationship('Show', backref='artists')

    def __repr__(self):
      return '<Artist {}, {}>'.format(self.id, self.name)

class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id', ondelete='CASCADE'),  nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id', ondelete='CASCADE'), nullable=False)
  start_time = db.Column(db.DateTime(), nullable=False)

  venue = db.relationship('Venue')
  artist = db.relationship('Artist')