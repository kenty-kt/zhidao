from copy import deepcopy
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import base64
import hashlib
import hmac
import json
import os
import time

from api._lib.http_utils import json_resp, read_json_body


def now_str():
    return time.strftime('%Y-%m-%d %H:%M', time.localtime())


def parse_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def parse_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default


def default_state():
    return {
        'activeTab': 'events',
        'editingEventId': None,
        'selectedEventId': 'evt-001',
        'events': [
            {
                'id': 'evt-001',
                'title': '美联储降息预期',
                'topic': 'Fed Rate Path',
                'description': '跟踪利率路径、通胀与就业数据变化，评估风险资产方向。',
                'keywords': [
                    {'term': 'fed', 'weight': 0.9, 'enabled': True},
                    {'term': 'cpi', 'weight': 0.8, 'enabled': True},
                    {'term': 'rate cut', 'weight': 0.75, 'enabled': True},
                ],
                'symbols': [
                    {'symbol': 'BTC', 'name': 'Bitcoin', 'assetType': 'crypto'},
                    {'symbol': 'GOLD', 'name': 'Gold', 'assetType': 'commodity'},
                    {'symbol': 'SPX', 'name': 'S&P 500', 'assetType': 'index'},
                ],
                'status': 'active',
                'version': 3,
                'primaryAnalysisId': 'ana-1002',
                'analyses': [
                    {'id': 'ana-1001', 'trigger': 'schedule', 'status': 'done', 'isPrimary': False, 'createdAt': '2026-04-02 09:20'},
                    {'id': 'ana-1002', 'trigger': 'manual', 'status': 'done', 'isPrimary': True, 'createdAt': '2026-04-02 10:05'},
                ],
                'news': [
                    {'id': 'news-1', 'type': 'manual', 'text': '美国3月CPI同比回落但核心项仍偏高', 'createdAt': '2026-04-02 09:10'}
                ],
                'sources': ['https://example.com/rss/fed'],
            },
            {
                'id': 'evt-002',
                'title': 'AI 算力链景气度',
                'topic': 'AI Compute Cycle',
                'description': '追踪算力供需、财报指引与估值扩张节奏。',
                'keywords': [
                    {'term': 'gpu', 'weight': 0.9, 'enabled': True},
                    {'term': 'datacenter', 'weight': 0.7, 'enabled': True},
                ],
                'symbols': [
                    {'symbol': 'NVDA', 'name': 'NVIDIA', 'assetType': 'stock'},
                    {'symbol': 'TSM', 'name': 'TSMC', 'assetType': 'stock'},
                ],
                'status': 'draft',
                'version': 1,
                'primaryAnalysisId': '',
                'analyses': [],
                'news': [],
                'sources': [],
            },
        ],
        'globalTradeSettings': {
            'riskLevel': 6,
            'positionSize': 25,
            'takeProfit': 6.5,
            'stopLoss': 3.5,
            'thresholds': {'buy': 0.68, 'sell': 0.38, 'warning': 0.55},
        },
        'eventTradeSettings': {
            'evt-001': {'useGlobal': False, 'overrides': {'riskLevel': 7, 'positionSize': 30, 'takeProfit': 7.2, 'stopLoss': 3.2}}
        },
        'analysisTasks': [],
        'users': [{'id': 'seed-admin', 'privyUserId': 'privy_admin_seed_001', 'role': 'admin', 'status': 'enabled'}],
    }


ADMIN_STATE = default_state()
TOKEN_SECRET = (os.getenv('ADMIN_TOKEN_SECRET', '').strip() or 'zhidao-admin-dev-secret').encode('utf-8')
TOKEN_TTL_SECONDS = int(os.getenv('ADMIN_TOKEN_TTL_SECONDS', '604800') or 604800)


def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode('utf-8').rstrip('=')


def b64url_decode(raw: str) -> bytes:
    pad = '=' * ((4 - (len(raw) % 4)) % 4)
    return base64.urlsafe_b64decode((raw + pad).encode('utf-8'))


