#!/usr/bin/env python
import cgi
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import urlreveal
import template

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.header)
        self.response.out.write("""<form action="/reveal" method="post">
    <div><input type="text" name="url" size="60"></input></div>
    <div><input type="submit" value="Show me the real URL"></div>
</form>""")
        self.response.out.write(template.footer)


class Reveal(webapp.RequestHandler):
    def post(self):
        self.response.out.write(template.header)
        self.response.out.write("""
        <p>""")
        url = self.request.get('url')
        if not url.startswith('http://'):
            revealed = urlreveal.reveal('http://' + url)
        else:
            revealed = urlreveal.reveal(url)
        if revealed == '301':
            self.response.out.write('301: The URL provided resulted in too many redirects.')
        elif revealed == '403':
            self.response.out.write('403: Forbidden')
        elif revealed == '404':
            self.response.out.write('404: The URL provided was invalid.')
        else:
            self.response.out.write('%s<br /><br />leads to<br /><br /><a href="%s" rel="nofollow">%s</a>' % (url, revealed, revealed))
        self.response.out.write("</p>")
        self.response.out.write(template.footer)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/reveal', Reveal)],
                                     debug=True)

if __name__ == '__main__':
    run_wsgi_app(application)
