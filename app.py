#!/usr/bin/env python
import datetime
from xml.sax.saxutils import quoteattr, escape
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import urlreveal
import model
import template

class Request(webapp.RequestHandler):

    def send(self, data):
        return self.response.out.write(data)

class MainPage(Request):

    def get(self):
        self.send(template.header)
        self.send(template.revealform)
        self.send("""<br />
<p>UrlReveal shows you the page behind a shortened URL. <a href="/about" title="About">Learn more</a>.</p>""")
        self.send(template.footer)

class AboutPage(Request):

    def get(self):
        self.send(template.header)
        self.send(template.revealform)
        self.send("""<br />
<p>UrlReveal shows you where short URLs lead you to before you actually follow them.</p>
<p>As an example, try entering <a href="http://bit.ly/hixYHw" title="bit.ly link">bit.ly/hixYHw</a> above. Clever!</p>""")
        self.send(template.footer)

class Reveal(Request):

    def get(self):
        self.send(template.header)
        self.send("""
        <p>""")
        url = self.request.get('url').strip()
        try:
            revealed = getRevealed(url)
            if revealed == '301':
                self.send('301: The URL provided resulted in too many redirects.')
            elif revealed == '403':
                self.send('403: Forbidden')
            elif revealed == '404':
                self.send('404: The URL provided was invalid.')
            elif revealed == url:
                self.send('<a href=%s rel="nofollow">%s</a><br /><br />does not redirect elsewhere.' % (quoteattr(revealed), escape(revealed)))
            else:
                self.send('%s<br /><br />leads to<br /><br /><a href="%s" rel="nofollow">%s</a>' % (escape(url), quoteattr(revealed), escape(revealed)))
        except:
            self.send('There was an error opening the URL. Please check it and try again.')
        self.send("</p><br />")
        self.send(template.revealform)
        self.send(template.footer)

def getRevealed(url):
    if not url.startswith('http://'):
        url = 'http://' + url
    try:
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
    except:
        return urlreveal.reveal(url)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/about', AboutPage),
                                      ('/reveal', Reveal)],
                                     debug=False)

if __name__ == '__main__':
    run_wsgi_app(application)
