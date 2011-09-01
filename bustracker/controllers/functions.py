import urllib2

def get_xml(url):
    '''Go to url and returns the xml data.'''
    file = urllib2.urlopen(url)
    xml = file.read()
    file.close()
    return xml
    
def get_leave_at(time_to_stop, minutes):
    '''Return the string that tells user when to leave to catch the bus.'''
    minutes = int(minutes)
    if time_to_stop > minutes:
        return "missed"
    elif time_to_stop == minutes:
        return "leave now"
    else:
        return "leave in " + str(minutes - time_to_stop) + "m"
    