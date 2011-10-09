from google.appengine.ext import db

class User(db.Model):
    user = db.UserProperty()
    max_arrivals = db.IntegerProperty(default=3)
    show_missed = db.BooleanProperty(default=False)
    show_news_feed = db.StringProperty(default="no")
    news_feed_width = db.IntegerProperty(default=0)
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
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)