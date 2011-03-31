#!/usr/bin/env python
from xml.sax.saxutils import quoteattr, escape
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import urlreveal

url_cache_duration = 3600     # How many seconds to cache pages/results
page_cache_duration = 2592000 # How many seconds to cache (static) rendered pages

class Request(webapp.RequestHandler):

    def send(self, data):
        return self.response.out.write(data)

class MainPage(Request):

    def get(self):
        self.send(getStaticPage('index', 'view/index.html'))

class AboutPage(Request):

    def get(self):
        self.send(getStaticPage('about', 'view/about.html'))

class Reveal(Request):

    def get(self):
        result = ''
        url = self.request.get('url').strip()
        if not url:
            self.redirect('/')
            return
        try:
            destination = getDestination(url)
            if destination == '301':
                result = '301: The URL provided resulted in too many redirects.'
            elif destination == '403':
                result = '403: Forbidden'
            elif destination == '404':
                result = '404: The URL provided was invalid.'
            elif destination == '410':
                result = '410: The URL provided is no longer available.'
            elif destination == '503':
                result = '503: The server is unavailable.'
            elif destination == url:
                result = '<a href=%s rel="nofollow">%s</a><br /><br />does not redirect elsewhere.' % (quoteattr(destination), escape(destination))
            else:
                result = '%s<br /><br />leads to<br /><br /><a href=%s rel="nofollow">%s</a>' % (escape(url), quoteattr(destination), escape(destination))
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
            destination = getDestination(url)
        except:
            destination = '500'
        self.send(destination)

class ApiHelp(Request):

    def get(self):
        self.send(getStaticPage('apihelp', 'view/apihelp.html'))

def getStaticPage(name, file):
    memcachekey = 'page|' + name
    val = memcache.get(memcachekey)
    if val is None:
        val = template.render(file, dict())
        memcache.set(memcachekey, val, page_cache_duration)
    return val

def getDestination(url):
    memcachekey = 'url|' + url
    val = memcache.get(memcachekey)
    if val is None:
        val = urlreveal.reveal(url)
        memcache.set(memcachekey, val, url_cache_duration)
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
