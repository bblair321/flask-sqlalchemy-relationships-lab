import pytest
from app import app, db
from models import Event, Session, Speaker, Bio
import datetime

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            event1 = Event(name="Tech Conference", location="Virtual")
            event2 = Event(name="AI Summit", location="San Francisco")
            db.session.add_all([event1, event2])
            db.session.commit()

            session1 = Session(title="Future of AI", start_time=datetime.datetime(2024, 6, 1, 9, 0), event=event1)
            session2 = Session(title="Web Dev Best Practices", start_time=datetime.datetime(2024, 6, 1, 11, 0), event=event1)
            db.session.add_all([session1, session2])
            db.session.commit()

            speaker1 = Speaker(name="Jane Doe")
            speaker2 = Speaker(name="John Smith")
            db.session.add_all([speaker1, speaker2])
            db.session.commit()

            bio1 = Bio(bio_text="Expert in AI and ML.", speaker=speaker1)
            db.session.add(bio1)
            db.session.commit()

            session1.speakers.append(speaker1)
            session2.speakers.append(speaker2)
            db.session.commit()

        yield client
        with app.app_context():
            db.drop_all()

def test_get_events_success(test_client):
    response = test_client.get("/events")
    assert response.status_code == 200
    events = response.get_json()
    assert isinstance(events, list)
    assert len(events) > 0
    assert events[0]["name"] == "Tech Conference"

def test_get_event_sessions_success(test_client):
    event = db.session.query(Event).filter_by(name="Tech Conference").first()
    response = test_client.get(f"/events/{event.id}/sessions")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)
    assert "sessions" in data
    assert isinstance(data["sessions"], list)
    assert len(data["sessions"]) > 0
    assert data["event_id"] == event.id
    assert data["event_name"] == event.name

    first_session = data["sessions"][0]
    assert "id" in first_session
    assert "title" in first_session
    assert "start_time" in first_session
    assert "speakers" in first_session
    assert isinstance(first_session["speakers"], list)

def test_get_event_sessions_not_found(test_client):
    response = test_client.get("/events/9999/sessions")
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"message": "Event with id 9999 not found"}

