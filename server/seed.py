#!/usr/bin/env python3
from app import app
from models import db, Event, Session, Speaker, Bio
import datetime
import os # Import the os module for file operations
import sys # Import sys for exiting

print("--- Starting seed.py script ---")

with app.app_context():
    # Define the path to the database file
    db_path = 'app.db'
    print(f"--- Database file path: {db_path} ---")

    # Ensure a clean database file every time the script runs
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"--- Successfully removed existing database file: {db_path} ---")
        except OSError as e:
            print(f"!!! ERROR: Could not remove existing database file {db_path}: {e} !!!")
            print("!!! Please ensure the file is not in use by another process and you have write permissions. Exiting. !!!")
            sys.exit(1) # Exit if we can't remove the old DB
    else:
        print(f"--- No existing database file '{db_path}' found. Proceeding to create. ---")

    # CREATE ALL TABLES FIRST
    try:
        db.create_all()
        print("--- Database tables created successfully. ---")
    except Exception as e:
        print(f"!!! ERROR: Could not create database tables: {e} !!!")
        print("!!! This might indicate an issue with your models.py or SQLAlchemy setup. Exiting. !!!")
        sys.exit(1) # Exit if table creation fails
    
    # Clear all table data - but handle missing tables gracefully
    # This block should now only run if tables were successfully created
    try:
        # Corrected table name for deletion (should be 'session_speaker', singular)
        print("--- Attempting to clear session_speaker table... ---")
        db.session.execute(db.text('DELETE FROM session_speaker'))
        db.session.commit() # Commit the deletion
        print("--- Cleared session_speaker table successfully. ---")
    except Exception as e:
        # This warning should ideally not happen if db.create_all() succeeded
        print(f"Warning: Could not clear session_speaker table (might be empty or other issue): {e}")
        db.session.rollback() # Rollback in case of an error during deletion
    
    # Clear data from other tables
    print("--- Clearing data from Bio, Session, Speaker, and Event tables... ---")
    Bio.query.delete()
    Session.query.delete()
    Speaker.query.delete()
    Event.query.delete()
    db.session.commit()
    print("--- Cleared Bio, Session, Speaker, and Event tables successfully. ---")
    
    # Create Events
    print("--- Creating Events... ---")
    event1 = Event(name="Tech Future Conference", location="New York")
    event2 = Event(name="AI World Summit", location="San Francisco")
    db.session.add_all([event1, event2])
    db.session.commit()
    print("--- Created Events. ---")
    
    # Create Sessions
    print("--- Creating Sessions... ---")
    session1 = Session(title="Building Scalable Web Apps", start_time=datetime.datetime(2023, 9, 15, 10, 0), event=event1)
    session2 = Session(title="Intro to Machine Learning", start_time=datetime.datetime(2023, 9, 15, 14, 0), event=event1)
    session3 = Session(title="The Future of AI Ethics", start_time=datetime.datetime(2023, 10, 20, 11, 0), event=event2)
    db.session.add_all([session1, session2, session3])
    db.session.commit()
    print("--- Created Sessions. ---")
    
    # Create Speakers
    print("--- Creating Speakers... ---")
    speaker1 = Speaker(name="Alex Johnson")
    speaker2 = Speaker(name="Riley Chen")
    speaker3 = Speaker(name="Jordan Brooks")
    db.session.add_all([speaker1, speaker2, speaker3])
    db.session.commit()
    print("--- Created Speakers. ---")
    
    # Create Bios
    print("--- Creating Bios... ---")
    bio1 = Bio(bio_text="Expert in scalable backend systems with 10+ years of experience.", speaker=speaker1)
    bio2 = Bio(bio_text="AI researcher focusing on machine learning and data ethics.", speaker=speaker2)
    bio3 = Bio(bio_text="Software engineer passionate about teaching and open source.", speaker=speaker3)
    db.session.add_all([bio1, bio2, bio3])
    db.session.commit()
    print("--- Created Bios. ---")
    
    # Associate Speakers and Sessions
    print("--- Associating Speakers and Sessions... ---")
    session1.speakers.append(speaker1)
    session2.speakers.append(speaker2)
    session2.speakers.append(speaker3)
    session3.speakers.append(speaker2)
    db.session.commit()
    print("--- Associated Speakers and Sessions. ---")
    
    print("Database seeded successfully! ---")
