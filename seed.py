"""Seed file to make sample data for users db."""

from models import User, Search_History, db   	# Don’t forget db!
from app import app

with app.app_context():

    # Drop & create all tables

    db.drop_all()
    db.create_all()


    # If table isn't empty, empty it
    User.query.delete()

    # Add users
    q = User(user_name = 'Anon', user_pwd = "a")
    t = User(user_name = '222', user_pwd = "222")
    a = User(user_name = 'aaa', user_pwd = "aaa")
    z = User(user_name = 'zzz', user_pwd = "zzz")
    p = User(user_name = 'Pat', user_pwd = "pp")

    # Add new objects to session, so they'll persist
    db.session.add_all([q,t,a,z,p])			# or put the variables in a list and add_all()

    # Commit-otherwise, this never gets saved!
    db.session.commit()

     # If table isn't empty, empty it
    Search_History.query.delete()

    # Add Search History
    a = Search_History(
        user_id = 1, 
        search_date = "2024-09-25", 
        event_date = "Dec 12", 
        event_location = "Space Needle", 
        no_of_years = 5,
        temp = '72',
        prcp = '20.0')
    
    b = Search_History(
        user_id = 2, 
        search_date = "2024-09-25", 
        event_date = "May 14", 
        event_location = "Key West", 
        no_of_years = 3,
        temp = '72',
        prcp = '20.0')
    
    c = Search_History(
        user_id = 2, 
        search_date = "2024-09-25", 
        event_date = "July 30", 
        event_location = "63132", 
        no_of_years = 10,
        temp = '72',
        prcp = '20.0')
    
    d = Search_History(
        user_id = 5, 
        search_date = "2024-09-25", 
        event_date = "Mar 6", 
        event_location = "Grand Canyon", 
        no_of_years = 3,
        temp = '72',
        prcp = '20.0')

    # Add new objects to session, so they'll persist
    db.session.add_all([a,b,c,d])			# or put the variables in a list and add_all()

    # Commit-otherwise, this never gets saved!
    db.session.commit()
   
