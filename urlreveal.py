#!/usr/bin/env python
import urllib2

__version__ = '1.0'

def reveal(url):
    url = url.encode('utf-8')
    crawler = urllib2.build_opener()
    crawler.addheaders = [
        ('User-Agent', 'UrlReveal/%s' % __version__),
        ]
    try:
        f = crawler.open(url)
        location = f.geturl()
        return location.decode('utf-8')
    except urllib2.HTTPError, e:
        # 301: Too many redirects (infinite loop)
        # 403: Forbidden
        # 404: Not found
        return str(e.code)

if __name__ == '__main__':
    import sys
    print reveal(sys.argv[1])
