from app import db
from datetime import datetime, timezone

class RelationComposition(db.Model):
    __tablename__ = 'RelationComposition'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


# Create Association table to hold the relatiion between Artist and RelationComposition (Many-to-many)
CompositionsAssociation_Atrist = db.Table('compositionsAssociation_Atrist',
    db.Column('genre_id', db.Integer, db.ForeignKey('RelationComposition.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

# Create Association table to hold the relatiion between venue and RelationComposition Many-to-many
CompositionsAssociation_Venue = db.Table('compositionsAssociation_Venue',
    db.Column('genre_id', db.Integer, db.ForeignKey('RelationComposition.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)




class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # linking the venue table for manytomany relationship with CompositionsAssociation venue table
    genres = db.relationship('RelationComposition', secondary=CompositionsAssociation_Venue, backref=db.backref('venues'))
    #--------------------------------------------------------------------#
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', passive_deletes=True, lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    #genres = db.Column(db.String(120)) this genres is no longer needed
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    #linking the artist table for manytomany relationship with CompositionsAssociation Artist table
    genres = db.relationship('RelationComposition', secondary=CompositionsAssociation_Atrist, backref=db.backref('artists'))
    #--------------------------------------------------------------------#
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', passive_deletes=True, lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    show_name = db.Column(db.String)

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time} artist_id={artist_id} venue_id={venue_id}>'
