from http.server import BaseHTTPRequestHandler
import time

import app as core
from api._lib.http_utils import json_resp


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        json_resp(self, 200, {'ok': True})

    def do_GET(self):
        try:
            data = core.fetch_soso_sector_board()
            json_resp(self, 200, {'ok': True, 'source': 'sosovalue', 'items': data, 'timestamp': int(time.time())})
        except Exception as e:
            json_resp(self, 500, {'ok': False, 'error': str(e), 'items': []})
