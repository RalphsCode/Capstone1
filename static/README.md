Ralph's Event Weather App

ReadMe

To run this app:
    Create ENV keys for:
        Google Maps & NOAA

    Then run app.py on a python server
    That should open the website that runs the app.

The idea for this App is to predict the weather at any location in the USA based on years of weather history from that day in the past.

The user enters the location of their event - whether it be a wedding in Tahoe, or a sports event in LA, or a birthday party at the Zoo in St. Louis, or a conference in New Orleans, or a vacation to Disneyland, etc. The location can be as generic as a zip, code, or the name of a place, or a street address, all are valid searches.

After entering the location the user enters the date for the event, for example May 14th, 2025. The App also askes the user to select how many years of weather history they want to search (3 to 10 years).

The App will:
Validate the address using Google Places API
Get the latitude and Longitude for the location also from Google Places.
Ensure the location is in the USA.
From the FCC API the App will find the FIPS code (county code) for the Lat/long.
Calculate the dates to use for the weather history search.
Do API calls to the NOAA NCDC API to get weather history from all the weather stations in that county of the event.
Process the weather history data and calculate a prediction.
Present a prediction of the temperature and the probability of rain on that day at the event location. Eg: 65.5 degrees, 10% likelyhood of precipitation.


API's used:
The App uses:
- the Google Places API
- the FCC location lookup API
- NOAA's NCDC API

Some of the technologies used:
Python
Flask
WTForms
Flash
Inheritance
Logging
Debugging

A flowchart of the App process flow is in the process folder (process_diagram.jpg).

The website is on Render at:
https://capstone-1-event-weather.onrender.com

Thank you,
Ralph.

I can be reached at:
RalphsCode@gmail.com
