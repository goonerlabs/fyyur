#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

# from email.policy import default
import os
import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import load_only
from models import Artist, Venue, Show, app, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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

  locations = Venue.query.distinct(Venue.city, Venue.state).all()

  data = []
  try:
    for location in locations:
      temporary_data = {}
      temporary_data = {
        'city': location.city,
        'state': location.state
      }
      venues = []
      venue_data = Venue.query.filter(Venue.city == location.city, Venue.state == location.state).all()
      for venue in venue_data:
        temp_data = {
          'id' : venue.id,
          'name' : venue.name,
          'num_upcoming_shows' : len(list(filter(lambda x: x.start_time > datetime.today(), venue.shows )))
        }
        venues.append(temp_data)
      temporary_data['venues'] = venues
      data.append(temporary_data)
    
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Something went wrong. Please try again.')
    return render_template('pages/home.html')
  
  finally:
    return render_template('pages/venues.html', areas=data)
  
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  #* done
  search_info = request.form.get('search_term', '')
  venues = Venue.query.filter(
    Venue.name.ilike('%{}%'.format(search_info))
  ).all()

  data = []
  for venue in venues:
    temporary_data = {}
    temporary_data['id'] = venue.id
    temporary_data['name'] = venue.name
    temporary_data['num_upcoming_shows'] = len(list(filter(lambda x: x.start_time > datetime.today(), venue.shows )))
    data.append(temporary_data)
  
  response = {}
  response['count'] = len(data)
  response['data'] = data
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # *done
  data = {}
  
  try: 
    venue = Venue.query.get(venue_id)
    if venue is None:
      return not_found_error(404) 
    unfiltered_past_shows = list(filter(lambda x: x.start_time < datetime.today(), venue.shows))

    unfiltered_upcoming_shows = list(filter(lambda x: x.start_time > datetime.today(), venue.shows))

    past_shows = []
    for show in unfiltered_past_shows:
      artist = Artist.query.get(show.artist_id)
      filtered_show_data = {
        'artist_id': artist.id,
        'artist_name': artist.name, 
        'artist_image_link': artist.image_link,
        'start_time': show.start_time
      }
      past_shows.append(filtered_show_data)
    upcoming_shows = []
    for show in unfiltered_upcoming_shows:
      artist = Artist.query.get(show.artist_id)
      filtered_show_data = {
        'artist_id': artist.id,
        'artist_name': artist.name, 
        'artist_image_link': artist.image_link,
        'start_time': show.start_time
      }
      upcoming_shows.append(filtered_show_data)
      
    data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
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
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
    # print(data['genres'])
  except:
    print(sys.exc_info())
    flash('Something went wrong. Please try again.')

  finally:
    db.session.close()

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  try:
    new_venue = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres', type=str),
      website = request.form.get('website'),
      facebook_link = request.form.get('facebook_link'),
      image_link = request.form.get('image_link'),
      seeking_talent = True if request.form.get('seeking_talent') else False,
      seeking_description = request.form.get('seeking_description')
    )
    db.session.add(new_venue)
    db.session.commit()
    db.session.refresh(new_venue)
    flash('Venue {} was successfully listed!'.format(request.form.get('name')))
  
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Venue {} could not be listed'.format(request.form.get('name')))
  
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  pass

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  #* done
  cols = ['id', 'name']
  data = db.session.query(Artist).options(load_only(*cols)).all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # *done
  search_info = request.form.get('search_term', '')
  
  artists = Artist.query.filter(
    Artist.name.ilike('%{}%'.format(search_info))
  ).all()

  data = []
  for artist in artists:
    temporary_data = {}
    temporary_data['id'] = artist.id
    temporary_data['name'] = artist.name
    temporary_data['num_upcoming_shows'] = len(list(filter(lambda x: x.start_time > datetime.today(), artist.shows )))
    data.append(temporary_data)
  
  response = {}
  response['count'] = len(data)
  response['data'] = data
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # * done
  data = {}
  
  try: 
    artist = Artist.query.get(artist_id)
    if artist is None:
      return not_found_error(404) 

    unfiltered_past_shows = list(filter(lambda x: x.start_time < datetime.today(), artist.shows))

    unfiltered_upcoming_shows = list(filter(lambda x: x.start_time > datetime.today(), artist.shows))

    past_shows = []
    for show in unfiltered_past_shows:
      venue = Venue.query.get(show.venue_id)
      filtered_show_data = {
        'venue_id': venue.id,
        'venue_name': venue.name, 
        'venue_image_link': venue.image_link,
        'start_time': show.start_time
      }
      past_shows.append(filtered_show_data)

    upcoming_shows = []
    for show in unfiltered_upcoming_shows:
      venue = Venue.query.get(show.venue_id)
      filtered_show_data = {
        'venue_id' : venue.id,
        'venue_name': venue.name, 
        'venue_image_link': venue.image_link,
        'start_time': show.start_time
      }
      upcoming_shows.append(filtered_show_data)
      
    data={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
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
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
  
  except:
    print(sys.exc_info())
    flash('Something went wrong. Please try again.')

  finally:
    db.session.close()
  
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  data = {}

  try:
    artist = Artist.query.get(artist_id)
    if artist is None:
      return not_found_error(404)

    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
    }

  except:
    print(sys.exc_info())
    flash('Something went wrong, please try again.')
    return redirect(url_for('index'))

  finally:
    db.session.close()

  # *done
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # *done
  try:
    update_artist = Artist.query.get(artist_id)

    if update_artist is None: 
      return not_found_error(404)

    update_artist.name = request.form.get('name')
    update_artist.city = request.form.get('city')
    update_artist.state = request.form.get('state')
    update_artist.phone = request.form.get('phone')
    update_artist.genres = request.form.getlist('genres', type=str)
    update_artist.facebook_link = request.form.get('facebook_link')
    update_artist.website = request.form.get('website')
    update_artist.seeking_venue = True if request.form.get('seeking_venue') else False
    update_artist.seeking_description = request.form.get('seeking_description')


    db.session.add(update_artist)
    db.session.commit()
    db.session.refresh(update_artist)
    flash('Artist {} was successfully updated!'.format(request.form.get('name')))
    
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Venue {} could not be listed'.format(request.form.get('name')))
  
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  data = {}

  try:
    venue = Venue.query.get(venue_id)
    if venue is None:
      return not_found_error(404)

    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      'address': venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
    }
  

  except:
    print(sys.exc_info())
    flash('Something went wrong, please try again.')
    return redirect(url_for('index'))

  finally:
    db.session.close()
  # *done
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # *done
  try:
    update_venue = Venue.query.get(venue_id)

    if update_venue is None: 
      return not_found_error(404)

    update_venue.name = request.form.get('name')
    update_venue.city = request.form.get('city')
    update_venue.state = request.form.get('state')
    update_venue.phone = request.form.get('phone')
    update_venue.address = request.form.get('address')
    update_venue.genres = request.form.getlist('genres', type=str)
    update_venue.facebook_link = request.form.get('facebook_link')
    update_venue.website = request.form.get('website')
    update_venue.seeking_talent =True if request.form.get('seeking_talent') else False
    update_venue.seeking_description = request.form.get('seeking_description')
    update_venue.image_link = request.form.get('image_link')


    db.session.add(update_venue)
    db.session.commit()
    db.session.refresh(update_venue)
    flash('Venue {} was successfully updated!'.format(request.form.get('name')))
    
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Artist {} could not be listed'.format(request.form.get('name')))
  
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
  # *done
  try:
    new_artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres', type=str),
      website = request.form.get('website'),
      facebook_link = request.form.get('facebook_link'),
      image_link = request.form.get('image_link'),
      seeking_venue = True if request.form.get('seeking_venue') else False,
      seeking_description = request.form.get('seeking_description')
    )
    db.session.add(new_artist)
    db.session.commit()
    db.session.refresh(new_artist)
    flash('Artist {} was successfully listed!'.format(request.form.get('name')))
    
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Venue {} could not be listed'.format(request.form.get('name')))
  
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # *done
  shows = Show.query.all()

  try:

    data=[]
    for show in shows:
      data.append({
        'venue_id' : show.venue.id,
        'venue_name' : show.venue.name,
        'artist_id' : show.artist.id,
        'artist_name' : show.artist.name,
        'artist_image_link' : show.artist.image_link,
        'start_time' : show.start_time
      })

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('something went wrong, please try again.')

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # *done
  try:
    show = Show(
      artist_id = request.form.get('artist_id'),
      venue_id = request.form.get('venue_id'),
      start_time = datetime.fromisoformat(request.form.get('start_time'))
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')

  finally:
    db.session.close()
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
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

