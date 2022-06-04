#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
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
from models import *
from settings import app, moment, db, migrate


# TODO: connect to a local postgresql database
  

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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

#  Create a Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  body = {}
  try:
    form = VenueForm(request.form)
    print(form.data)
    venue = Venue(
    name = form.name.data,
    genres = form.genres.data,
    city = form.city.data,
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website = form.website_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data)

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html') 


#Show all Venues
#--------------------------------------------
@app.route('/venues')
def venues():

  data = []
  distinct_venues = []

  results = Venue.query.all()
  for result in results:
    city_title = {
      'city': result.city,
      'state': result.state
    }
    if city_title not in distinct_venues:
      distinct_venues.append(city_title)
  
  for item in distinct_venues:
    venues = Venue.query.filter_by(city=item['city'], state=item['state']).all()
    for venue in venues:
      new_venue = []
      add_venue = {
        'id': venue.id,
        'name': venue.name
      }
      new_venue.append(add_venue)
      city_state = {
        'city': item['city'],
        'state': item['state'],
        'venues': new_venue
      }
    data.append(city_state)
  
  return render_template('pages/venues.html', areas=data)

  #Search for Venues
  #-----------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = {}
  search_entry = request.form.get("search_term", "")
  venues = list(Venue.query.filter(
      Venue.name.ilike(f"%{search_entry}%") |
      Venue.state.ilike(f"%{search_entry}%") |
      Venue.city.ilike(f"%{search_entry}%") 
    ).all())

  pre_data = []
  for venue in venues:
      venue_unit = {
          "id": venue.id,
          "name": venue.name
      }
      pre_data.append(venue_unit)

  results = {
        "count": len(venues),
        "data": pre_data
      }

  return render_template('pages/search_venues.html', results=results, search_term=request.form.get("search_term", ""))


#Show Particular Venue
#---------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)

    past_shows = db.session.query(Shows).join(Venue).filter(Shows.venue_id==venue_id).filter(Shows.start_time<datetime.now()).all()
    sub_shows = []
    for show in past_shows:
        sub_shows.append({
          "artist_name": show.artist.name,
          "artist_id": show.artist.id,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })
    venue.past_shows = sub_shows
    venue.past_shows_count = len(past_shows)

  
    upcoming_shows = db.session.query(Shows).join(Venue).filter(Shows.venue_id==venue_id).filter(Shows.start_time>datetime.now()).all()
    sub_shows = []
    for show in upcoming_shows:
        sub_shows.append({
          "artist_name": show.artist.name,
          "artist_id": show.artist.id,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })
    venue.upcoming_shows = sub_shows
    venue.upcoming_shows_count = len(upcoming_shows)
    
    return render_template('pages/show_venue.html', venue=venue)

  
#Delete a Venue
#----------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash("Venue " + venue.name + " was deleted successfully!")
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash("Venue was not deleted successfully.")
  finally:
      db.session.close()

  return redirect(url_for("index"))



#  Artists
#  ----------------------------------------------------------------
#  Create an Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  try:
      new_artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=form.genres.data,
          image_link=form.image_link.data,
          facebook_link=form.facebook_link.data,
          website=form.website_link.data,
          seeking_venue=form.seeking_venue.data,
          seeking_description=form.seeking_description.data,
      )
      db.session.add(new_artist)
      db.session.commit()
      flash("Artist " + request.form["name"] + " was successfully listed!")
  except Exception:
      db.session.rollback()
      flash("Artist was not successfully listed.")
  finally:
      db.session.close()

  return redirect(url_for("index"))

#Show all Artists
#--------------------------------------------------
@app.route('/artists')
def artists():
  
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)


#Search for Artists
#----------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  search_entry = request.form.get("search_term", "")
  artists = list(Artist.query.filter(
      Artist.name.ilike(f"%{search_entry}%") |
      Artist.state.ilike(f"%{search_entry}%") |
      Artist.city.ilike(f"%{search_entry}%") 
    ).all())

  pre_data = []
  for artist in artists:
      artist_unit = {
          "id": artist.id,
          "name": artist.name
      }
      pre_data.append(artist_unit)

  results = {
        "count": len(artists),
        "data": pre_data
      }

  return render_template('pages/search_artists.html', results=results, search_term=request.form.get("search_term", ""))

#Show particular Artist
#-----------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
    
  past_shows = db.session.query(Shows).join(Artist).filter(Shows.artist_id==artist_id).filter(Shows.start_time<datetime.now()).all()
  sub_shows = []
  for show in past_shows:
      sub_shows.append({
        "venue_name": show.venue.name,
        "venue_id": show.venue.id,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })
  artist.past_shows = sub_shows
  artist.past_shows_count = len(past_shows)


  upcoming_shows = db.session.query(Shows).join(Artist).filter(Shows.artist_id==artist_id).filter(Shows.start_time>datetime.now()).all()
  sub_shows = []
  for show in upcoming_shows:
      sub_shows.append({
        "venue_name": show.venue.name,
        "venue_id": show.venue.id,
        "venue_image_link": show.venue.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })
  artist.upcoming_shows = sub_shows
  artist.upcoming_shows_count = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=artist)

# Delete an  Artist
#----------------------------------------
@app.route("/artists/<artist_id>/delete", methods=["GET"])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
        flash("Artist " + artist.name+ " was deleted successfully!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Artist was not deleted successfully.")
    finally:
        db.session.close()

    return redirect(url_for("index"))

#  Update
#  ----------------------------------------------------------------

#Edit Artist Details
#---------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()  
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  try:
      artist = Artist.query.get(artist_id)

      artist.name = form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.genres=form.genres.data
      artist.facebook_link=form.facebook_link.data
      artist.image_link=form.image_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data
      artist.website=form.website_link.data

      db.session.add(artist)
      db.session.commit()
      flash("Artist " + artist.name + " was successfully edited!")
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash("Artist was not edited successfully.")
  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


#Edit Venue Details
#----------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    try:
        venue = Venue.query.get(venue_id)

        venue.name = form.name.data
        venue.city=form.city.data
        venue.state=form.state.data
        venue.address=form.address.data
        venue.phone=form.phone.data
        venue.genres=form.genres.data
        venue.facebook_link=form.facebook_link.data
        venue.image_link=form.image_link.data
        venue.seeking_talent=form.seeking_talent.data
        venue.seeking_description=form.seeking_description.data
        venue.website=form.website_link.data

        db.session.add(venue)
        db.session.commit()

        flash("Venue " + form.name.data + " edited successfully")
        
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("Venue was not edited successfully.")
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Shows
#  ----------------------------------------------------------------
# Create a Show
#------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
  try:
      new_show = Shows(
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data,
          start_time=form.start_time.data
      )
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Show was not successfully listed.')
  finally:
      db.session.close()

  return redirect(url_for("index"))

# Display all Shows
#-------------------------------
@app.route('/shows')
def shows():
  data = []
  shows = Shows.query.all()
  for show in shows:
      #I used backref to access data in parent forms here.
      data.append({
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      })
  return render_template('pages/shows.html', shows=data)

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

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
