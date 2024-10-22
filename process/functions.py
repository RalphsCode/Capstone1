"""This is where the functions that get and process the data are kept."""
from flask import session, flash, make_response
import requests
import statistics
# from process.my_secrets import Google_API_KEY, NOAA_token
from models import db, connect_db, Search_History, User
from datetime import datetime
import os
from static.extensions import bcrypt

# Set global dictionary to hold the calculated weather history data
weather_history_dict = {
    'TAVG_history' : [],
    'PRCP_history' : []
    }

daily_summary_dict = {}

g_key = os.getenv('Google_API_KEY')   #  Google_API_KEY 
NOAA_token = os.getenv('NOAA_token')    #  NOAA_token 

"""
---------------------------------------------------------------
Function A: Make a list of dates to use for weather history
----------------------------------------------------------------
"""
def dates_to_use(search_years):
    """Function to determine the dates in the past to use in the weather history queries"""
    event_day = session["event_date"].strftime("%d")
    event_month = session["event_date"].strftime("%m")

    # Make a list of the dates for the previous passed in number of years
    year = 2024
    past_dates = []
    for num in range(search_years):
            year = year -1
            date = f"{year}-{event_month}-{event_day}"
            past_dates.append(date)
    return past_dates


"""
---------------------------------------------------------------
Function B: For each date in the past_dates list; 
(1) get the weather history from NCDC API call, 
(2) Parse the needed data elements from the weather history data (TAVG, and PRCP)
----------------------------------------------------------------
"""
def process_dates(past_dates, fips):
    """Get the weather history from NCDC API call, 
and extract TAVG, and PRCP data"""

    print(f"Starting to aquire data for a year... FIPS: {fips}.")

    global daily_summary_dict 

    for date in past_dates:
        # Process each annual date.
        try:
            # Get the year's weather history from NOAA
            weather_data = get_weather_history(date, fips)

            # Extract needed data points

            # TAVG - Temp Average
            extract_data_points(weather_data, "TAVG")

            # PRCP - Precipitation
            extract_data_points(weather_data, "PRCP")

            # Place the day in history into a dictionary
            summarize_day_in_history(date)

            # Adding a .25 second delay to prevent overwhelming the server/API
            # time.sleep(0.25)  

        except Exception as e:
            location_data = session.get('location_data')
            flash(f"Not able to retrieve weather history for '{location_data.get('address', 'that location')}. Either the location has no weather history data, or the NOAA API server is down.", 'danger')
            print(f"Error aquiring weather data. Was on date {date}: {e}")

    return daily_summary_dict
# END process_dates()


"""
-----------------------------------------------------------------
Function C: Verify event location is in the USA
----------------------------------------------------------------
"""
def in_the_USA(address):
   """Verify if the address returned from the Google API is in the USA"""

   if "USA" not in address and "United States" not in address:
       return False
   return True
# END in_the_usa()


"""
---------------------------------------------------------------
Function 1 get the Lat/Long and formatted address for the event location from the Google Places API
----------------------------------------------------------------
"""

def location(address):
    """Query Google places API to get the Lat/Long of the user entered location"""

    # API endpoint
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={address}&key={g_key}"
    
    # Sending GET request to the API
    response = requests.get(url)
    
    # Checking if the request was successful
    if response.status_code == 200:
        # Parsing the JSON response
        data = response.json()
        # Extracting the lat / long & formatted address
        lat = data['results'][0]['geometry']['location']['lat']
        long = data['results'][0]['geometry']['location']['lng']
        address = data['results'][0]['formatted_address']

        # Create a data dictionary with the results
        location_data = {"address": address, "lat":lat, "long":long}

        # Set the 'location_data' session variable
        session['location_data']= location_data

        # Return the Lat/Long & formatted address dictionary
        return location_data
    
    else:
        # Handling errors
        return f"Failed to get Lat/Long data for {address} from the Google API. Error code: {response.status_code}"
# END location()



"""
------------------------------------------------------------------
Function 2 get the FIPS code encompassing the event location using the event's Lat/Long
------------------------------------------------------------------
"""

def fips():
    """Using the Gov't FCC API to return the FIPS code for the Lat/long of the user location"""
    ll = session.get('location_data', {})
    lat = ll.get('lat', 'No latitude present')
    long = ll.get('long', 'No longitude present')
    # API endpoint
    url = f"https://geo.fcc.gov/api/census/block/find?format=json&latitude={lat}&longitude={long}&showall=true"
    
    # Sending GET request to the API
    response = requests.get(url)
    
    # Checking if the request was successful
    if response.status_code == 200:
        # Parsing the JSON response
        data = response.json()
        # Extracting the FIPS
        fips = data['County']['FIPS']
        # *****  Return the FIPS code  *****
        session['fips'] = fips
        ############### ADD COUNTY NAME ###########
        return fips
    else:
        # Handling errors
        return f"Failed to get FIPS for the event address from the FCC API. Error code: {response.status_code}"
# END fips()
    


