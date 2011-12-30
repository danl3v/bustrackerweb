from google.appengine.ext import db

class User(db.Model):
    user = db.UserProperty()
    
    latitude = db.FloatProperty(default=37.80198255)
    longitude = db.FloatProperty(default=-122.27268)
    zoom_level = db.IntegerProperty(default=14)
    map_type = db.StringProperty(default="roadmap")
    show_controls = db.StringProperty(default="yes")
    
    max_arrivals = db.IntegerProperty(default=3)
    show_missed = db.BooleanProperty(default=True)
    show_news_feed = db.StringProperty(default="no")
    news_feed_width = db.IntegerProperty(default=0)
    show_banner = db.StringProperty(default="");
    timezone = db.StringProperty(default="pacific")
    
class Stop(db.Model):
    user = db.ReferenceProperty(User, collection_name='stops')
    title = db.StringProperty(default="untitled")
    agency_tag = db.StringProperty(default="")
    line_tag = db.StringProperty(default="")
    direction_tag = db.StringProperty(default="")
    stop_tag = db.StringProperty(default="")
    destination_tag = db.StringProperty(default="")
    time_to_stop = db.IntegerProperty(0)
    position = db.IntegerProperty(0)
    
class Post(db.Model):
    user = db.ReferenceProperty(User, collection_name='posts')
    body = db.StringProperty(default="untitled")
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)