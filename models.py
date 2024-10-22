from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  		# create variable to run SQLAlchemy / connect to database

#Put the connection in a function so it doesn't run immediately and unnecessarily.
def connect_db(app):
        db.app = app  			# associate flask app with the db variable
        db.init_app(app)   		# initialize

# models go below
class User(db.Model):
        """User table"""

        __tablename__ = "users"
        user_id = db.Column(db.Integer, primary_key = True)
        user_name = db.Column(db.String, nullable=False, unique=True)

        user_pwd = db.Column(db.Text, nullable=False, unique=False)


class Search_History(db.Model):
        """contains the user's search history"""

        __tablename__ = "search_history"

        id = db.Column(db.Integer, primary_key = True)
        user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
        search_date = db.Column(db.String)
        event_date = db.Column(db.String)
        event_location = db.Column(db.String)
        no_of_years = db.Column(db.Integer)
        temp = db.Column(db.String)
        prcp = db.Column(db.String)