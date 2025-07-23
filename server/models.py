from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Table

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

session_speaker = db.Table(
    'session_speaker',
    db.Column('session_id', db.Integer, db.ForeignKey('sessions.id'), primary_key=True),
    db.Column('speaker_id', db.Integer, db.ForeignKey('speakers.id'), primary_key=True)
)

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)

    sessions = db.relationship(
        'Session',
        back_populates='event',
        cascade='all, delete, delete-orphan'
    )
    
    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', location='{self.location}')>"

class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    event = db.relationship('Event', back_populates='sessions')
    
    speakers = db.relationship(
        'Speaker',
        secondary=session_speaker,
        back_populates='sessions'
    )
    
    def __repr__(self):
        return (f"<Session(id={self.id}, title='{self.title}', start_time={self.start_time}, "
                f"event_id={self.event_id})>")

class Speaker(db.Model):
    __tablename__ = 'speakers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    
    bio = db.relationship(
        'Bio',
        back_populates='speaker',
        uselist=False,
        cascade='all, delete, delete-orphan'
    )
    
    sessions = db.relationship(
        'Session',
        secondary=session_speaker,
        back_populates='speakers'
    )
    
    def __repr__(self):
        return f"<Speaker(id={self.id}, name='{self.name}')>"

class Bio(db.Model):
    __tablename__ = 'bios'

    id = db.Column(db.Integer, primary_key=True)
    bio_text = db.Column(db.String, nullable=False)
    
    speaker_id = db.Column(db.Integer, db.ForeignKey('speakers.id'), nullable=False)
    speaker = db.relationship('Speaker', back_populates='bio')
    
    def __repr__(self):
        return f"<Bio(id={self.id}, speaker_id={self.speaker_id}, bio_text='{self.bio_text[:30]}...')>"

class Earthquake(db.Model):
    __tablename__ = 'earthquakes'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String, nullable=False)
    magnitude = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Earthquake {self.location}, Mag {self.magnitude}, Year {self.year}>"
