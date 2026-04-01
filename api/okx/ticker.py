from http.server import BaseHTTPRequestHandler

import app as core
from api._lib.http_utils import json_resp, query_of


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        json_resp(self, 200, {'ok': True})

    def do_GET(self):
        q = query_of(self.path)
        inst_id = (q.get('instId') or ['BTC-USDT-SWAP'])[0]
        try:
            json_resp(self, 200, {'ok': True, 'ticker': core.fetch_okx_ticker(inst_id)})
        except Exception as e:
            json_resp(self, 500, {'ok': False, 'error': str(e)})
