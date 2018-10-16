import urllib.request
import json

def request(api_url):
    req = urllib.request.Request(
        api_url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as url:
            data = json.loads(url.read().decode())
        return data
    except Exception as ex:
        return {}
