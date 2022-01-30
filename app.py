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
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
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
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(200))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(100))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(300))
    show = db.relationship('Show', backref='venue', lazy=True)
    @property
    def search(self):
      return {
        'id': self.id,
        'name': self.name,
      }


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(1000))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='artist', lazy=True)
    @property
    def search(self):
      return {
        'id': self.id,
        'name': self.name,
      }


class Show(db.Model):
  __tablename__ = 'show'

  show_id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)




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

@app.route('/venues')
def venues():

  places = Venue.query.distinct(Venue.city, Venue.state).all()
  venues = Venue.query.all()
  locals = []
  #
  for place in places:
    locals.append ({
      "city": place.city,
      "state": place.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).count()
      } for venue in venues if venue.city == place.city and venue.state == place.state]
    })

  return render_template('pages/venues.html', areas=locals)




@app.route('/venues/search', methods=['POST'])
def search_venues():

  search = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%' + search + '%')).all()

  data = []

  for venue in venues:
    data.append(venue.search)

  response = {
    "count": len(venues),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  get_venue = Venue.query.filter_by(id=venue_id).first()
  shows=Show.query.join(Artist, Artist.id==Show.artist_id).filter(Artist.id==Show.artist_id, Show.venue_id==venue_id).all()

  past_shows = []
  upcoming_shows = []

  for show in shows:
    show_data={
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if (show.start_time <= datetime.now()):
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)


  data = {
    "id": get_venue.id,
    "name": get_venue.name,
    "genres": get_venue.genres,
    "address": get_venue.address,
    "city": get_venue.city,
    "state": get_venue.state,
    "phone": get_venue.phone,
    "website_link": get_venue.website_link,
    "facebook_link": get_venue.facebook_link,
    "seeking_talent": get_venue.seeking_talent,
    "seeking_description": get_venue.seeking_description,
    "image_link": get_venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
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

  form = VenueForm(request.form)
  try:
    venue=Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Value as e:
    print(e)
    db.session.rollback()
    flash('something went wrong, please try again!)
  finally:
    db.session.close()


  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):

  try:
    venue = Venue.query.get(venue_id)
    flash(venue)
    db.session.delete(venue)
    db.session.commit()
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('deleted was unsuccessful.  try again!')
  finally:
    db.session.close()

  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data=[]
  artists = Artist.query.all()

  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()

  data = []
  for artist in artists:
    data.append(artist.search)

  response ={
    "count": len(artists),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  get_artist = Artist.query.filter_by(id=artist_id).first()
  shows = Show.query.join(Artist,Venue).filter(artist_id == Show.artist_id,Show.venue_id == Venue.id).all()

  past_shows = []
  upcoming_shows = []

  for show in shows:
    show_data = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time < datetime.now():
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)


  data = {
    "id": get_artist.id,
    "name": get_artist.name,
    "genres": get_artist.genres,
    "city": get_artist.city,
    "state": get_artist.state,
    "phone": get_artist.phone,
    "website": get_artist.website,
    "facebook_link": get_artist.facebook_link,
    "seeking_venue": get_artist.seeking_venue,
    "seeking_description": get_artist.seeking_description,
    "image_link": get_artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm(request.form)

  try:
    artist = Artist.query.first_or_404(artist_id)
    form.populate_obj(artist)
    db.session.commit()
    flash('Artist {form.name.data} was updated.')
  except ValueError as e:
    db.session.rollback()
    flash(f'an error occured during update of {form.name.data}' + e)
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm(request.form)

  try:
    venue = Venue.query.first_or_404(venue_id)
    form.populate_obj(venue)
    db.session.commit()
    flash(f'Venue {form.name.data} was updated.')
  except ValueError as e:
    db.session.rollback()
    flash('An error occurred during update.' + e)
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

  form = ArtistForm(request.form)
  try:
    artist = Artist()
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Value as e:
    print(e)
    db.session.rollback()
    flash('something went wrong, please try again')
  finally:
    db.session.close()


  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  get_shows = Show.query.order_by(Show.start_time.desc()).all()
  show_data=[]

  for show in get_shows:
    venue = Venue.query.filter_by(id=Show.venue_id).first_or_404()
    artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
    show_data.extend([{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }])
  #
  #
  return render_template('pages/shows.html', shows=show_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form)
  try:
    show = Show(
      venue_id=form.venue_id.data,
      artist_id=form.artist_id.data,
      start_time=form.start_time.data,
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Value as e:
    print(e)
    db.session.rollback()
    flash('something went wrong, please try again')
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
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
