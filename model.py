from google.appengine.ext import db

class CachedUrl(db.Model):
    url = db.StringProperty()
    destination = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
