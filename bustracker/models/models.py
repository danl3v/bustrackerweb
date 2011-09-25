from google.appengine.ext import db
from datetime import timedelta, datetime
import timezone

class User(db.Model):
    user = db.UserProperty()
    max_arrivals = db.IntegerProperty(default=3)
    show_missed = db.BooleanProperty(default=False)
    show_news_feed = db.IntegerProperty(default=0)
    show_banner = db.StringProperty(default="");
    timezone = db.StringProperty(default="pacific")
    
class Stop(db.Model):
    user = db.ReferenceProperty(User, collection_name='stops')
    title = db.StringProperty(default="untitled")
    agency_tag = db.StringProperty()
    line_tag = db.StringProperty(default="")
    direction_tag = db.StringProperty()
    stop_tag = db.StringProperty()
    destination_tag = db.StringProperty()
    time_to_stop = db.IntegerProperty()
    position = db.IntegerProperty()
    
class Post(db.Model):
    user = db.ReferenceProperty(User, collection_name='posts')
    body = db.StringProperty(default="untitled")
    created = db.DateTimeProperty(auto_now=True)
    updated = db.DateTimeProperty(auto_now_add=True)
    
    @property
    def local_created(self): return self.created.replace(tzinfo=timezone.tz("utc")).astimezone(timezone.tz(self.user.timezone))
    
    @property
    def pretty_created(self): return pretty_date(self, self.created)
    
def pretty_date(self, time):
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
    if day_diff == 1: return "Yesterday at " + self.local_created.strftime("%I:%M%p")
    if day_diff < 7: return self.local_created.strftime("%A at %I:%M%p")
    if day_diff < 365: return self.local_created.strftime("%B %d at %I:%M%p")
    return self.local_created.strftime("%B %d, %Y at %I:%M%p")
