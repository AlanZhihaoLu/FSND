#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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
from datetime import datetime
from sqlalchemy.sql import func
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://alanzhihaolu@localhost:5432/fyyurapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.debug = True
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200), nullable=True)
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)
    def get_venue(self):
      return {
        "id": self.id,
        'name': self.name,
        'num_upcoming_shows': Show.query.filter(Show.start_time > datetime.now()).filter(Show.venue_id==self.id).count()
      }
    # children = db.relationship("Show", back_populates="parent")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200), nullable=True)
    website = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)
    # parents = db.relationship("Show", back_populates="child")
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = "show"
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime)
  artist_id = db.Column(db.Integer(), db.ForeignKey('artist.id'), nullable=False)  
  venue_id = db.Column(db.Integer(), db.ForeignKey('venue.id'), nullable=False)
  def get_artistInfo(self):
    artistInfo = Artist.query.filter_by(id=self.artist_id).first()
    artist_name = artistInfo.name
    artist_image_link = artistInfo.image_link
    return {
      'artist_id': self.artist_id,
      'artist_name': artist_name,
      'artist_image_link': artist_image_link,
      'start_time' : self.start_time
    }
  def get_venueInfo(self):
    venueInfo = Venue.query.filter_by(id=self.venue_id).first()
    venue_name = venueInfo.name
    venue_image_link = venueInfo.image_link
    return {
      'venue_id': self.venue_id,
      'venue_name': venue_name,
      'venue_image_link': venue_image_link,
      'start_time' : self.start_time
    }
  # child = db.relationship("Artist", back_populates="parents")
  # parent = db.relationship("Venue", back_populates="children")

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

# @app.route('/venues')
# def venues():
#   data = Venue.query.order_by(Venue.id).all()
#   for i in data:
#     currentID = i.id
#     upcoming_shows = Show.query.filter(Show.start_time > datetime.now()).filter(Show.venue_id==currentID).count()
#     i.num_upcoming_shows = upcoming_shows
#   return render_template('pages/venues.html', areas=data)

@app.route('/venues')
def venues():
  areas = Venue.query.distinct('city','state').all()
  data = []
  for area in areas:
    venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
    record = {
      'city': area.city,
      'state': area.state,
      'venues': [venue.get_venue() for venue in venues],
    }
    data.append(record)
  return render_template('pages/venues.html', areas=data)


# @app.route('/venues')
# def venues():
#   # TODO: replace with real venues data.
#   #       num_shows should be aggregated based on number of upcoming shows per venue.
#   data=[{
#     "city": "San Francisco",
#     "state": "CA",
#     "venues": [{
#       "id": 1,
#       "name": "The Musical Hop",
#       "num_upcoming_shows": 0,
#     }, {
#       "id": 3,
#       "name": "Park Square Live Music & Coffee",
#       "num_upcoming_shows": 1,
#     }]
#   }, {
#     "city": "New York",
#     "state": "NY",
#     "venues": [{
#       "id": 2,
#       "name": "The Dueling Pianos Bar",
#       "num_upcoming_shows": 0,
#     }]
#   }]
#   return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  response = {
    'data': Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  }
  response['count'] = len(response['data'])
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# @app.route('/venues/search', methods=['POST'])
# def search_venues():
#   # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
#   # seach for Hop should return "The Musical Hop".
#   # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
#   response={
#     "count": 1,
#     "data": [{
#       "id": 2,
#       "name": "The Dueling Pianos Bar",
#       "num_upcoming_shows": 0,
#     }]
#   }
#   return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venueData = Venue.query.filter_by(id = venue_id).all()
  venueData = venueData[0]
  data = {
    "id": venueData.id,
    "name": venueData.name,
    "city": venueData.city,
    "state": venueData.state,
    "address": venueData.address,
    "phone": venueData.phone,
    "genres": venueData.genres,
    "image_link": venueData.image_link,
    "facebook_link": venueData.facebook_link,
    "seeking_talent": venueData.seeking_talent,
    "seeking_description": venueData.seeking_description,
    "website": venueData.website
  }
  past_shows = Show.query.filter(Show.start_time < datetime.now()).filter(Show.venue_id==venue_id).all()
  data['past_shows'] = [show.get_artistInfo() for show in past_shows]
  upcoming_shows = Show.query.filter(Show.start_time > datetime.now()).filter(Show.venue_id==venue_id).all()
  data['upcoming_shows'] = [show.get_artistInfo() for show in upcoming_shows]
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_venue.html', venue=data)

