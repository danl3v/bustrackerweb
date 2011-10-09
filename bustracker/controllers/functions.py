from datetime import timedelta, datetime
import urllib2, timezone

def get_xml(url):
    '''Go to url and returns the xml data.'''
    file = urllib2.urlopen(url)
    xml = file.read()
    file.close()
    return xml
    
def get_leave_at_html(time_to_stop, time_to_arrival):
    '''Return the string that tells user when to leave to catch the bus.'''
    leave_at = get_leave_at(time_to_stop, time_to_arrival)
    if leave_at == -1:
        return "missed"
    elif leave_at == 0:
        return "leave now"
    else:
        return "leave in " + str(leave_at) + "m"

def get_leave_at(time_to_stop, time_to_arrival):
    '''Return -1 if user missed the bus, 0 if user should neave now, otherwise number of minutes user should leave in.'''
    try:
        time_to_arrival = int(time_to_arrival)
    except:
        return -1
        
    if time_to_stop > time_to_arrival:
        return -1
    elif time_to_stop == time_to_arrival:
        return 0
    else:
        return str(time_to_arrival - time_to_stop)

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