#! python3

import sys, os
import importlib
import requests
import json
from datetime import datetime
import dateutil.parser
from geopy.geocoders import Nominatim

conf_file = os.path.join(os.path.dirname(__file__),'config.py')
config = importlib.import_module('config', conf_file)

headers = {
    'User-Agent': config.uagent
}

def strtodatetime(s):
    return dateutil.parser.parse(s)

def degToCompass(num):
    val=int((num/22.5)+.5)
    arr=["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return arr[(val % 16)]

def getlatlon(loc):
    geolocator = Nominatim()
    coords = geolocator.geocode(loc)
    return (str(coords.latitude), str(coords.longitude))

def getobsstation(loc):
    return config.obsstation

def daily(loc=None, nperiods=4):
    if loc is None:
        lat = config.lat
        lon = config.lon
    else:
        lat, lon = getlatlon(loc)
    url = 'https://api.weather.gov/points/' + lat + ',' + lon + '/forecast'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = json.loads(response.text)
    output = ''
    for i in range(nperiods):
        period = data['properties']['periods'][i]
        output += period['name'] + '\n'
        output += period['detailedForecast'] + '\n\n'
    return output

def hourly(loc=None, nhours=6):
    if loc is None:
        lat = config.lat
        lon = config.lon
    else:
        lat, lon = getlatlon(loc)
    url = 'https://api.weather.gov/points/' + lat + ',' + lon + '/forecast/hourly'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = json.loads(response.text)
    output = ''
    for i in range(nhours):
        period = data['properties']['periods'][i]
        start = strtodatetime(period['startTime'])
        end = strtodatetime(period['endTime'])
        timestr = datetime.strftime(start, '%A %B %d %Y %I:%M %p') + '-' + datetime.strftime(end, '%I:%M %p')
        temp = str(period['temperature']) + ' ' + period['temperatureUnit']
        wind = period['windSpeed'] + ' ' + period['windDirection']
        output += timestr + '\n'
        output += period['shortForecast'] + '\n'
        output += 'Temperature: ' + temp + '\n'
        output += 'Wind: ' + wind + '\n\n'
    return output

def current(loc=None):
    if loc is None:
        station = config.obsstation
    else:
        station = getobsstation(loc)
    url = 'https://api.weather.gov/stations/' + station + '/observations/current'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = json.loads(response.text)
    props = data['properties']
    timestamp = datetime.strftime(strtodatetime(props['timestamp']), '%A %B %d %Y %I:%M %p')
    temperature = props['temperature']['value'] * 1.8 + 32
    if props['windChill']['value'] != None:
        feelsLike = props['windChill']['value'] * 1.8 + 32
    elif props['heatIndex']['value'] != None:
        feelsLike = props['heatIndex']['value'] * 1.8 + 32
    else:
        feelsLike = temperature
    humidity = props['relativeHumidity']['value']
    windspeed = props['windSpeed']['value'] * 2.23694
    if props['windGust']['value'] != None:
        windgust = props['windGust']['value'] * 2.23694
    else:
        windgust = windspeed
    winddir = degToCompass(props['windDirection']['value'])
    windstr = f"Wind from {winddir} at {windspeed!s:.2} mph with gusts to {windgust!s:.2} mph"
    pressure = props['barometricPressure']['value'] * 0.00029530
    output = ''
    output += 'Station ID: ' + station + '\n'
    output += 'Temperature: %.0f F' % temperature + '\n'
    output += 'Feels like: %.0f F' % feelsLike + '\n'
    output += 'Humidity: %.0f %%' % humidity + '\n'
    output += windstr + '\n'
    output += 'Barometer: %.2f inHg' % pressure + '\n'
    output += 'Timestamp: ' + timestamp + '\n'
    return output

def alerts(loc=None):
    if loc is None:
        lat = config.lat
        lon = config.lon
    else:
        lat, lon = getlatlon(loc)
    url = 'https://api.weather.gov/alerts?point=' + lat + ',' + lon
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = json.loads(response.text)
    features = data['features']
    alert_str = 'Alerts for your location:\n\n'
    alert_str += '--------------------------------------------------------------------------------\n\n'
    for feature in features:
        props = feature['properties']
        start = strtodatetime(props['effective'])
        end = strtodatetime(props['expires'])
        alert_str += 'Message Type: ' + props['messageType'] + '\n'
        alert_str += 'Active: ' + datetime.strftime(start, '%A %B %d %Y %I:%M %p') + '-' + datetime.strftime(end, '%I:%M %p') + '\n\n'
        alert_str += 'Description:\n'
        alert_str += props['description'] + '\n\n'
        alert_str += 'Instructions:\n'
        alert_str += props['instruction'] + '\n\n'
        alert_str += '--------------------------------------------------------------------------------\n\n'
    return alert_str

def radar(loc=None):
    return False
    # TODO: Figure out how to view NWS radar
    # Local radar is KTLX

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    else:
        print('Please specify a command')
        sys.exit()
    
    if cmd == 'daily':
        print(daily())
    elif cmd == 'hourly':
        print(hourly())
    elif cmd == 'current':
        print(current())
    elif cmd == 'alerts':
        print(alerts())
    else:
        print('Please specify a valid command')
