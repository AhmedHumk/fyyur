#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    abort,
    jsonify
    )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
#from flask_wtf import Form [deprecated]
from forms import *
from datetime import datetime, timezone
import re
from operator import itemgetter 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.InitiateConfig')
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

# Models Moved To models.py as suggested by the reviewer 
# lets import it after we initialized our db
from models import *

#---------------------------------------------#
# date time formatter function 
#---------------------------------------------#

# Formate datetime.now to a proper date
def currentdateformat(value):

    date_obj = value
    strdate = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    return strdate

# Format the datetime value to preferred format
def strdateToTime(value, format='medium'):

    date_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    if format == 'full':
        return date_obj.strftime("%m/%d/%Y, %H:%M:%S")
    elif format == 'medium':
        return date_obj.strftime("%d-%b-%Y, %H:%M:%S")



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
    # lets get all records from Venue table
    allvenues = Venue.query.all()
    # define and empty the data array to send it later
    datarray = []
    # loop through our venues records
    for venueitem in allvenues:
        venuearia = Venue.query.filter_by(state=venueitem.state).filter_by(city=venueitem.city).all()
        # array that will hold our venue data
        venuearray = []
        Currentime = datetime.now()
        # lets fill our venuearray
        for v in venuearia:
            upcommingshowsnum = len(db.session.query(Show).filter(Show.venue_id==v.id).filter(Show.start_time>Currentime).all())
            venuearray.append({
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": upcommingshowsnum
                })

        datarray.append({
            "city": venueitem.city,
            "state": venueitem.state,
            "venues": venuearray
            })    

    return render_template('pages/venues.html', areas=datarray)
    


