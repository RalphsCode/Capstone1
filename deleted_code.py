"""
Code used in legacy versions of the App, but not used in the final version.
"""

# From app.py:


# 3. Get the weather station ID from functions.py
stations = get_station_id(found_fips)

# Find the closest weather station to the event
closest_station = find_closest_station(stations)

closest_station_id = closest_station[0]['id']
print(f"Found Station ID: {closest_station_id}")


#++++++++++++++++++++++++++++++++++++++++++++++++
# From Functions.py

"""
-----------------------------------------------------------------
Function 3b: find distances between 2 geographical points
----------------------------------------------------------------
"""

def haversine(lat1, lon1, lat2, lon2):
    """Function to calculate the distance between two points using the Haversine formula"""
    R = 6371.0  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance
# END haversine()


"""
-----------------------------------------------------------------
Function 3c: find distances between weather offices in that FIBS, and return the station closest to the event's Lat/Long
----------------------------------------------------------------
"""

def find_closest_station(stations):
    # Event latitude and longitude
    event_lat = session['lat_long'][0]['lat']
    event_lon = session['lat_long'][0]['long']

    # Calculate distance for each weather station and store it
    for station in stations:
        station_lat = float(station['latitude'])
        station_lon = float(station['longitude'])
        distance = haversine(event_lat, event_lon, station_lat, station_lon)
        station['distance'] = distance

    # Sort stations by distance
    stations_sorted = sorted(stations, key=lambda x: x['distance'])

    # Select the closest station to the event
    closest_station = stations_sorted[:10]
    for stat in closest_station:
        print(stat['id'], stat['name'])

    # Write the station id to session
    session["closest_station"]=[closest_station[0]['id']]

    # Print & return the closest stations
    print("### Closest Station ID:", closest_station[0]['id'])
    # print(f"Station: {closest_station['name']}, Distance: {closest_station['distance']:.2f} km, ID: {closest_station['id']}")
    return closest_station
# END find_closest_station



"""
-----------------------------------------------------------------
Function 4a: Get the weather history for the station_id
----------------------------------------------------------------
"""
def get_weather_history_id(station_id):
    """Retrieve the weather history at the weather forecast station closest to the event"""

    date = dates_to_use()
    
    # API endpoint
    url = f"https://www.ncei.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&stationid={station_id}&startdate={date}&enddate={date}&datatypeid=TMAX,TMIN,PRCP,TAVG,CLDC&units=standard&limit=1000" 
    headers= {"token": NOAA_token}
    
    # Sending GET request to the API
    response = requests.get(url, headers=headers)
    
    # Checking if the request was successful
    if response.status_code == 200:
        # Parsing the JSON response
        data = response.json()
        print(data)
        # find_closest_station(stations)

        return data
    
    else:
        # Handling errors
        return f"Failed to get Weather History. Error code: {response.status_code}"
# END get_weather_histord_id()



"""
-----------------------------------------------------------------
Function 3a find the weather forecast offices in that FIBS
----------------------------------------------------------------
"""

def get_station_id(fips):
    """Using the NOAA app to get the relevant weather office for the FIPS location."""

    # API endpoint
    url = f"https://www.ncdc.noaa.gov/cdo-web/api/v2/stations?locationid=FIPS:{fips}&limit=20&datasetid=GHCND"
    headers= {"token": NOAA_token}
    
    # Sending GET request to the API
    response = requests.get(url, headers=headers)
    
    # Checking if the request was successful
    if response.status_code == 200:
        # Parsing the JSON response
        data = response.json()

        no_of_stations = data['metadata']['resultset']['count']
        print("Stations returned: ", no_of_stations)

        # Write the number of stations to session
        session["no_of_stations"]=[no_of_stations]

        stations = data['results'] 
        # find_closest_station(stations)

        return stations
    
    else:
        # Handling errors
        return f"Failed to get Station ID for FIPS {fips}. Error code: {response.status_code}"
# END get_station_id()


"""
---------------------------------------------------------------
Function C: Do a pattern check to see if the entered zip matches the pattern of a US zipcode.
----------------------------------------------------------------
"""
def zip_checker(zip):
    pattern = r'^\d{5}(-\d{4})?$'
    return re.match(pattern, zip) is not None




<!-- Display some of the info used in the search -->
<div class="container mt-5">
    <h2 class="mb-4">Criteria</h2>
    <table class="table table-bordered table-striped">
        <thead class="thead-dark">
            <tr>
                <th scope="col">Criteria</th>
                <th scope="col">Details</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Event Date</td>
                <td class="text-success"> {{ session.event_date.strftime("%B %d") }} </td>
            </tr>
            <tr>
                <td>Event Location</td>
                <td class="text-success"> {{ session.lat_long.get('address') }} </td>
            </tr>
            <tr>
                <td>Event Latitude and Longitude</td>
                <td class="text-success"> {{ session.lat_long.get('lat') }} / {{ session.lat_long.get('long') }} </td>
            </tr>
            <tr>
                <td>FIPS county code used to search for weather stations</td>
                <td class="text-success"> {{ found_fips }} </td>
            </tr>
        </tbody>
    </table>
</div>


    """
    Option 1 for Testing, or, if NOAA API is down:
    If the NOAA NCDC API Server is down, use this static data in place of the dynamic data.
    Comment this option out if you want to do live API calls to the NCDC API server.
    """
    # with open('static/test_data.json', 'r') as file:
    #     data = json.load(file)
    # print(f"Weather Data Sucessfully received for: {date}.")
    # return data

    """ End option 1 """

    """
    Option 2 for live deploy:
    Use this to make actual live calls to the NOAA NCDC API Server
    Comment this option out if in testing or NCDC server is down.
    """