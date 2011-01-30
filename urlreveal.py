#!/usr/bin/env python
import urllib2
import httplib

__version__ = '1.0'
crawler = urllib2.build_opener()
crawler.addheaders = [
    ('User-Agent', 'UrlReveal/%s' % __version__),
]

def reveal(url, tries=0):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    url = url.encode('utf-8')
    try:
        f = crawler.open(url)
        location = f.geturl()
        return location.decode('utf-8')
    except (ValueError, httplib.InvalidURL):
        return '404'
    except urllib2.HTTPError, e:
        return str(e.code)
    except:
        if tries >= 3:
            raise
        else:
            return reveal(url, tries=tries+1)

if __name__ == '__main__':
    import sys
    print reveal(sys.argv[1])
