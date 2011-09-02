import urllib2

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