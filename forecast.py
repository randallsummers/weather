#! /usr/bin/python3

import sys, os
import shelve
import requests
import json
from datetime import datetime
import dateutil.parser
import pprint

conf_file = os.path.join(os.path.dirname(__file__),'config')
shelf = shelve.open(conf_file)
user_agent = shelf['uagent']
default_location = (str(shelf['lat']), str(shelf['lon']), shelf['obsstation'], shelf['radarstation'])
shelf.close()

headers = {
    'User-Agent': user_agent
}

def strtodatetime(s):
    return dateutil.parser.parse(s)

def degToCompass(num):
    val=int((num/22.5)+.5)
    arr=["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return arr[(val % 16)]

def locationinfo(location):
    if type(location) is tuple:
        if len(location) == 4:
            return location
        elif len(location) == 2:
            # Find station and return (lat, lon, obsstation, radarstation)
            # Find and return (lat, lon, obsstation, radarstation)
            return location
    return location

def daily(nperiods=4, loc=default_location):
    locinfo = locationinfo(loc)
    lat = locinfo[0]
    lon = locinfo[1]
    url = 'https://api.weather.gov/points/' + lat + ',' + lon + '/forecast'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = json.loads(response.text)
    for i in range(nperiods):
        period = data['properties']['periods'][i]
        print(period['name'])
        print(period['detailedForecast'] + '\n')

def hourly(nhours=6, loc=default_location):
    locinfo = locationinfo(loc)
    lat = locinfo[0]
    lon = locinfo[1]
    url = 'https://api.weather.gov/points/' + lat + ',' + lon + '/forecast/hourly'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = json.loads(response.text)
    for i in range(nhours):
        period = data['properties']['periods'][i]
        start = strtodatetime(period['startTime'])
        end = strtodatetime(period['endTime'])
        timestr = datetime.strftime(start, '%A %B %d %Y %I:%M %p') + '-' + datetime.strftime(end, '%I:%M %p')
        temp = str(period['temperature']) + ' ' + period['temperatureUnit']
        wind = period['windSpeed'] + ' ' + period['windDirection']
        print(timestr)
        print(period['shortForecast'])
        print('Temperature: ' + temp)
        print('Wind: ' + wind + '\n')

def current(loc=default_location):
    locinfo = locationinfo(loc)
    station = locinfo[2]
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
    windgust = props['windGust']['value'] * 2.23694
    winddir = degToCompass(props['windDirection']['value'])
    windstr = f"Wind from {winddir} at {windspeed!s:.2} mph with gusts to {windgust!s:.2} mph"
    pressure = props['barometricPressure']['value'] * 0.00029530
    print('Station ID: ' + station)
    print('Temperature: %.0f F' % temperature)
    print('Feels like: %.0f F' % feelsLike)
    print('Humidity: %.0f %%' % humidity)
    print(windstr)
    print('Barometer: %.2f inHg' % pressure)
    print('Timestamp: ' + timestamp)

def alerts(loc=default_location):
    locinfo = locationinfo(loc)
    lat = locinfo[0]
    lon = locinfo[1]
    url = 'https://api.weather.gov/alerts/active?point=' + lat + ',' + lon
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = json.loads(response.text)
    pprint.pprint(data)

def radar(loc=default_location):
    locinfo = locationinfo(loc)
    radarstation = locinfo[3]
    # TODO: Figure out how to view NWS radar
    # Local radar is KTLX

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    else:
        print('Please specify a command')
        sys.exit()
    
    if cmd == 'daily':
        daily()
    elif cmd == 'hourly':
        hourly()
    elif cmd == 'current':
        current()
    elif cmd == 'alerts':
        alerts()
    else:
        print('Please specify a valid command')
