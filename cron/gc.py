import datetime
from google.appengine.ext import db

import model

query = model.CachedUrl.gql("WHERE date < :1", datetime.datetime.now() - datetime.timedelta(hours=1))
for x in query:
    db.delete(x)
