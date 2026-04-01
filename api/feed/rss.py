from http.server import BaseHTTPRequestHandler
import urllib.parse
import urllib.request

from api._lib.http_utils import json_resp, query_of

ALLOWED_FEEDS = {
    'https://blockcast.it/feed',
    'https://rsshub.app/coindesk/news',
}


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8',
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode('utf-8', errors='ignore')


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        json_resp(self, 200, {'ok': True})

    def do_GET(self):
        q = query_of(self.path)
        feed_url = (q.get('url') or [''])[0].strip()
        feed_url = urllib.parse.unquote(feed_url)
        if feed_url not in ALLOWED_FEEDS:
            json_resp(self, 400, {'ok': False, 'error': 'feed url not allowed', 'items': []})
            return
        try:
            xml = fetch_text(feed_url)
            if '<rss' not in xml and '<feed' not in xml:
                raise RuntimeError('invalid rss xml')
            json_resp(self, 200, {'ok': True, 'xml': xml})
        except Exception as e:
            json_resp(self, 500, {'ok': False, 'error': str(e), 'xml': ''})
