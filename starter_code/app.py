#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#import psycopg2
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship 
from flask_migrate import Migrate
import sys
from models import app, db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

#app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#db = SQLAlchemy(app)
db.init_app(app)
app.config['SECRET_KEY'] = 'FYYUR'

# TODO: connect to a local postgresql database
#app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:zeronyuuki23@localhost:5432/fyyur2'
#migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():



  #query the venues grouped based in city and state 
  state_city = db.session.query(Venue.city,Venue.state).group_by(Venue.state,Venue.city).all()
  data = []
  for area in state_city:
    #query venue id and name filter by state_city 
    venues = db.session.query(Venue.id,Venue.name).filter(Venue.city==area.city).filter(Venue.state==area.state).all()
     #add state_city data in data list 

    data.append({
        "city": area.city,
        "state": area.state,
        "venues":[]
    })

  for venue in venues:
     current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
     #count the num_shows by compare the start date of show with current date  
     num_shows=db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > current_time)
     num_shows=num_shows.count()  
     #add venue data in venues list 
     data[-1]["venues"].append({
         "id": venue.id,
         "name":venue.name,
         "num_upcoming_shows":num_shows 
     })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_term=request.form['search_term']
  # using ilike func because its case insensitive and partial search 
  venue_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')) 
    #'%' + request.form.['search_term'] + '%' >>> appear invalid syntax error
  venue_founded=venue_results.count()
  response={
    "count":venue_founded,
    "data":[]
  }

  #insert venue info in data list 
  for venue in venue_results:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    # count the num_shows by compare the start date of show with current date  
    num_shows=db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > current_time)
    num_shows=num_shows.count()
    response["data"].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows":num_shows
      
        })

   
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
   ##query to fetch all shows for that venue (venue_id) 
  venue_by_id = db.session.query(Venue).filter(Venue.id==venue_id).all()
  past_shows=[]
  upcoming_shows=[]
  past_shows_count=0
  upcoming_shows_count=0
  current_time=datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  #query data of the shows 
  show_data = db.session.query(Show).filter(venue_by_id.id==Show.venue_id)
  for show in show_data:
    the_show_data ={
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%S:%M')#convert the date to string 
      
    }

   #based on the start_time of the show its will be upcoming or past  
    if(current_time < Venue.Show.start_time):
        upcoming_shows.append(the_show_data)
        upcoming_shows_count+=1
    else:
        past_shows.append(the_show_data)
        past_shows_count+=1
   
  # past_shows_count=past_shows.count()
  # upcoming_shows_count=upcoming_shows.count()
  #store data to render it on show_venue page
  for venue in venue_by_id: 
    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.getlist('genres'), #.split(',')
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": upcoming_shows_count
    }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

 #create new venue object 
  add_new_venue=Venue(
  name=request.form['name'],
  city=request.form['city'],
  state=request.form['state'],
  address=request.form['address'],
  facebook_link=request.form['facebook_link'],
  phone=request.form['phone'],
  genres=request.form.getlist('genres'), 
  website=request.form['website'],
  image_link=request.form['image_link'],
  seeking_talent=False,  #request.form['seeking_talent'] >> dosenot work !!
  seeking_description=request.form['seeking_description'],
  upcoming_shows_count=0,
  past_shows_count=0

 ) 

  

  try:
    #add venue recored in db
    db.session.add(add_new_venue)  
    db.session.commit()
    # successful db insert
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    #unsuccessful db insert
    error=True
    print(sys.exc_info())
    #flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
     
  finally: 
  # we should close the session either succeed or fail 
    db.session.close()

  
  #redirect to the index handler which is render homepage
  return redirect(url_for('index'))
  #return render_template('pages/home.html') 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
 

  venue =db.session.query(Venue).filter(Venue.id==venue_id)
  venue_to_del = db.session.query(venue.id)
  try:
    db.session.delete(venue_to_del)
    db.session.commit()
    flash('venue successfully deleted')
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    
    
  finally:
    db.session.close()

  return None
  # return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]

  artist_list = db.session.query(Artist.id,Artist.name).all()
  data=[]
  for artist in artist_list:
    data.append()({
    "id":artist.id,
    "name":artist.name
  })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
 
   #see if the user enter A query all artist on db
  if (request.form['search_term'] == ('A'or'a')):
      all_artist=db.session.query(Artist.id,Artist.name)
    
  else:
    #if else fetch artist based on the search_term 
      all_artist = Artist.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  #exit if statement 
      
  response={
    "count":all_artist.count(),
    "data":[]
  }

  #insert artist info in data list 
  for artist in all_artist:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    num_shows=db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > current_time).all()
    num_shows=num_shows.count()
    response["data"].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows":num_shows
       
    })
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  

  artist_by_id = db.session.query(Artist).filter(Artist.id==artist_id).all()
  past_shows=[]
  upcoming_shows=[]
  past_shows_count=0
  upcoming_shows_count=0
  current_time=datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  #query to fetch all shows for that venue (venue_id)
  #show_data = db.session.query(Show).filter(artist_by_id.id==Show.artist_id).all()
  show_data = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id)
  for show in show_data:
    the_show_data ={
      "venue_id": show.artist_id,
      "venue_name": show.artist.name,
      "venue_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%S:%M')#convert the date to string 
      
    }

   #based on the start_time of the show its will be upcoming or past  
    if(current_time < show.start_time):
        upcoming_shows.append(the_show_data)
        upcoming_shows_count+=1
    else:
        past_shows.append(the_show_data)
        past_shows_count+=1
   
  # past_shows_count=past_shows.count()
  # upcoming_shows_count=upcoming_shows.count()
  #store data to render it on show_venue page 
  for artist in artist_by_id:
    data={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.getlist('genres'), #.split(',')
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": upcoming_shows_count
    }


  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }

  artist_to_update=db.session.query(Artist).filter(Artist.id==artist_id).all()
  #to show data in the form 
  #for artist in artist_to_update:
  form.name.data = artist_to_update.name
  form.city.data = artist_to_update.city
  form.state.data = artist_to_update.state
  form.phone.data = artist_to_update.phone
  form.genres.data = artist_to_update.genres
  form.facebook_link.data = artist_to_update.facebook_link
  form.image_link.data = artist_to_update.image_link
  form.website.data = artist_to_update.website
  form.seeking_venue.data = artist_to_update.seeking_venue
  form.seeking_description.data = artist_to_update.seeking_description


    
    # artist={
    #   "id": artist.id,
    #   "name": artist.name,
    #   "genres": artist.genres,
    #   "city": artist.city,
    #   "state": artist.state,
    #   "phone": artist.phone,
    #   "website": artist.website,
    #   "facebook_link": artist.facebook_link,
    #   "seeking_venue": artist.seeking_venue,
    #   "seeking_description": artist.seeking_description,
    #   "image_link": artist.image_link
    # }



  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_to_update)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  artist_to_update=db.session.query(Artist).filter(Artist.id==artist_id).all()
  #assign the new value to old 
  artist_to_update.name = request.form['name']
  artist_to_update.city = request.form['city']
  artist_to_update.state = request.form['state']
  artist_to_update.phone = request.form['phone']
  artist_to_update.genres = request.form.getlist('genres')
  artist_to_update.image_link = request.form['image_link']
  artist_to_update.facebook_link = request.form['facebook_link']
  artist_to_update.website = request.form['website']
  artist_to_update.seeking_venue = False
  artist_to_update.seeking_description = request.form['seeking_description']

  try:
    db.session.commit()
    flash("Artist updated successfully")
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
   
  finally:
    db.session.close()




   
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_to_update=db.session.query(Venue).filter(Venue.id==venue_id).all()
  #for venue in venue_to_update:
  form.name.data = venue_to_update.name
  form.city.data = venue_to_update.city
  form.state.data = venue_to_update.state
  form.phone.data = venue_to_update.phone
  form.address.data = venue_to_update.address
  form.genres.data = venue_to_update.genres
  form.facebook_link.data = venue_to_update.facebook_link
  form.image_link.data = venue_to_update.image_link
  form.website.data = venue_to_update.website
  form.seeking_talent.data = venue_to_update.seeking_talent
  form.seeking_description.data = venue_to_update.seeking_description

    
    # venue={
    #   "id": venue.id,
    #   "name": venue.name,
    #   "genres": venue.getlist('genres'),
    #   "address":venue.address,
    #   "city": venue.city,
    #   "state": venue.state,
    #   "phone": venue.phone,
    #   "website": venue.website,
    #   "facebook_link": venue.facebook_link,
    #   "seeking_talent": venue.seeking_talent,
    #   "seeking_description": venue.seeking_description,
    #   "image_link": venue.image_link
    # }

  return render_template('forms/edit_venue.html', form=form, venue=venue_to_update)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  venue_to_update=db.session.query(Venue).filter(Venue.id==venue_id).all()
  #assign the new value to old 
  venue_to_update.name = request.form['name']
  venue_to_update.city = request.form['city']
  venue_to_update.state = request.form['state']
  venue_to_update.address=request.form['address']
  venue_to_update.phone = request.form['phone']
  venue_to_update.genres = request.form.getlist('genres')
  venue_to_update.image_link = request.form['image_link']
  venue_to_update.facebook_link = request.form['facebook_link']
  venue_to_update.website = request.form['website']
  venue_to_update.seeking_venue = request.form['seeking_talent']
  venue_to_update.seeking_description = request.form['seeking_description']

  try:
    db.session.commit()
    flash("Venue updated successfully")
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
   
  finally:
    db.session.close()





  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  #create new artist object 
  add_new_artist=Artist(
  name = request.form['name'],
  city = request.form['city'],
  state = request.form['state'],
  phone = request.form['phone'],
  genres = request.form.getlist('genres'),
  facebook_link = request.form['facebook_link'],
  image_link = request.form['image_link'],
  website = request.form['website'],
  seeking_venue = False ,
  seeking_description = request.form['seeking_description']

  ) 

  
  try:
    #add show recored in db
    db.session.add(add_new_artist)  
    db.session.commit()
    # successful db insert
    flash('Show was successfully listed!')
  except:
    #unsuccessful db insert
    error=True
    print(sys.exc_info())
    #flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
     
  finally: 
  # we should close the session either succeed or fail 
    db.session.close()

  
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  
  all_show= db.session.query(Show).join(Artist).join(Venue).all()

  data = []
  for show in all_show: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
  #create new  show object 
  add_new_show=Show(
  artist_id=request.form['artist_id'],
  venue_id=request.form['venue_id'],
  start_time=request.form['start_time'],
  

 ) 

  

  try:
    #add venue recored in db
    db.session.add(add_new_show)  
    db.session.commit()
    # successful db insert
    flash('show ' + request.form['name'] + ' was successfully listed!')
  except:
    #unsuccessful db insert
    error=True
    print(sys.exc_info())
    #flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
     
  finally: 
  # we should close the session either succeed or fail 
    db.session.close()

  
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
#python3 file name auto will run 
# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
