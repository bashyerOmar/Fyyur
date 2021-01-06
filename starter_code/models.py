#from app import db
from sqlalchemy import ARRAY , String
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(ARRAY(String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    show_venue = db.relationship('Show', backref='venue', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # Show class , Venue the name of table 

    def __init__(self, name, genres, city, state, address, phone, image_link, 
      facebook_link, website, seeking_talent, seeking_description, upcoming_shows_count, past_shows_count ):
       self.name = name
       self.genres = genres
       self.city = city
       self.state = state
       self.address=address
       self.phone=phone
       self.image_link=image_link
       self.facebook_link=facebook_link
       self.website=website
       self.seeking_talent=seeking_talent
       self.seeking_description=seeking_description
       self.upcoming_shows_count=upcoming_shows_count
       self.past_shows_count=past_shows_count



class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text)
    upcoming_shows_count = db.Column(db.Integer)
    past_shows_count = db.Column(db.Integer)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    show_artist = db.relationship('Show', backref='artist', lazy=True)
    
    def __init__(self, name, city, state, phone, genres, image_link, 
      facebook_link, website, seeking_venue, seeking_description, upcoming_shows_count, past_shows_count ):
       self.name = name
       self.city = city
       self.state = state
       self.phone=phone
       self.genres = genres
       self.image_link=image_link
       self.facebook_link=facebook_link
       self.website=website
       self.seeking_venue=seeking_venue
       self.seeking_description=seeking_description
       self.upcoming_shows_count=upcoming_shows_count
       self.past_shows_count=past_shows_count

 
class Show(db.Model):
    __tablename__='show'
    id=db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id') , nullable=False)
    start_time=db.Column(db.DateTime, nullable=False)
    venue_id= db.Column(db.Integer,db.ForeignKey('venue.id') , nullable=False)




  #db.create_all()