# @app.route('/venues/<int:venue_id>')
# def show_venue(venue_id):
#   # shows the venue page with the given venue_id
#   # TODO: replace with real venue data from the venues table, using venue_id
#   data1={
#     "id": 1,
#     "name": "The Musical Hop",
#     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#     "address": "1015 Folsom Street",
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "123-123-1234",
#     "website": "https://www.themusicalhop.com",
#     "facebook_link": "https://www.facebook.com/TheMusicalHop",
#     "seeking_talent": True,
#     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
#     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#     "past_shows": [{
#       "artist_id": 4,
#       "artist_name": "Guns N Petals",
#       "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#       "start_time": "2019-05-21T21:30:00.000Z"
#     }],
#     "upcoming_shows": [],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 0,
#   }
#   data2={
#     "id": 2,
#     "name": "The Dueling Pianos Bar",
#     "genres": ["Classical", "R&B", "Hip-Hop"],
#     "address": "335 Delancey Street",
#     "city": "New York",
#     "state": "NY",
#     "phone": "914-003-1132",
#     "website": "https://www.theduelingpianos.com",
#     "facebook_link": "https://www.facebook.com/theduelingpianos",
#     "seeking_talent": False,
#     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
#     "past_shows": [],
#     "upcoming_shows": [],
#     "past_shows_count": 0,
#     "upcoming_shows_count": 0,
#   }
#   data3={
#     "id": 3,
#     "name": "Park Square Live Music & Coffee",
#     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
#     "address": "34 Whiskey Moore Ave",
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "415-000-1234",
#     "website": "https://www.parksquarelivemusicandcoffee.com",
#     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
#     "seeking_talent": False,
#     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#     "past_shows": [{
#       "artist_id": 5,
#       "artist_name": "Matt Quevedo",
#       "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#       "start_time": "2019-06-15T23:00:00.000Z"
#     }],
#     "upcoming_shows": [{
#       "artist_id": 6,
#       "artist_name": "The Wild Sax Band",
#       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#       "start_time": "2035-04-01T20:00:00.000Z"
#     }, {
#       "artist_id": 6,
#       "artist_name": "The Wild Sax Band",
#       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#       "start_time": "2035-04-08T20:00:00.000Z"
#     }, {
#       "artist_id": 6,
#       "artist_name": "The Wild Sax Band",
#       "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#       "start_time": "2035-04-15T20:00:00.000Z"
#     }],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 1,
#   }
#   data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
#   return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request.form)
  return render_template('forms/new_venue.html', form=form)

# @app.route('/venues/create', methods=['POST'])
# def create_venue_submission():
#     form = VenueForm(request.form, meta={'csrf': False})
#     name=form.name.data,
#     city=form.city.data,
#     state=form.state.data,
#     address=form.address.data,
#     phone=form.phone.data,
#     facebook_link=form.facebook_link.data,
#     image_link=form.image_link.data,
#     website=form.website.data,
#     seeking_talent=form.seeking_talent.data,
#     seeking_description=form.seeking_description.data
#     if form.validate():
#         try:
#             venue = Venue(
#                 name=name,
#                 city=city,
#                 state=state,
#                 address=address,
#                 phone=phone,
#                 genres=request.form.getlist('genres'),
#                 facebook_link=facebook_link,
#                 image_link=image_link,
#                 website=website,
#                 seeking_talent=seeking_talent,
#                 seeking_description=seeking_description
#             )
#             db.session.add(venue)
#             db.session.commit()
#             flash('Venue ' + form.name.data + ' was successfully listed!')
#         except ValueError as e:
#             print(e)
#             db.session.rollback()
#             flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
#         finally:
#             db.session.close()
#     else:
#         message = []
#         for field, errors in form.errors.items():
#             message.append(field + ': (' + '|'.join(errors) + ')')
#     return render_template('pages/home.html')

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    data = request.form
    vname = data['name']
    vcity = data['city']
    vstate = data['state']
    vaddress = data['address']
    vphone = data['phone']
    vgenres = request.form.getlist('genres')
    vfb_link = data['facebook_link']
    vimage_link = data['image_link']
    vwebsite = data['website']
    if data['seeking_talent'] == 'True':
      vseeking_talent = True
    else:
      vseeking_talent = False
    vseeking_description = data['seeking_description']
    try:
        db.session.add(Venue(
            city=vcity,
            state=vstate,
            name=vname,
            address=vaddress,
            phone=vphone,
            facebook_link=vfb_link,
            genres=vgenres,
            seeking_talent=vseeking_talent,
            seeking_description=vseeking_description,
            website=vwebsite,
            image_link=vimage_link
        ))
    except:
        error = True
    finally:
        if not error:
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        else:
            flash('An error occurred. Venue ' +
                  vname + ' could not be listed.')
            db.session.rollback()
    return render_template('pages/home.html')

