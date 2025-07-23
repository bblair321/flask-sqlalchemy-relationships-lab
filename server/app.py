from flask import Flask, jsonify
from flask_migrate import Migrate

from models import db, Event, Session, Speaker, Bio

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/earthquakes/<int:id>', methods=['GET'])
def get_earthquake_by_id(id):
    quake = Earthquake.query.get(id)
    if quake:
        return jsonify({
            "id": quake.id,
            "location": quake.location,
            "magnitude": quake.magnitude,
            "year": quake.year
        }), 200
    else:
        return jsonify({"message": f"Earthquake {id} not found."}), 404

@app.route('/earthquakes/magnitude/<float:magnitude>', methods=['GET'])
def get_earthquakes_by_magnitude(magnitude):
    quakes = Earthquake.query.filter(Earthquake.magnitude >= magnitude).all()
    return jsonify({
        "count": len(quakes),
        "quakes": [
            {
                "id": q.id,
                "location": q.location,
                "magnitude": q.magnitude,
                "year": q.year
            } for q in quakes
        ]
    }), 200

@app.route('/events', methods=['GET'])
def get_events():
    """
    Retrieves all events.
    """
    events = Event.query.all()
    events_data = []
    for event in events:
        events_data.append({
            "id": event.id,
            "name": event.name,
            "location": event.location
        })
    return jsonify(events_data), 200


@app.route('/events/<int:event_id>/sessions', methods=['GET'])
def get_event_sessions(event_id):
    """
    Retrieves all sessions associated with a specific event,
    including details for each session's speakers and their bios.
    """
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"message": f"Event with id {event_id} not found"}), 404

    sessions_data = []
    for session in event.sessions:
        speakers_data = []
        for speaker in session.speakers:
            bio_data = None
            if speaker.bio:
                bio_data = {
                    "id": speaker.bio.id,
                    "bio_text": speaker.bio.bio_text
                }
            speakers_data.append({
                "id": speaker.id,
                "name": speaker.name,
                "bio": bio_data
            })
        sessions_data.append({
            "id": session.id,
            "title": session.title,
            "start_time": session.start_time.isoformat(),
            "speakers": speakers_data
        })
    
    return jsonify({
        "event_id": event.id,
        "event_name": event.name,
        "sessions": sessions_data
    }), 200


@app.route('/speakers', methods=['GET'])
def get_speakers():
    """
    Retrieves all speakers, including their associated bio.
    """
    speakers = Speaker.query.all()
    speakers_data = []
    for speaker in speakers:
        bio_data = None
        if speaker.bio:
            bio_data = {
                "id": speaker.bio.id,
                "bio_text": speaker.bio.bio_text
            }
        speakers_data.append({
            "id": speaker.id,
            "name": speaker.name,
            "bio": bio_data
        })
    return jsonify(speakers_data), 200


@app.route('/speakers/<int:speaker_id>', methods=['GET'])
def get_speaker(speaker_id):
    """
    Retrieves a single speaker by ID, including their associated bio and sessions.
    """
    speaker = Speaker.query.get(speaker_id)
    if not speaker:
        return jsonify({"message": f"Speaker with id {speaker_id} not found"}), 404
    
    bio_data = None
    if speaker.bio:
        bio_data = {
            "id": speaker.bio.id,
            "bio_text": speaker.bio.bio_text
        }
    
    sessions_data = []
    for session in speaker.sessions:
        sessions_data.append({
            "id": session.id,
            "title": session.title,
            "start_time": session.start_time.isoformat(),
            "event_id": session.event_id
        })

    return jsonify({
        "id": speaker.id,
        "name": speaker.name,
        "bio": bio_data,
        "sessions": sessions_data
    }), 200


@app.route('/sessions/<int:session_id>/speakers', methods=['GET'])
def get_session_speakers(session_id):
    """
    Retrieves all speakers associated with a specific session,
    including details for each speaker's bio.
    """
    session = Session.query.get(session_id)
    if not session:
        return jsonify({"message": f"Session with id {session_id} not found"}), 404

    speakers_data = []
    for speaker in session.speakers:
        bio_data = None
        if speaker.bio:
            bio_data = {
                "id": speaker.bio.id,
                "bio_text": speaker.bio.bio_text
            }
        speakers_data.append({
            "id": speaker.id,
            "name": speaker.name,
            "bio": bio_data
        })
    
    return jsonify({
        "session_id": session.id,
        "session_title": session.title,
        "speakers": speakers_data
    }), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(port=5555, debug=True)
