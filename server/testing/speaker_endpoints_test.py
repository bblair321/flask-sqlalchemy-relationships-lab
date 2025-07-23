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
            speaker1 = Speaker(name="Alex Johnson")
            speaker2 = Speaker(name="Riley Chen")
            speaker3 = Speaker(name="Jordan Brooks")
            db.session.add_all([speaker1, speaker2, speaker3])
            db.session.commit()

            bio1 = Bio(bio_text="Expert in scalable backend systems with 10+ years of experience.", speaker=speaker1)
            db.session.add(bio1)
            db.session.commit()

            event1 = Event(name="Tech Future Conference", location="New York")
            db.session.add(event1)
            db.session.commit()

            session1 = Session(title="Building Scalable Web Apps", start_time=datetime.datetime(2023, 9, 15, 10, 0), event=event1)
            db.session.add(session1)
            db.session.commit()

            session1.speakers.append(speaker1)
            db.session.commit()

        yield client
        with app.app_context():
            db.drop_all()

def test_get_speakers_success(test_client):
    response = test_client.get("/speakers")
    assert response.status_code == 200
    speakers = response.get_json()
    assert isinstance(speakers, list)
    assert len(speakers) > 0
    found_speaker_with_bio = False
    found_speaker_without_bio = False
    for speaker_data in speakers:
        if speaker_data["name"] == "Alex Johnson":
            assert "bio" in speaker_data
            assert speaker_data["bio"] is not None
            assert "bio_text" in speaker_data["bio"]
            found_speaker_with_bio = True
        elif speaker_data["name"] == "Jordan Brooks":
            assert "bio" in speaker_data
            assert speaker_data["bio"] is None
            found_speaker_without_bio = True
    assert found_speaker_with_bio
    assert found_speaker_without_bio


def test_get_speaker_with_bio(test_client):
    speaker = db.session.query(Speaker).filter_by(name="Alex Johnson").first()
    response = test_client.get(f"/speakers/{speaker.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "id" in data
    assert "name" in data
    assert "bio" in data
    assert data["bio"] is not None
    assert "bio_text" in data["bio"]
    assert data["bio"]["bio_text"] == "Expert in scalable backend systems with 10+ years of experience."
    assert "sessions" in data
    assert isinstance(data["sessions"], list)


def test_get_speaker_without_bio(test_client):
    speaker_without_bio = db.session.query(Speaker).filter_by(name="Jordan Brooks").first()
    response = test_client.get(f"/speakers/{speaker_without_bio.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "id" in data
    assert "name" in data
    assert "bio" in data
    assert data["bio"] is None
    assert "sessions" in data
    assert isinstance(data["sessions"], list)


def test_get_speaker_not_found(test_client):
    response = test_client.get("/speakers/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert data == {"message": "Speaker with id 9999 not found"}