# @app.route('/venues/create', methods=['POST'])
# def create_venue_submission():
#   # TODO: insert form data as a new Venue record in the db, instead
#   # TODO: modify data to be the data object returned from db insertion

#   # on successful db insert, flash success
#   flash('Venue ' + request.form['name'] + ' was successfully listed!')
#   # TODO: on unsuccessful db insert, flash an error instead.
#   # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
#   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#   return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Show.query.filter_by(venue_id = venue_id).delete()
    Venue.query.filter_by(id = venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return None

# @app.route('/venues/<venue_id>', methods=['DELETE'])
# def delete_venue(venue_id):
#   # TODO: Complete this endpoint for taking a venue_id, and using
#   # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

#   # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
#   # clicking that button delete it from the db then redirect the user to the homepage
#   return None

#  Artists
#  ----------------------------------------------------------------
# @app.route('/artists')
# def artists():
#   # TODO: replace with real data returned from querying the database
#   data=[{
#     "id": 4,
#     "name": "Guns N Petals",
#   }, {
#     "id": 5,
#     "name": "Matt Quevedo",
#   }, {
#     "id": 6,
#     "name": "The Wild Sax Band",
#   }]
#   return render_template('pages/artists.html', artists=data)

@app.route('/artists')
def artists():
  artistInfo = Artist.query.order_by(Artist.id).all()
  data = []
  for artist in artistInfo:
    record = {
      'id': artist.id,
      'name': artist.name
    }
    data.append(record)
  return render_template('pages/artists.html', artists=data)


# @app.route('/artists')
# def artists():
#   data = Artist.query.order_by(Artist.id).all()
#   for i in data:
#     currentID = i.id
#     upcoming_shows = Show.query.filter(Show.start_time > datetime.now()).filter(Show.artist_id==currentID).count()
#     i.num_upcoming_shows = upcoming_shows
#   return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')
  response = {
    'data': Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  }
  response['count'] = len(response['data'])
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# @app.route('/artists/search', methods=['POST'])
# def search_artists():
#   # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
#   # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
#   # search for "band" should return "The Wild Sax Band".
#   response={
#     "count": 1,
#     "data": [{
#       "id": 4,
#       "name": "Guns N Petals",
#       "num_upcoming_shows": 0,
#     }]
#   }
#   return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artistData = Artist.query.filter_by(id = artist_id).all()
  artistData = artistData[0]
  data = {
    'id': artistData.id,
    'name': artistData.name,
    'genres': ''.join(list(filter(lambda x : x!= '{' and x!='}', artistData.genres ))).split(','),
    'city': artistData.city,
    'state': artistData.state,
    'phone': artistData.phone,
    'website': artistData.website,
    'facebook_link': artistData.facebook_link,
    'seeking_venue': artistData.seeking_venue,
    'seeking_description': artistData.seeking_description,
    'image_link': artistData.image_link
  }
  past_shows = Show.query.filter(pShow.start_time < datetime.now()).filter(Show.artist_id==artist_id).all()
  data['past_shows'] = [show.get_venueInfo() for show in past_shows]
  upcoming_shows = Show.query.filter(Show.start_time > datetime.now()).filter(Show.artist_id==artist_id).all()
  data['upcoming_shows'] = [show.get_venueInfo() for show in upcoming_shows]
  data['past_shows_count'] = len(data['past_shows'])
  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  return render_template('pages/show_artist.html', artist=data)

# @app.route('/artists/<int:artist_id>')
# def show_artist(artist_id):
#   # shows the venue page with the given venue_id
#   # TODO: replace with real venue data from the venues table, using venue_id
#   data1={
#     "id": 4,
#     "name": "Guns N Petals",
#     "genres": ["Rock n Roll"],
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "326-123-5000",
#     "website": "https://www.gunsnpetalsband.com",
#     "facebook_link": "https://www.facebook.com/GunsNPetals",
#     "seeking_venue": True,
#     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
#     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#     "past_shows": [{
#       "venue_id": 1,
#       "venue_name": "The Musical Hop",
#       "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#       "start_time": "2019-05-21T21:30:00.000Z"
#     }],
#     "upcoming_shows": [],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 0,
#   }
#   data2={
#     "id": 5,
#     "name": "Matt Quevedo",
#     "genres": ["Jazz"],
#     "city": "New York",
#     "state": "NY",
#     "phone": "300-400-5000",
#     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
#     "seeking_venue": False,
#     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#     "past_shows": [{
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2019-06-15T23:00:00.000Z"
#     }],
#     "upcoming_shows": [],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 0,
#   }
#   data3={
#     "id": 6,
#     "name": "The Wild Sax Band",
#     "genres": ["Jazz", "Classical"],
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "432-325-5432",
#     "seeking_venue": False,
#     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "past_shows": [],
#     "upcoming_shows": [{
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-01T20:00:00.000Z"
#     }, {
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-08T20:00:00.000Z"
#     }, {
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-15T20:00:00.000Z"
#     }],
#     "past_shows_count": 0,
#     "upcoming_shows_count": 3,
#   }
#   data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
#   return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(request.form)
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    return render_template('forms/edit_artist.html', form=form, artist=artist)

# @app.route('/artists/<int:artist_id>/edit', methods=['GET'])
# def edit_artist(artist_id):
#   form = ArtistForm()
#   artist={
#     "id": 4,
#     "name": "Guns N Petals",
#     "genres": ["Rock n Roll"],
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "326-123-5000",
#     "website": "https://www.gunsnpetalsband.com",
#     "facebook_link": "https://www.facebook.com/GunsNPetals",
#     "seeking_venue": True,
#     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
#     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
#   }
#   # TODO: populate form with fields from artist with ID <artist_id>
#   return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    form = ArtistForm(request.form)
    if form.validate():
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.choices
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.website = form.website.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Artist ' + artist.name + ' was successfully edited!')
        except ValueError:
            db.session.rollback()
            flash('Error! Artist ' + artist.name + ' could not be listed.')
    else:
        message = []
        for field, errors in form.errors.items():
            message.append(form[field].label + ', '.join(errors))
            flash('Errors: ' + '|'.join(message))
    return redirect(url_for('show_artist', artist_id=artist_id))

# @app.route('/artists/<int:artist_id>/edit', methods=['POST'])
# def edit_artist_submission(artist_id):
#   # TODO: take values from the form submitted, and update existing
#   # artist record with ID <artist_id> using the new attributes

#   return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm(request.form)
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    return render_template('forms/edit_venue.html', form=form, venue=venue)

# @app.route('/venues/<int:venue_id>/edit', methods=['GET'])
# def edit_venue(venue_id):
#   form = VenueForm()
#   venue={
#     "id": 1,
#     "name": "The Musical Hop",
#     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
#     "address": "1015 Folsom Street",
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "123-123-1234",
#     "website": "https://www.themusicalhop.com",
#     "facebook_link": "https://www.facebook.com/TheMusicalHop",
#     "seeking_talent": True,
#     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
#     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
#   }
#   # TODO: populate form with values from venue with ID <venue_id>
#   return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/artists/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    form = VenueForm(request.form)
    if form.validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.genres = form.genres.choices
            venue.facebook_link = form.facebook_link.data
            venue.image_link = form.image_link.data
            venue.website = form.website.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Venue ' + venue.name + ' was successfully edited!')
        except ValueError:
            db.session.rollback()
            flash('Error! Venue ' + venue.name + ' could not be listed.')
    else:
        message = []
        for field, errors in form.errors.items():
            message.append(form[field].label + ', '.join(errors))
            flash('Errors: ' + '|'.join(message))
    return redirect(url_for('show_venue', venue_id=venue_id))

# @app.route('/venues/<int:venue_id>/edit', methods=['POST'])
# def edit_venue_submission(venue_id):
#   # TODO: take values from the form submitted, and update existing
#   # venue record with ID <venue_id> using the new attributes
#   return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm(request.form)
  return render_template('forms/new_artist.html', form=form)

# @app.route('/artists/create', methods=['POST'])
# def create_artist_submission():
#   # called upon submitting the new artist listing form
#   # TODO: insert form data as a new Venue record in the db, instead
#   # TODO: modify data to be the data object returned from db insertion

#   # on successful db insert, flash success
#   flash('Artist ' + request.form['name'] + ' was successfully listed!')
#   # TODO: on unsuccessful db insert, flash an error instead.
#   # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
#   return render_template('pages/home.html')

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    data = request.form
    aname = data['name']
    acity = data['city']
    astate = data['state']
    aphone = data['phone']
    agenres = request.form.getlist('genres')
    afb_link = data['facebook_link']
    aimage_link = data['image_link']
    awebsite = data['website']
    if data['seeking_venue'] == 'True':
      aseeking_venue = True
    else:
      aseeking_venue = False
    aseeking_description = data['seeking_description']
    try:
        db.session.add(Artist(
            city=acity,
            state=astate,
            name=aname,
            phone=aphone,
            facebook_link=afb_link,
            genres=agenres,
            seeking_venue=aseeking_venue,
            seeking_description=aseeking_description,
            website=awebsite,
            image_link=aimage_link
        ))
    except:
        error = True
    finally:
        if not error:
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        else:
            flash('An error occurred. Artist ' +
                  aname + ' could not be listed.')
            db.session.rollback()
    return render_template('pages/home.html')

# @app.route('/artists/create', methods=['POST'])
# def create_artist_submission():
#   error = False
#   try:
#     newArtist=request.form.get('form', '')
#     db.session.add(newArtist)
#     db.session.commit()
#   except:
#     error = True
#     db.session.rollback()
#     print(sys.exc_info())
#   finally:
#     db.session.close()
#   if error:
#     flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
#   else:
#     flash('Artist ' + request.form['name'] + ' was successfully listed!')
#   return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  result = []
  shows = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Artist.id == Show.artist_id).all()
  for show in shows:
    showObj = {"venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
    }
    result.append(showObj)
  return render_template('pages/shows.html', shows=result)