@app.route('/venues/search', methods=['POST'])
def search_venues():
  sterm = request.form.get('search_term', '').strip()
  venueResult  = Venue.query.filter(Venue.name.ilike('%' + sterm + '%')).all()
  datarray = []
  Currentime = datetime.now()

  for res in venueResult:
      upcommingshownum = len(db.session.query(Show).filter(Show.venue_id == res.id).filter(Show.start_time > Currentime).all())
      datarray.append({
          "id": res.id,
          "name": res.name,
          "num_upcoming_shows": upcommingshownum

          })

  searchCount = len(venueResult)    
  response = {
      "count": searchCount,
      "data": datarray
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    getvenueItem = Venue.query.filter_by(id=venue_id).one()
    
    if not getvenueItem:
        return redirect(url_for('index'))
    
    genresarr = []
    currentTime = datetime.now()
    # populate genresarr from the getvenueItem genre array that is listed in RelationComposition
    for genrevalue in getvenueItem.genres:
        genresarr.append(genrevalue.name)
        
    # lets get all shows that is bigger than current Time .
    upcomingQ = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>currentTime).all()
    nextshows = []
    # lets get all shows that is smaller than current Time.
    pastshowsQ = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<currentTime).all()
    pastshows = []
    # lets loop on what we have and populate our arrays
    for showitem in upcomingQ:
        nextshows.append({
            "artist_id": showitem.artist_id,
            "artist_name": showitem.artist.name,
            "artist_image_link": showitem.artist.image_link,
            "start_time": currentdateformat(showitem.start_time)
            })
    
    for showitem in pastshowsQ:
        pastshows.append({
            "artist_id": showitem.artist_id,
            "artist_name": showitem.artist.name,
            "artist_image_link": showitem.artist.image_link,
            "start_time": currentdateformat(showitem.start_time)
            })

    #after we loop through our tables and compared the time and date of the show
    #now we can count what we have in our arrays
    nextshowsnum = 0
    pastshowsnum = 0
    nextshowsnum = len(nextshows) # check the len of our array
    pastshowsnum = len(pastshows) # check the len of our array
    print(nextshowsnum)
    print(pastshowsnum)

    data = {
        "id": venue_id,
        "name": getvenueItem.name,
        "genres": genresarr,
        "address": getvenueItem.address,
        "city": getvenueItem.city,
        "state": getvenueItem.state,
        "phone": getvenueItem.phone,
        "website": getvenueItem.website,
        "facebook_link": getvenueItem.facebook_link,
        "seeking_talent": getvenueItem.seeking_talent,
        "seeking_description": getvenueItem.seeking_description,
        "image_link": getvenueItem.image_link,
        "past_shows": pastshows,
        "past_shows_count": pastshowsnum,
        "upcoming_shows": nextshows,
        "upcoming_shows_count": nextshowsnum
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
    venueFrm = VenueForm()
    
    # set the variables from Form Data
    name = venueFrm['name'].data
    city = venueFrm['city'].data
    state = venueFrm['state'].data
    address = venueFrm['address'].data
    phone = venueFrm['phone'].data
    facebook_link = venueFrm['facebook_link'].data
    image_link = venueFrm['image_link'].data
    website = venueFrm['website'].data
    seeking_talent = True if venueFrm['seeking_talent'].data == 'Yes' else False
    seeking_description = venueFrm['seeking_description'].data
    # hold the generes array that selected by form
    genres = venueFrm['genres'].data

    Create_venue_Error = False

    try:
        # Try to insert our venue Record
        print(name)
        newvenue = Venue()
        newvenue.name = name
        newvenue.city = city
        newvenue.state = state
        newvenue.address = address
        newvenue.phone = phone
        newvenue.seeking_talent = seeking_talent
        newvenue.seeking_description = seeking_description
        newvenue.image_link = image_link
        newvenue.website = website
        newvenue.facebook_link = facebook_link

        for itemven in genres:
            # lets work with each itemven
            getcomposition = db.session.query(RelationComposition).filter_by(name=itemven).one_or_none() # Raise an exception if there is duplicates found
            if getcomposition:
                # if we found a composition then append it to the venue genres
                newvenue.genres.append(getcomposition)
            else:
                # if the composition werent found create it
                newComposition = RelationComposition(name=itemven)
                db.session.add(newComposition)
                newvenue.genres.append(newComposition)
                
        db.session.add(newvenue)
        db.session.commit()
            
    except Exception as E:
        Create_venue_Error = True
        print(E)
        db.session.rollback()
    finally:
        db.session.close()
    if not Create_venue_Error:
        flash('Venue ' + request.form['name'] + ' Created !')
        return redirect(url_for('index'))
    else:
        flash('Venue ' + request.form['name'] + ' Not Created !')
        print("Error in create_venue_submission()")
        abort(500)
    



@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    
    getvenue = Venue.query.filter_by(id=venue_id).one()
    
    if not getvenue:
        return redirect(url_for('index'))

    Error_delete_venue = False
    
    try:
        venuename = getvenue.name
        db.session.delete(getvenue)
        db.session.commit()
    except Exception as E:
        Error_delete_venue = True
        print(E)
        db.session.rollback()
    finally:
        db.session.close()
    if Error_delete_venue:
        flash('Error deleteing ' + venuename + ' .')
        print("Error in delete_venue()")
        abort(500)
    else:
        flash(' Venue ' + venuename + ' is deleted.')
        return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # lets get all records from Artist table
    artists = Artist.query.order_by(Artist.id).all()
    # define and empty the data array to send it later
    datarray = []
    for artistitm in artists:
        datarray.append({
            "id": artistitm.id,
            "name": artistitm.name
        }) 
    return render_template('pages/artists.html', artists=datarray)



@app.route('/artists/search', methods=['POST'])
def search_artists():
    sterm = request.form.get('search_term', '').strip()
    artisResult  = Artist.query.filter(Artist.name.ilike('%' + sterm + '%')).all()

    datarray = []
    Currentime = datetime.now()

    for res in artisResult:
        upcommingshownum = len(db.session.query(Show).filter(Show.artist_id == res.id).filter(Show.start_time > Currentime).all())
        datarray.append({
            "id": res.id,
            "name": res.name,
            "num_upcoming_shows": upcommingshownum
            
            })

    searchCount = len(artisResult)
    response = {
        "count": searchCount,
        "data": datarray
        }
    
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
        
        




@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    getartist = Artist.query.filter_by(id=artist_id).one()

    if not getartist:
        return redirect(url_for('index'))
    
    genresarr = []
    currentTime = datetime.now()
    # populate genresarr from the getartist genre array that is listed in RelationComposition
    for genrevalue in getartist.genres:
        genresarr.append(genrevalue.name)
    # lets get all shows that is bigger than current Time .
    upcomingQ = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>currentTime).all()
    nextshows = []
    # lets get all shows that is smaller than current Time.
    pastshowsQ = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<currentTime).all()
    pastshows = []

    # lets loop on what we have and populate our arrays
    for showitem in upcomingQ:
        nextshows.append({
            "venue_id": showitem.venue_id,
            "venue_name": showitem.venue.name,
            "venue_image_link": showitem.venue.image_link,
            "start_time": currentdateformat(showitem.start_time)
            })
        
    for showitem in pastshowsQ:
        pastshows.append({
            "venue_id": showitem.venue_id,
            "venue_name": showitem.venue.name,
            "venue_image_link": showitem.venue.image_link,
            "start_time": currentdateformat(showitem.start_time)
            })
        
    #after we loop through our tables and compared the time and date of the show
    #now we can count what we have in our arrays
    nextshowsnum = 0
    pastshowsnum = 0
    nextshowsnum = len(nextshows) # check the len of our array
    pastshowsnum = len(pastshows) # check the len of our array

    print(nextshowsnum)
    print(pastshowsnum)

    data = {
        "id": artist_id,
        "name": getartist.name,
        "genres": genresarr,
        "city": getartist.city,
        "state": getartist.state,
        "phone": getartist.phone,
        "website": getartist.website,
        "facebook_link": getartist.facebook_link,
        "seeking_venue": getartist.seeking_venue,
        "seeking_description": getartist.seeking_description,
        "image_link": getartist.image_link,
        "past_shows": pastshows,
        "past_shows_count": pastshowsnum,
        "upcoming_shows": nextshows,
        "upcoming_shows_count": nextshowsnum
        }

    return render_template('pages/show_artist.html', artist=data)



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    getartist = Artist.query.filter_by(id=artist_id).one()
    if not getartist:
        # no atrist found with that id
        return redirect(url_for('index'))
    #artist_id found fill the form
    
    artform = ArtistForm(obj=getartist)
    genresarr = []

    for genrevalue in getartist.genres:
        genresarr.append(genrevalue.name)
        
    artist = {
        "id": artist_id,
        "name": getartist.name,
        "genres": genresarr,
        "city": getartist.city,
        "state": getartist.state,
        "phone": getartist.phone,
        "website": getartist.website,
        "facebook_link": getartist.facebook_link,
        "seeking_venue": getartist.seeking_venue,
        "seeking_description": getartist.seeking_description,
        "image_link": getartist.image_link
    }
    return render_template('forms/edit_artist.html', form=artform, artist=getartist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # lets edit the artist data
    artform = ArtistForm()
    # set the variables from Form Data
    artistid = artist_id
    name = artform['name'].data
    city = artform['city'].data
    state = artform['state'].data
    phone = artform['phone'].data
    facebook_link = artform['facebook_link'].data
    image_link = artform['image_link'].data
    website = artform['website'].data
    seeking_venue = True if artform['seeking_venue'].data == 'Yes' else False
    seeking_description = artform['seeking_description'].data

    # hold the generes array that selected by form
    genres = artform['genres'].data
    
    Edit_artist_Error = False
    try:
        getartistitem = db.session.query(Artist).filter_by(id=artistid).one()
        getartistitem.name = name
        getartistitem.city = city
        getartistitem.state = state
        getartistitem.phone = phone
        getartistitem.seeking_venue = seeking_venue
        getartistitem.seeking_description = seeking_description
        getartistitem.image_link = image_link
        getartistitem.website = website
        getartistitem.facebook_link = facebook_link
        # empty the artist genres array data to apply new once
        getartistitem.genres = []

        for itemg in genres:
            # lets work with each itemg
            getcomposition  = db.session.query(RelationComposition).filter_by(name=itemg).one_or_none() # Raise an exception if there is duplicates found
            
            if getcomposition:
                # if we found a composition then append it to the artist genres
                getartistitem.genres.append(getcomposition)
            else:
                # if the composition werent found create it
                newComposition = RelationComposition(name=itemg)
                db.session.add(newComposition)
                #append the new composition to the artist generes
                getartistitem.genres.append(newComposition)
              
        db.session.add(getartistitem)
        db.session.commit()
      
    except Exception as E:
        Edit_artist_Error = False
        print(E)
        db.session.rollback()
    finally:
        db.session.close()
    if not Edit_artist_Error:
        flash('Artist ' + name+ ' has been updated!')
        return redirect(url_for('show_artist', artist_id=artistid))
    else:
        flash('An error occurred. Artist ' + name + ' could not be updated.')
        print("Error in edit_artist_submission()")
        abort(500)
    
    
    


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    getvenueitem = Venue.query.filter_by(id=venue_id).one()

    if not getvenueitem:
        return redirect(url_for('index'))

    venueFrm = VenueForm(obj=getvenueitem)

    genresarr = []

    for genrevalue in getvenueitem.genres:
        genresarr.append(genrevalue.name)
    
    venue = {
        "id": venue_id,
        "name": getvenueitem.name,
        "genres": genresarr,
        "address": getvenueitem.address,
        "city": getvenueitem.city,
        "state": getvenueitem.state,
        "phone": getvenueitem.phone,
        "website": getvenueitem.website,
        "facebook_link": getvenueitem.facebook_link,
        "seeking_talent": getvenueitem.seeking_talent,
        "seeking_description": getvenueitem.seeking_description,
        "image_link": getvenueitem.image_link
    }
    return render_template('forms/edit_venue.html', form=venueFrm, venue=getvenueitem)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venueFrm = VenueForm()
    # set the variables from Form Data
    venueid = venue_id
    name = venueFrm['name'].data
    city = venueFrm['city'].data
    state = venueFrm['state'].data
    address = venueFrm['address'].data
    phone = venueFrm['phone'].data
    facebook_link = venueFrm['facebook_link'].data
    image_link = venueFrm['image_link'].data
    website = venueFrm['website'].data
    seeking_talent = True if venueFrm['seeking_talent'].data == 'Yes' else False
    seeking_description = venueFrm['seeking_description'].data
    # hold the generes array that selected by form
    genres = venueFrm['genres'].data

    Edit_Venue_Error = False

    try:
        getvenueitem = db.session.query(Venue).filter_by(id=venueid).one()
        getvenueitem.name = name
        getvenueitem.city = city
        getvenueitem.state = state
        getvenueitem.address = address
        getvenueitem.phone = phone
        getvenueitem.seeking_talent = seeking_talent
        getvenueitem.seeking_description = seeking_description
        getvenueitem.image_link = image_link
        getvenueitem.website = website
        getvenueitem.facebook_link = facebook_link
        # clearn the venueitem genres array to apply new once
        getvenueitem.genres = []

        for itemven in genres:
            # lets work with each itemven
            getcomposition = db.session.query(RelationComposition).filter_by(name=itemven).one_or_none() # Raise an exception if there is duplicates found
            if getcomposition:
                # if we found a composition then append it to the venue genres
                getvenueitem.genres.append(getcomposition)
            else:
                # if the composition werent found create it
                newComposition(name=itemven)
                db.session.add(newComposition)
                getvenueitem.genres.append(newComposition)

        db.session.add(getvenueitem)
        db.session.commit()
        
    except Exception as E:
        Edit_Venue_Error = True
        print(E)
        db.session.rollback()
    finally:
        db.session.close()
    if not Edit_Venue_Error:
        # if there is no Errors
        flash('Venue ' + name + ' has been updated !')
        return redirect(url_for('show_venue', venue_id=venueid))
    else:
        flash('An error occurred. Venue ' + name + ' could not be updated.')
        print("Error in edit_venue_submission()")
        abort(500)
        
    

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    artform = ArtistForm()
    # set the variables from Form Data
    name = artform['name'].data
    city = artform['city'].data
    state = artform['state'].data
    phone = artform['phone'].data
    facebook_link = artform['facebook_link'].data
    image_link = artform['image_link'].data
    website = artform['website'].data
    seeking_venue = True if artform['seeking_venue'].data == 'Yes' else False
    seeking_description = artform['seeking_description'].data

    # hold the generes array that selected by form
    genres = artform['genres'].data

    Create_artist_Error = False

    try:
        # Try to insert our Artist Record
        print(name)
        newartist = Artist()
        newartist.name = name
        newartist.city = city
        newartist.state = state
        newartist.phone = phone
        newartist.seeking_venue = seeking_venue
        newartist.seeking_description = seeking_description
        newartist.image_link = image_link
        newartist.website = website
        newartist.facebook_link = facebook_link

        print(genres)
        for itemg in genres:
            # lets work with each itemg
            getcomposition  = db.session.query(RelationComposition).filter_by(name=itemg).one_or_none() # Raise an exception if there is duplicates found

            if getcomposition:
                # if we found a composition then append it to the artist genres
                newartist.genres.append(getcomposition)
            else:
                # if the composition werent found create it
                newComposition = RelationComposition(name=itemg)
                db.session.add(newComposition)
                #append the new composition to the artist generes
                newartist.genres.append(newComposition) 
                
        db.session.add(newartist)
        db.session.commit()

    except Exception as E:
        Create_artist_Error = True
        print(E)
        db.session.rollback()
    finally:
        db.session.close()
    if not Create_artist_Error:
        flash('Artist ' + request.form['name'] + ' Created !')
        return redirect(url_for('index'))
    else:
        flash('Artist ' + request.form['name'] + ' Not Created !')
        print("Error in create_artist_submission()")
        abort(500)
    


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []
    shows = Show.query.all()
    
    for showitem in shows:
        data.append({
            "venue_id": showitem.venue.id,
            "venue_name": showitem.venue.name,
            "artist_id": showitem.artist.id,
            "artist_name": showitem.artist.name,
            "artist_image_link": showitem.artist.image_link,
            "start_time": currentdateformat(showitem.start_time),
            "show_name": showitem.show_name
        })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    showFrm = ShowForm()
    artistid = showFrm['artist_id'].data
    venueid = showFrm['venue_id'].data
    startTime = showFrm['start_time'].data
    showname = showFrm['show_name'].data

    # check if we have integer values for venueid and artistid
    if not venueid.isdigit():
        flash(f'Venue id Not Valid.')
        return render_template('pages/home.html')
    
    if not artistid.isdigit():
        flash(f'artid id Not valid.')
        return render_template('pages/home.html')

    # how ever if every thing is fine lets Try to create the show
    Create_show_Error = False

    try:
        #check if artis,venue are exists in our database
        venueidcheck = Venue.query.get(venueid)
        artistidcheck = Artist.query.get(artistid)
        
        if not venueidcheck:
            flash(f'Venue id Not Found.')
            return render_template('pages/home.html')

        if not artistidcheck:
            flash(f'artist id Not Found.')
            return render_template('pages/home.html')
    
        newshow = Show()
        newshow.show_name = showname
        newshow.artist_id = artistid
        newshow.venue_id = venueid
        newshow.start_time = startTime
        db.session.add(newshow)
        db.session.commit()
    except Exception as E:
        Create_show_Error = True
        print(E)
        db.session.rollback()
    finally:
        db.session.close()
        
    if not Create_show_Error:
        # if there is no Errors
        flash('Show ' + showname + ' is Created .')
    else:
        flash('Show ' + showname + ' did Not Created .')

    return render_template('pages/home.html')




@app.route('/shows/<int:show_id>')
def shows_show(show_id):
    data = []
    show = Show.query.filter_by(id=show_id).one()
    if not show:
        return redirect(url_for('index'))

    data.append({
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": currentdateformat(show.start_time),
        "show_name": show.show_name
        })

    return render_template('pages/show.html', shows=data)
    
     


@app.route('/shows/search', methods=['POST'])
def search_shows():
    # Search Shows
    search_term = request.form.get('search_term', '').strip()
    shows = Show.query.filter(Show.show_name.ilike('%' + search_term + '%')).all()
    data = []
    for show in shows:

        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": currentdateformat(show.start_time),
            "show_name": show.show_name
        })
   

    return render_template('pages/show.html', shows=data)


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

# -> Run the server
if __name__ == "__main__":
    app.run(host="localhost", port=4000, debug=False)
