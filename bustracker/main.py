from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from controllers import welcome, stops, nextbus, bart, buswrap, posts

def main():
    application = webapp.WSGIApplication([
           # main
           ('/', welcome.MainPage),
           ('/feedback', welcome.Feedback),
           ('/settings', welcome.Settings),
           
           # user specific data
           ('/stops', buswrap.UserStops),
           ('/lines', buswrap.UserLines),
           ('/predictions', buswrap.UserPredictions),
           ('/vehicles/(.*)', buswrap.UserVehicles),
           
           ('/defaults', buswrap.Defaults),
           ('/map', buswrap.UserMap),
           
           # stop management
           ('/stop/save', stops.SaveStop),
           ('/stop/moveup', stops.MoveUp),
           ('/stop/movedown', stops.MoveDown),
           ('/stop/delete', stops.DeleteStop),
           
           # general api
           ('/agencies', buswrap.Agencies),
           ('/(.*)/lines', buswrap.Lines),
           ('/(.*)/(.*)/directions', buswrap.Directions),
           ('/(.*)/(.*)/(.*)/stops', buswrap.Stops),
           
           # news feed
           ('/posts', posts.Posts),
           ('/post/new', posts.NewPost),
           ('/post/edit/(.*)', posts.EditPost),
           ('/post/delete/(.*)', posts.DeletePost),
           
         ],debug=True)

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
