import requests
import requests_cache
import googlemaps
from cachetools import cached, LFUCache # pip install cachetools (for caching)
import moment
import pytz
import collections
import datetime as DT
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

cache = LFUCache(maxsize=1000) # 1000 items max in cache at a time (will evict least recently used items)
debug = False

lat = 40.7128
long = 74.0060
gmaps_key = os.getenv('GMAPS_KEY')

def getTime(lat, long, location, debug):
    gmaps = googlemaps.Client(key=gmaps_key)
    with requests_cache.enabled('time_cache', backend='sqlite'):
        timeZone = gmaps.timezone((lat, long))
    offset = timeZone["dstOffset"] + timeZone["rawOffset"]
    if debug:
        return f"It is: {moment.utcnow().add(seconds=offset).format('ddd HH:mm')} {location} {lat}, {long}"
    return f"It is: {moment.utcnow().add(seconds=offset).format('ddd HH:mm')} {location}"

def getTimeAtAbbreviatedTimeZone(location):
    abbreviatedTimeZone = location.upper()

    tzones = collections.defaultdict(set)
    abbrevs = collections.defaultdict(set)

    for name in pytz.all_timezones:
        tzone = pytz.timezone(name)
        for utcoffset, dstoffset, tzabbrev in getattr(
                tzone, '_transition_info', [[None, None, DT.datetime.now(tzone).tzname()]]):
            tzones[tzabbrev].add(name)
            abbrevs[name].add(tzabbrev)
    # find the time zone that matches the provided abbreviation
    timeZone = next(timeZone for timeZone in tzones[abbreviatedTimeZone] if timeZone)
    # if a time zone was found, get the current time at that time zone
    if timeZone:
        return f"It is: {moment.utcnow().timezone(timeZone).format('ddd HH:mm')} {location}"
    else:
        # if no time zone was found, print an error message
        return 'Error: Invalid location'

def getCoordinates(location):
    with requests_cache.enabled('location_cache', backend='sqlite'):
        headers = {
            'User-Agent': 'Cyan Twitch Weather Grabber/1.0',
        }
        results = requests.get(f"https://nominatim.openstreetmap.org/search?format=json&limit=1&q={location}", headers=headers).json()

    lat = results[0]["lat"]
    long = results[0]["lon"]

    return lat, long

@cached(cache) # cache the result of this function
def getCoordinatesGoogle(location):
    with requests_cache.enabled('location_cache', backend='sqlite'):
        gmaps = googlemaps.Client(key=gmaps_key)
        geocode_result = gmaps.geocode(location)
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    long = geocode_result[0]["geometry"]["location"]["lng"]
    return lat, long

def main(location, debug):
    try:
        result = getTimeAtAbbreviatedTimeZone(location)
        return result
    except:
        pass
    try:
        lat, long = getCoordinatesGoogle(location)
    except:
        lat, long = getCoordinates(location)
    result = getTime(lat, long, location, debug)
    return result

if __name__ == "__main__":
    print(main("EST", False))