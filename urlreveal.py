#!/usr/bin/env python
import urllib2

__version__ = '1.0'
crawler = urllib2.build_opener()
crawler.addheaders = [
    ('User-Agent', 'UrlReveal/%s' % __version__),
]

def reveal(url, tries=0):
    if not url.startswith('http://'):
        url = 'http://' + url
    url = url.encode('utf-8')
    try:
        f = crawler.open(url)
        location = f.geturl()
        return location.decode('utf-8')
    except urllib2.HTTPError, e:
        return str(e.code)
    except ValueError:
        return '404'
    except:
        if tries >= 3:
            return '500'
        else:
            return reveal(url, tries=tries+1)

if __name__ == '__main__':
    import sys
    print reveal(sys.argv[1])
