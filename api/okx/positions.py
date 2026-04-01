from http.server import BaseHTTPRequestHandler
import os
import time

import app as core
from api._lib.http_utils import json_resp


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        json_resp(self, 200, {'ok': True})

    def do_GET(self):
        try:
            positions = core.fetch_okx_positions()
            positions.sort(key=lambda x: float(x.get('usdtValue', 0) or 0), reverse=True)
            json_resp(
                self,
                200,
                {
                    'ok': True,
                    'positions': positions[:20],
                    'configured': bool(os.getenv('OKX_API_KEY', '').strip() and os.getenv('OKX_API_SECRET', '').strip()),
                    'source': 'okx',
                    'timestamp': int(time.time()),
                },
            )
        except Exception as e:
            json_resp(
                self,
                500,
                {
                    'ok': False,
                    'configured': bool(os.getenv('OKX_API_KEY', '').strip() and os.getenv('OKX_API_SECRET', '').strip()),
                    'source': 'okx',
                    'error': str(e),
                    'positions': [],
                },
            )
