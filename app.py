#!/usr/bin/env python
from xml.sax.saxutils import quoteattr, escape
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import urlreveal

# How many seconds to cache results
cache_duration = 3600

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
    memcachekey = 'url|' + url
    val = memcache.get(memcachekey)
    if val is None:
        val = urlreveal.reveal(url)
        memcache.set(memcachekey, val, cache_duration)
    return val

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/about', AboutPage),
                                      ('/reveal', Reveal),
                                      ('/api', Api),
                                      ('/apihelp', ApiHelp)],
                                     debug=False)

if __name__ == '__main__':
    run_wsgi_app(application)
