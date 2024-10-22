from flask import Flask, render_template, redirect, request, flash, session, url_for
from static.extensions import bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from forms import AddressForm, UserForm
from models import db, connect_db, User
from process.functions import reset, calculate_prediction, in_the_USA, log_event, location, fips, process_dates, dates_to_use, login
import logging
import os
# from process.my_secrets import secret_key, db_conn
from datetime import datetime

app = Flask(__name__)  
bcrypt.init_app(app)

app.debug = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.getenv('secret_key')    # secret_key

<<<<<<< HEAD
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('db_conn') 	# db_conn	
=======
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn	
>>>>>>> c712bad (Made some changes to the password functionality.)
app.config['ENV'] = 'development'

with app.app_context():
    connect_db(app)
    db.create_all()
	
debug = DebugToolbarExtension(app)

logging.basicConfig(
    level=logging.CRITICAL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app_log.log',
    filemode='w'  # 'a' for append mode, 'w' to overwrite the file
)

#-----------------------------------------------------------------------
# There are only 2 routes: (1) home and (2) get_data

@app.route('/', methods=['GET', 'POST'])
def home():
	"""Homepage with the form to enter address & date"""
	logging.critical('---------- Starting App ---------') 
	addressForm = AddressForm()
	userForm = UserForm() 
	# if the homepage is a POST request, process the user inputs:
	if request.method == 'POST':
		# Get the user entered data from the form
		if addressForm.validate_on_submit():
			address = addressForm.address.data
			date = addressForm.date.data
			search_years = addressForm.search_years.data
			# Set search years to session
			session['search_years'] = search_years

			# Send user to get_data
			return redirect(url_for('confirm', address=address, date=date, search_years=search_years))
		
		# If the address/date form failed
		flash("FORM VALIDATION FAILED", 'danger')
		logging.error('Address & Date verification failed.')
		return redirect('/')
	
	# If the homepage is a GET request clear session variables (if any) and show the form:
	reset()
	return render_template('home.html', addressForm = addressForm, userForm = userForm)


@app.route('/confirm', methods=['GET','POST'])
def confirm():
	"""Asks user to verify info is correct and if confirmed; sends App to get_weather."""
	# if coming from the CONFIRMED button on this route
	if request.method == 'POST':

		print("Confirm route is a post, and I don't have a route for this")
		return redirect('/')
	
	# if coming from the homepage for REVIEW
	address=request.args.get('address')
	date=request.args.get('date')
	# cast the date as a datetime object
	event_date = datetime.strptime(date, "%Y-%m-%d")
	
	# Set Event Date as a flask session variable
	session['event_date'] = event_date

	# Get the formatted address and lat/long of the address from Google and save to session
	location_data = location(address)

	# Update address object to the Google formatted address
	address = location_data.get('address')
			
	# Get the fips from functions.py
	found_fips = fips()
	print(f'FCC determined FIPS: {found_fips}')
		
	# Verify that the event location is in the USA (foreign weather info not available)
	if not in_the_USA(address):
		flash('Currently we only have weather data for the USA - Sorry!', 'danger')
		return redirect('/')

	return render_template('/confirm.html', address=address, event_date=event_date)
# END confirm route


"""Process the request, get and perform the calculations."""
@app.route('/get_data', methods=['GET','POST'])
def get_data():
	"""Gets the weather data"""
	# if coming from the CONFIRMED page
	if request.method == 'POST':

		#  1. The lat/long and address from Address were already determined in the GET route below, and saved to the session
		
		#  2. fips was already determined in the GET route below

		#  3. Send user to get the weather history - get_weather

		# Get the dates to use for weather history
		search_years = session.get('search_years')
		past_dates = dates_to_use(int(search_years))

		# Get the weather data for those dates
		daily_summary_dict = process_dates( past_dates, session.get('fips') ) # returns true

		# Calculate prediction
		prediction = calculate_prediction()

		log_event(prediction)
		
		# Load the results page
		return render_template('display_prediction.html', prediction=prediction, daily_summary_dict=daily_summary_dict)
	
	# if coming from the homepage for REVIEW
	print("Get_data sent a GET request. I don't have a route for that.")

	return redirect('/')
# END get data route


@app.route('/register', methods=['GET','POST'])
def register():
	"""Register OR log in a user."""

	userForm = UserForm() 
	
	if request.method == 'POST':
		# Get the user entered data from the form
		if userForm.validate_on_submit():

			entered_username = userForm.username.data
			entered_password = userForm.password.data
			hashed_pw = bcrypt.generate_password_hash(entered_password).decode('utf-8')

			if not entered_username or not entered_password :
				flash("Both Username & Password are required.", "danger")

			users = User.query.filter(User.user_name == entered_username).first()
			
			# New User - Register
			if userForm.submit_button_register.data:
				if users:
					# username already exists in datbase
					flash("Username not available.", "danger")
					return redirect('/')				
				try: 
					new_user = User(user_name = entered_username, user_pwd = hashed_pw)

					db.session.add(new_user)
					db.session.commit()
					# Create user object once it has an id
					set_user = {"user_id": new_user.user_id, "username":new_user.user_name}
					session['user'] = set_user

					flash(f"Welcome {entered_username}!", "success")
				except Exception as err:
					print('** ERROR writing to the database **', err)
				print("Registration completed succesfully, redirecting to home page")
				return redirect('/')
			
			# Existing User - Login
			elif userForm.submit_button_login.data:
					
					if not users:
						# If username is not found in database
						flash("Username not found, please try again.", "danger")
					else :
						# username is in database
						login(entered_username, entered_password)

					return redirect('/')
	
	else:
		print("Did not get the info back from the form")


@app.route('/logout')
def logout():
	"""User log out."""
	
	session.pop('user', None)

	return redirect('/')
