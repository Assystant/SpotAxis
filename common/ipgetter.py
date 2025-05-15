# common/ipgetter.py

import re
import urllib2

def get_external_ip():
    url_list = [
        'http://ip.42.pl/raw',
        'http://checkip.dyndns.org/',
        'http://www.whatismyip.org/',
        'http://ipecho.net/plain',
    ]
    
    for url in url_list:
        try:
            response = urllib2.urlopen(url, timeout=5).read()
            # for checkip.dyndns.org
            if 'Current IP Address' in response:
                return re.search(r'Current IP Address: ([\d.]+)', response).group(1)
            return response.strip()
        except Exception:
            continue
    return None