# @app.route('/shows')
# def shows():
#   # displays list of shows at /shows
#   # TODO: replace with real venues data.
#   #       num_shows should be aggregated based on number of upcoming shows per venue.
#   data=[{
#     "venue_id": 1,
#     "venue_name": "The Musical Hop",
#     "artist_id": 4,
#     "artist_name": "Guns N Petals",
#     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#     "start_time": "2019-05-21T21:30:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 5,
#     "artist_name": "Matt Quevedo",
#     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#     "start_time": "2019-06-15T23:00:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 6,
#     "artist_name": "The Wild Sax Band",
#     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "start_time": "2035-04-01T20:00:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 6,
#     "artist_name": "The Wild Sax Band",
#     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "start_time": "2035-04-08T20:00:00.000Z"
#   }, {
#     "venue_id": 3,
#     "venue_name": "Park Square Live Music & Coffee",
#     "artist_id": 6,
#     "artist_name": "The Wild Sax Band",
#     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "start_time": "2035-04-15T20:00:00.000Z"
#   }]
#   return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# @app.route('/shows/create', methods=['POST'])
# def create_show_submission():
#   # called to create new shows in the db, upon submitting new show listing form
#   # TODO: [COMPLETED] insert form data as a new Show record in the db, instead
#   error = False
#   date_format = '%Y-%m-%d %H:%M:%S'
#   try:
#     show = Show()
#     show.artist_id = request.form['artist_id']
#     show.venue_id = request.form['venue_id']
#     show.start_time = datetime.strptime(request.form['start_time'], date_format)
#     db.session.add(show)
#     db.session.commit()
#   except Exception as e:
#     error = True
#     print(f'Error ==> {e}')
#     db.session.rollback()
#   finally:
#     db.session.close()
#     if error: flash('An error occurred. Show could not be listed.')
#     else: flash('Show was successfully listed!')
#   return render_template('pages/home.html')

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  data = request.form
  sstart_time = str(data['start_time'])
  sartist_id = data['artist_id']
  svenue_id = data['venue_id']
  try:
    newShow = Show(
      artist_id = sartist_id,
      venue_id = svenue_id,
      start_time = sstart_time
    )
    db.session.add(newShow)
    db.session.commit()
  except:
    error = True
  finally:
    db.session.close()
    if not error:
      db.session.commit()
      flash('Show was successfully listed!')
    else:
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
  return render_template('pages/home.html')


# @app.route('/shows/create', methods=['POST'])
# def create_show_submission():
#   # called to create new shows in the db, upon submitting new show listing form
#   # TODO: insert form data as a new Show record in the db, instead

#   # on successful db insert, flash success
#   flash('Show was successfully listed!')
#   # TODO: on unsuccessful db insert, flash an error instead.
#   # e.g., flash('An error occurred. Show could not be listed.')
#   # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
#   return render_template('pages/home.html')

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
