from http.server import BaseHTTPRequestHandler
import time

import app as core
from api._lib.http_utils import json_resp, query_of


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        json_resp(self, 200, {'ok': True})

    def do_GET(self):
        q = query_of(self.path)
        date_str = (q.get('date') or [''])[0]
        period = (q.get('period') or ['week'])[0]
        cache_key = f"{period}:{date_str}"
        try:
            items = core.fetch_panews_calendar(date_str, period)
            now_ts = int(time.time())
            core.PANEWS_CACHE[cache_key] = {'items': items, 'timestamp': now_ts}
            json_resp(self, 200, {'ok': True, 'source': 'panews', 'items': items, 'timestamp': now_ts, 'stale': False})
        except Exception as e:
            cached = core.PANEWS_CACHE.get(cache_key)
            if not cached and core.PANEWS_CACHE:
                cached = max(core.PANEWS_CACHE.values(), key=lambda x: int(x.get('timestamp', 0)))
            json_resp(
                self,
                200,
                {
                    'ok': True,
                    'source': 'panews-cache' if cached else 'panews',
                    'items': (cached or {}).get('items', []),
                    'timestamp': int(time.time()),
                    'stale': True,
                    'error': str(e),
                },
            )
