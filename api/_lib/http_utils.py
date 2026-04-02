import json
from urllib.parse import parse_qs, urlparse


def json_resp(handler, code, payload):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    handler.send_response(code)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    handler.end_headers()
    handler.wfile.write(body)


def query_of(path):
    return parse_qs(urlparse(path).query)


def read_json_body(handler):
    try:
        cl = int(handler.headers.get('Content-Length', '0') or 0)
    except Exception:
        cl = 0
    raw = handler.rfile.read(cl) if cl > 0 else b'{}'
    try:
        payload = json.loads(raw.decode('utf-8') or '{}')
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}