def sign_token(payload: dict) -> str:
    body = b64url_encode(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
    sig = b64url_encode(hmac.new(TOKEN_SECRET, body.encode('utf-8'), hashlib.sha256).digest())
    return f'{body}.{sig}'


def verify_token(token: str):
    try:
        body, sig = token.split('.', 1)
        expected = b64url_encode(hmac.new(TOKEN_SECRET, body.encode('utf-8'), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(b64url_decode(body).decode('utf-8'))
        if int(payload.get('exp', 0)) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def get_admin_users():
    return [u for u in ADMIN_STATE.get('users', []) if str(u.get('role', '')).lower() == 'admin' and str(u.get('status', '')).lower() == 'enabled']


def is_allowed_admin(privy_user_id: str) -> bool:
    user_id = str(privy_user_id or '').strip()
    if not user_id:
        return False
    env_allow = [x.strip() for x in (os.getenv('ADMIN_PRIVY_ALLOWLIST', '') or '').split(',') if x.strip()]
    if env_allow and user_id in env_allow:
        return True
    return any(str(u.get('privyUserId')) == user_id for u in get_admin_users())


def bearer_token_from_headers(handler: BaseHTTPRequestHandler) -> str:
    auth = str(handler.headers.get('Authorization', '') or '')
    if auth.lower().startswith('bearer '):
        return auth[7:].strip()
    return ''


def current_user_from_token(handler: BaseHTTPRequestHandler):
    token = bearer_token_from_headers(handler)
    if not token:
        return None
    payload = verify_token(token)
    if not payload:
        return None
    privy_user_id = str(payload.get('privyUserId', '')).strip()
    role = str(payload.get('role', '')).strip()
    if role != 'admin':
        return None
    if not is_allowed_admin(privy_user_id):
        return None
    admin_user = next((u for u in get_admin_users() if str(u.get('privyUserId')) == privy_user_id), None)
    if admin_user:
        return deepcopy(admin_user)
    return {'id': f'admin-{privy_user_id}', 'privyUserId': privy_user_id, 'role': 'admin', 'status': 'enabled'}


def verify_privy_login(payload: dict):
    privy_user_id = str(payload.get('privyUserId') or '').strip()
    privy_token = str(payload.get('privyToken') or '').strip()
    bootstrap_token = str(os.getenv('ADMIN_BOOTSTRAP_TOKEN', '') or '').strip()
    if not privy_user_id:
        return {'ok': False, 'error': 'privyUserId required'}, 400
    if not is_allowed_admin(privy_user_id):
        return {'ok': False, 'error': 'admin not allowed'}, 403
    if bootstrap_token and privy_token != bootstrap_token:
        return {'ok': False, 'error': 'invalid bootstrap token'}, 401
    now = int(time.time())
    exp = now + max(300, TOKEN_TTL_SECONDS)
    token = sign_token({'privyUserId': privy_user_id, 'role': 'admin', 'iat': now, 'exp': exp})
    admin_user = next((u for u in get_admin_users() if str(u.get('privyUserId')) == privy_user_id), None)
    if not admin_user:
        admin_user = {'id': f'admin-{privy_user_id}', 'privyUserId': privy_user_id, 'role': 'admin', 'status': 'enabled'}
    return {'ok': True, 'accessToken': token, 'expiresAt': exp, 'user': deepcopy(admin_user)}, 200


def get_event(event_id):
    for evt in ADMIN_STATE.get('events', []):
        if str(evt.get('id')) == str(event_id):
            return evt
    return None


def next_id(prefix):
    return f'{prefix}-{str(int(time.time() * 1000))[-6:]}'


def list_events(query):
    status = (query.get('status') or [''])[0].strip().lower()
    q = (query.get('q') or [''])[0].strip().lower()
    events = ADMIN_STATE.get('events', [])
    out = []
    for evt in events:
        if status and str(evt.get('status', '')).lower() != status:
            continue
        if q:
            hit = (evt.get('title', '') + ' ' + evt.get('topic', '')).lower()
            if q not in hit:
                continue
        out.append(deepcopy(evt))
    return {'ok': True, 'items': out, 'total': len(out)}


def create_event(payload):
    event_id = next_id('evt')
    item = {
        'id': event_id,
        'title': str(payload.get('title') or '').strip(),
        'topic': str(payload.get('topic') or '').strip(),
        'description': str(payload.get('description') or '').strip(),
        'keywords': payload.get('keywords') if isinstance(payload.get('keywords'), list) else [],
        'symbols': payload.get('symbols') if isinstance(payload.get('symbols'), list) else [],
        'status': str(payload.get('status') or 'draft'),
        'version': 1,
        'primaryAnalysisId': '',
        'analyses': [],
        'news': [],
        'sources': [],
    }
    ADMIN_STATE['events'].insert(0, item)
    ADMIN_STATE['selectedEventId'] = event_id
    return {'ok': True, 'item': deepcopy(item)}


def update_event(event_id, payload):
    evt = get_event(event_id)
    if not evt:
        return None
    for key in ['title', 'topic', 'description', 'keywords', 'symbols', 'status']:
        if key in payload:
            evt[key] = payload.get(key)
    evt['version'] = parse_int(evt.get('version', 0), 0) + 1
    return {'ok': True, 'item': deepcopy(evt)}


def delete_event(event_id):
    events = ADMIN_STATE.get('events', [])
    idx = -1
    for i, item in enumerate(events):
        if str(item.get('id')) == str(event_id):
            idx = i
            break
    if idx < 0:
        return False
    del events[idx]
    if event_id in ADMIN_STATE.get('eventTradeSettings', {}):
        del ADMIN_STATE['eventTradeSettings'][event_id]
    ADMIN_STATE['analysisTasks'] = [t for t in ADMIN_STATE.get('analysisTasks', []) if str(t.get('eventId')) != str(event_id)]
    if ADMIN_STATE.get('selectedEventId') == event_id:
        ADMIN_STATE['selectedEventId'] = events[0]['id'] if events else None
    return True


def add_news(event_id, payload):
    evt = get_event(event_id)
    if not evt:
        return None
    text = str(payload.get('content') or payload.get('title') or '').strip()
    if not text:
        return {'ok': False, 'error': 'empty news'}
    item = {'id': next_id('news'), 'type': 'manual', 'text': text, 'createdAt': now_str()}
    evt.setdefault('news', []).insert(0, item)
    return {'ok': True, 'item': deepcopy(item)}


def add_news_source(event_id, payload):
    evt = get_event(event_id)
    if not evt:
        return None
    url = str(payload.get('url') or '').strip()
    if not url:
        return {'ok': False, 'error': 'empty source url'}
    evt.setdefault('sources', []).append(url)
    item = {'id': next_id('source'), 'type': 'source', 'text': '新增新闻源：' + url, 'createdAt': now_str()}
    evt.setdefault('news', []).insert(0, item)
    return {'ok': True, 'item': deepcopy(item)}


def run_analysis(event_id, payload):
    evt = get_event(event_id)
    if not evt:
        return None
    analysis_id = next_id('ana')
    trigger = str(payload.get('trigger') or 'manual')
    entry = {'id': analysis_id, 'trigger': trigger, 'status': 'done', 'isPrimary': False, 'createdAt': now_str()}
    evt.setdefault('analyses', []).insert(0, entry)
    task = {
        'taskId': next_id('task'),
        'eventId': event_id,
        'eventTitle': evt.get('title', ''),
        'status': 'done',
        'startedAt': now_str(),
        'endedAt': now_str(),
    }
    ADMIN_STATE.setdefault('analysisTasks', []).insert(0, task)
    return {'ok': True, 'taskId': task['taskId'], 'analysisId': analysis_id, 'status': 'done'}


def set_primary_analysis(event_id, analysis_id):
    evt = get_event(event_id)
    if not evt:
        return None
    found = False
    for a in evt.get('analyses', []):
        matched = str(a.get('id')) == str(analysis_id)
        a['isPrimary'] = matched
        if matched:
            found = True
    if not found:
        return {'ok': False, 'error': 'analysis not found'}
    evt['primaryAnalysisId'] = analysis_id
    return {'ok': True, 'primaryAnalysisId': analysis_id}


def get_event_trade_settings(event_id):
    record = ADMIN_STATE.get('eventTradeSettings', {}).get(event_id)
    if record is None:
        g = ADMIN_STATE.get('globalTradeSettings', {})
        record = {
            'useGlobal': True,
            'overrides': {
                'riskLevel': parse_int(g.get('riskLevel'), 5),
                'positionSize': parse_int(g.get('positionSize'), 20),
                'takeProfit': parse_float(g.get('takeProfit'), 5),
                'stopLoss': parse_float(g.get('stopLoss'), 3),
            },
        }
    return {'ok': True, **deepcopy(record)}


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        json_resp(self, 200, {'ok': True})

    def do_GET(self):
        self._dispatch('GET')

    def do_POST(self):
        self._dispatch('POST')

    def do_PUT(self):
        self._dispatch('PUT')

    def do_DELETE(self):
        self._dispatch('DELETE')

    def _dispatch(self, method: str):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query or '')
        body = read_json_body(self) if method in {'POST', 'PUT'} else {}

        code, payload = handle_request(self, method, path, query, body)
        json_resp(self, code, payload)


def handle_request(req_handler: BaseHTTPRequestHandler, method: str, path: str, query: dict, body: dict):
    body = body if isinstance(body, dict) else {}

    if path == '/api/admin/auth/privy/verify' and method == 'POST':
        payload, code = verify_privy_login(body)
        return code, payload

    user = current_user_from_token(req_handler)
    if not user:
        return 401, {'ok': False, 'error': 'unauthorized'}

    if path == '/api/admin/me' and method == 'GET':
        return 200, {'ok': True, **deepcopy(user)}

    if path == '/api/admin/users' and method == 'GET':
        return 200, {'ok': True, 'items': deepcopy(ADMIN_STATE.get('users', []))}

    if path == '/api/admin/analysis/tasks' and method == 'GET':
        return 200, {'ok': True, 'items': deepcopy(ADMIN_STATE.get('analysisTasks', [])), 'total': len(ADMIN_STATE.get('analysisTasks', []))}

    if path == '/api/admin/trade-settings/global':
        if method == 'GET':
            return 200, {'ok': True, **deepcopy(ADMIN_STATE.get('globalTradeSettings', {}))}
        if method == 'PUT':
            ADMIN_STATE['globalTradeSettings'] = {
                'riskLevel': parse_int(body.get('riskLevel'), 5),
                'positionSize': parse_int(body.get('positionSize'), 20),
                'takeProfit': parse_float(body.get('takeProfit'), 5),
                'stopLoss': parse_float(body.get('stopLoss'), 3),
                'thresholds': {
                    'buy': parse_float((body.get('thresholds') or {}).get('buy'), 0.65),
                    'sell': parse_float((body.get('thresholds') or {}).get('sell'), 0.35),
                    'warning': parse_float((body.get('thresholds') or {}).get('warning'), 0.55),
                },
            }
            return 200, {'ok': True, **deepcopy(ADMIN_STATE['globalTradeSettings'])}

    if path == '/api/admin/events' and method == 'GET':
        return 200, list_events(query)
    if path == '/api/admin/events' and method == 'POST':
        if not body.get('title') or not body.get('topic'):
            return 400, {'ok': False, 'error': 'title/topic required'}
        return 200, create_event(body)

    # /api/admin/events/:id...
    if path.startswith('/api/admin/events/'):
        rest = path[len('/api/admin/events/'):]
        parts = [p for p in rest.split('/') if p]
        event_id = parts[0] if parts else ''
        evt = get_event(event_id)
        if not evt:
            return 404, {'ok': False, 'error': 'event not found'}

        if len(parts) == 1:
            if method == 'GET':
                return 200, {'ok': True, 'item': deepcopy(evt)}
            if method == 'PUT':
                return 200, update_event(event_id, body)
            if method == 'DELETE':
                delete_event(event_id)
                return 200, {'ok': True}

        # /news
        if len(parts) == 2 and parts[1] == 'news' and method == 'POST':
            result = add_news(event_id, body)
            code = 200 if result and result.get('ok') else 400
            return code, result or {'ok': False, 'error': 'event not found'}

        # /news-sources
        if len(parts) == 2 and parts[1] == 'news-sources' and method == 'POST':
            result = add_news_source(event_id, body)
            code = 200 if result and result.get('ok') else 400
            return code, result or {'ok': False, 'error': 'event not found'}

        # /analyses
        if len(parts) == 2 and parts[1] == 'analyses' and method == 'GET':
            return 200, {'ok': True, 'items': deepcopy(evt.get('analyses', []))}

        # /analyses/run
        if len(parts) == 3 and parts[1] == 'analyses' and parts[2] == 'run' and method == 'POST':
            return 200, run_analysis(event_id, body)

        # /analyses/:analysisId/set-primary
        if len(parts) == 4 and parts[1] == 'analyses' and parts[3] == 'set-primary' and method == 'POST':
            return 200, set_primary_analysis(event_id, parts[2])

        # /trade-settings
        if len(parts) == 2 and parts[1] == 'trade-settings':
            if method == 'GET':
                return 200, get_event_trade_settings(event_id)
            if method == 'PUT':
                record = {
                    'useGlobal': bool(body.get('useGlobal', True)),
                    'overrides': {
                        'riskLevel': parse_int((body.get('overrides') or {}).get('riskLevel'), 5),
                        'positionSize': parse_int((body.get('overrides') or {}).get('positionSize'), 20),
                        'takeProfit': parse_float((body.get('overrides') or {}).get('takeProfit'), 5),
                        'stopLoss': parse_float((body.get('overrides') or {}).get('stopLoss'), 3),
                    },
                }
                ADMIN_STATE.setdefault('eventTradeSettings', {})[event_id] = record
                return 200, {'ok': True, **deepcopy(record)}

    if path == '/api/admin/state':
        if method == 'GET':
            return 200, {'ok': True, 'schemaVersion': 1, 'state': deepcopy(ADMIN_STATE)}
        if method == 'PUT':
            incoming = body.get('state') if isinstance(body.get('state'), dict) else body
            if not isinstance(incoming, dict):
                return 400, {'ok': False, 'error': 'invalid state'}
            # Keep minimal shape stable
            merged = default_state()
            merged.update(incoming)
            ADMIN_STATE.clear()
            ADMIN_STATE.update(merged)
            return 200, {'ok': True}

    return 404, {'ok': False, 'error': f'not found: {method} {path}'}
