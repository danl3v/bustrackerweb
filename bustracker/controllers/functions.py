from google.appengine.api import urlfetch

from datetime import timedelta, datetime
import timezone

import nextbus, bart, metrotransit

def apiwrapperfor(agency):
    if agency == "bart":
        return bart
    elif agency == "metrotransit":
        return metrotransit
    else:
        return nextbus

def get_xml(url):
    '''Go to url and returns the xml data.'''
    file = urlfetch.fetch(url)
    if file.status_code == 200:
    	return file.content
    else:
    	return None

def local_time(time, specified_timezone):
    return time.replace(tzinfo=timezone.tz("utc")).astimezone(timezone.tz(specified_timezone))

def pretty_time(time, specified_timezone):
    now = datetime.now()
    diff = now - time 
    second_diff = diff.seconds
    day_diff = diff.days
    if day_diff < 0: return "no time available"
    if day_diff == 0:
        if second_diff < 10: return "just now"
        if second_diff < 60: return str(second_diff) + " seconds ago"
        if second_diff < 120: return  "a minute ago"
        if second_diff < 3600: return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200: return "an hour ago"
        if second_diff < 86400: return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1: return "Yesterday at " + local_time(time, specified_timezone).strftime("%I:%M%p")
    if day_diff < 7: return local_time(time, specified_timezone).strftime("%A at %I:%M%p")
    if day_diff < 365: return local_time(time, specified_timezone).strftime("%B %d at %I:%M%p")
    return local_time(time, specified_timezone).strftime("%B %d, %Y at %I:%M%p")