"""
-----------------------------------------------------------------
Function 3: Get the weather history for the FIPS location for the previous 10 years
----------------------------------------------------------------
"""
def get_weather_history(date, fips):
    """Retrieve the TAVG and PRCP weather history for the FIPS code (County)"""

    # API endpoint
    url = f"https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&startdate={date}&enddate={date}&datatypeid=PRCP,TAVG&units=standard&limit=1000&locationid=FIPS:{fips}&includeStationLocation=True" 
    headers= {"token": NOAA_token}
    
    # Sending GET request to the API
    response = requests.get(url, headers=headers, timeout=158)

    # START DETOUR #######################################################
    # NCDC API SERVER DOWN USE THIS:
    # Get the file path
    # file_path = os.path.join(os.getcwd(), 'response', '../static/test_data.json')

    # # Open the file and read its content
    # with open(file_path, 'r') as file:
    #     response = file.read()
    # END DETOUR #########################################################
    
    # Checking if the request was successful
    if response.status_code == 200:
        # Parsing the JSON response
        data = response.json()
        print(f"Weather Data Sucessfully received for: {date}.")

        return data
    
    else:
        # Handling errors
        return f"Failed to get Weather History from NCDC API. Error code: {response.status_code}"
# END get_weather_history()



"""
-----------------------------------------------------------------
Function 4: Extract the needed weather history elements from the NCDC JSON data
----------------------------------------------------------------
"""
def extract_data_points(data, parameter):
    """Function to get the passed in paramater (TAVG / PRCP) from the weather JSON data and store it in a global dictionary"""

    for station in data['results']:
        # if a station is reporting the needed data point
        global weather_history_dict
        if station['datatype']== parameter:
            # Add datapoint to dictionary
            weather_history_dict[f'{parameter}_history'].append(station['value'])

    return True
# END extract_data_points()


"""
-----------------------------------------------------------------
Function 5: Summarize and save to a dict the weather history for a day in the past
----------------------------------------------------------------
"""
def summarize_day_in_history(date):
    """Summarize the daily data, and save it to the daily_summary_dict      
    """
    global daily_summary_dict, weather_history_dict
    # Calculate the TAVG mediam and assign it
    TAVG = statistics.median(weather_history_dict['TAVG_history'])

    # Set PRCP to True or False
    rain_count = 0
    for prcp in weather_history_dict['PRCP_history']:
        if prcp > 0.0:
            rain_count += 1
    if rain_count >= (len(weather_history_dict['PRCP_history'])/2):
        PRCP = True
    else:
        PRCP = False

    # Store the daily weather history in the summary dictionary
    daily_summary_dict[date] = {
        'TAVG': round(TAVG, 0),
        'PRCP': PRCP
        }
    return True
# END summarize_day_in_history()


    """
-----------------------------------------------------------------
Function 6: Reset the Data
----------------------------------------------------------------
"""
def reset():
    global weather_history_dict
    weather_history_dict = {
    'TAVG_history' : [],
    'PRCP_history' : []
    }

    global daily_summary_dict
    daily_summary_dict = {}

    session['event_date'] = None
    session['location_data'] = None
    session['search_years'] = None
    session['fips'] = None

    print('******* session variables reset ******')

# END reset()


"""
-----------------------------------------------------------------
Function 7: Distill the Data and make weather prediction
----------------------------------------------------------------
"""
def calculate_prediction():
    
    global daily_summary_dict

    # Calculate the Average temp from the historic weather data
    tavg_values = [data['TAVG'] for data in daily_summary_dict.values()]
    # Calculate mean TAVG
    mean_tavg = sum(tavg_values) / len(tavg_values) if tavg_values else 0
    # print result
    print('mean_tavg:', round(mean_tavg, 1) )

    # Calculate the precipitation percentage from the historic weather data
    # Count total number of days
    total_days = len(daily_summary_dict)

    # Count the number of rain days
    rain_days = sum(1 for data in daily_summary_dict.values() if data['PRCP'])

    # Calculate the percentage of rain days
    rain_percentage = (rain_days / total_days) * 100 if total_days > 0 else 0

    # Print result
    print(f"Percentage of Rain Days: {rain_percentage:.0f}%")

    prediction = {'temp_prediction': round(mean_tavg, 1), 'prcp_prediction': round(rain_percentage, 0) }

    return prediction
 
# END calculate_prediction()


def log_event(prediction):
    "Log the weather prediction in the database"
    global daily_summary_dict
    # with app.app_context():
    #     connect_db(app)
    #     db.create_all()

    # Check if a user is logged in
    if session.get('user') :
        user_id = session['user']['user_id']
    else :
        # No user logged in
        user_id = 1

    temp_prediction = prediction['temp_prediction']
    prcp_prediction = prediction['prcp_prediction']

    new_event = Search_History(
            user_id = user_id, 
            search_date = datetime.now(), 
            event_date= session['event_date'], 
            event_location = session['location_data']['address'], 
            no_of_years = int(session['search_years']),
            temp = temp_prediction,
            prcp = prcp_prediction
            )   
    
    db.session.add(new_event)
    db.session.commit()

    return new_event


def login(entered_username, entered_password):
    """Function to log a user in"""

    match = User.query.filter(User.user_name == entered_username).first()
    print("match:", match)
    if match and bcrypt.check_password_hash(match.user_pwd, entered_password):
        set_user = {"user_id": match.user_id, "username":match.user_name}
        session['user'] = set_user
        print("Logged in & user session set to:", set_user)
        flash(f"Welcome back {entered_username}.", "success")
    else :
        flash("Username and/or Password not found, please try again, or register.", "danger")
