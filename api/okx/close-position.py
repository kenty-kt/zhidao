from http.server import BaseHTTPRequestHandler

import app as core
from api._lib.http_utils import json_resp, read_json_body


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        json_resp(self, 200, {'ok': True})

    def do_POST(self):
        try:
            payload = read_json_body(self)
            data = core.place_okx_close_position(payload)
            json_resp(self, 200, data)
        except Exception as e:
            json_resp(self, 500, {'ok': False, 'error': str(e)})
