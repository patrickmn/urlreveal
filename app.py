#!/usr/bin/env python
import datetime
from xml.sax.saxutils import quoteattr, escape
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import urlreveal
import model

class Request(webapp.RequestHandler):

    def send(self, data):
        return self.response.out.write(data)

class MainPage(Request):

    def get(self):
        self.send(template.render('view/index.html', dict()))

class AboutPage(Request):

    def get(self):
        self.send(template.render('view/about.html', dict()))

class Reveal(Request):

    def get(self):
        url = self.request.get('url').strip()
        if not url:
            self.redirect('/')
            return
        result = ''
        try:
            revealed = getRevealed(url)
            if revealed == '301':
                result = '301: The URL provided resulted in too many redirects.'
            elif revealed == '403':
                result = '403: Forbidden'
            elif revealed == '404':
                result = '404: The URL provided was invalid.'
            elif revealed == '503':
                result = '503: The server is unavailable.'
            elif revealed == url:
                result = '<a href=%s rel="nofollow">%s</a><br /><br />does not redirect elsewhere.' % (quoteattr(revealed), escape(revealed))
            else:
                result = '%s<br /><br />leads to<br /><br /><a href=%s rel="nofollow">%s</a>' % (escape(url), quoteattr(revealed), escape(revealed))
        except:
            result = '500: There was an error opening the URL. Please check it and try again.'
        template_values = {
            'result': result,
        }
        self.send(template.render('view/reveal.html', template_values))

class Api(Request):

    def get(self):
        url = self.request.get('url').strip()
        try:
            revealed = getRevealed(url)
        except:
            revealed = '500'
        self.send(revealed)

class ApiHelp(Request):

    def get(self):
        self.send(template.render('view/apihelp.html', dict()))

def getRevealed(url):
    query = model.CachedUrl.gql("WHERE url = :1", url).fetch(1)
    if query:
        c = query[0]
        now = datetime.datetime.now()
        if now - c.date > datetime.timedelta(hours=1):
            try:
                c.destination = urlreveal.reveal(url)
                c.date = now
                c.put()
            except:
                return c.destination
    else:
        c = model.CachedUrl()
        c.url = url
        c.destination = urlreveal.reveal(url)
        c.put()
    return c.destination

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/about', AboutPage),
                                      ('/reveal', Reveal),
                                      ('/api', Api),
                                      ('/apihelp', ApiHelp)],
                                     debug=False)

if __name__ == '__main__':
    run_wsgi_app(application)
