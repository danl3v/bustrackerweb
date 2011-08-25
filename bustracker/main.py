from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from controllers import welcome

def main():
    application = webapp.WSGIApplication([

           # main pages
           ('/', welcome.MainPage),
           ('/predictions', welcome.Predictions),
           ('/stop/new', welcome.NewStop),
           ('/stop/edit/(.*)', welcome.EditStop),
           ('/stop/delete/(.*)', welcome.DeleteStop),
           ('/lines', welcome.Lines),
           ('/directions', welcome.Directions),
           ('/stops', welcome.Stops),
         ],debug=True)

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
