#!/usr/bin/env python
import cgi
import urllib2
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

__version__ = '1.0'

header = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:og="http://ogp.me/ns#" xmlns:fb="http://www.facebook.com/2008/fbml" dir="ltr" lang="en-US">
<head profile="http://gmpg.org/xfn/11">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>UrlReveal</title>
<meta name="robots" content="noodp, noydir" />
<meta name="description" content="Reveal the page behind short URL and redirects." />
<meta name="keywords" content="urlreveal, url reveal, url,redirect,url redirect" />
<link rel="canonical" href="http://urlreveal.tmwiw.com/" />
<!-- <link rel="SHORTCUT ICON" href="http://cdn.pmylund.com/favicon.ico" /> -->
</head>
<body><center>
    <h1>UrlReveal</h1>
"""
footer = """
</center>
</body>
</html>"""


class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write(header)
        self.response.out.write("""<form action="/reveal" method="post">
    <div><input type="text" name="url" size="60"></input></div>
    <div><input type="submit" value="Show me the real URL"></div>
</form>""")
        self.response.out.write(footer)


class Reveal(webapp.RequestHandler):
    def post(self):
        self.response.out.write(header)
        self.response.out.write("""
        <p>""")
        url = self.request.get('url')
        if not url.startswith('http://'):
            revealed = reveal('http://' + url)
        else:
            revealed = reveal(url)
        if revealed == '301':
            self.response.out.write('301: The URL provided resulted in too many redirects.')
        elif revealed == '403':
            self.response.out.write('403: Forbidden')
        elif revealed == '404':
            self.response.out.write('404: The URL provided was invalid.')
        else:
            self.response.out.write('{0} leads to <a href="{1}" rel="nofollow">{1}</a>'.format(url, revealed))
        self.response.out.write("</p>")
        self.response.out.write(footer)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/reveal', Reveal)],
                                     debug=True)

def reveal(url):
    crawler = urllib2.build_opener()
    crawler.addheaders = [
        ('User-Agent', 'UrlReveal.com/%s' % __version__),
        ]
    try:
        f = crawler.open(url)
        location = f.geturl()
        return location or url
    except urllib2.HTTPError, e:
        # 301: Too many redirects (infinite loop)
        # 404: Not found
        return str(e.code)

if __name__ == '__main__':
    run_wsgi_app(application)
