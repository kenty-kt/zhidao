from copy import deepcopy
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import base64
import email.utils
import hashlib
import hmac
import json
import os
import time
import urllib.request
import xml.etree.ElementTree as ET

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
        'feeds': [
            {
                'id': 'feed-001',
                'name': 'PA News 日历',
                'type': 'api',
                'url': '/api/panews/calendar?period=week',
                'status': 'active',
                'createdAt': '2026-04-02 09:00',
            },
            {
                'id': 'feed-002',
                'name': 'SoSo 板块',
                'type': 'api',
                'url': '/api/soso/sectors',
                'status': 'active',
                'createdAt': '2026-04-02 09:00',
            },
        ],
        'feedContents': [
            {
                'id': 'fc-001',
                'feedId': 'feed-001',
                'title': '美国 CPI 公布前市场波动放大',
                'url': 'https://example.com/news/cpi-vol',
                'summary': '市场提前交易通胀路径，风险资产短线波动增加。',
                'body': '美国 CPI 数据公布窗口临近，资金提前定价通胀路径，短周期波动明显放大。',
                'status': 'published',
                'tags': ['macro', 'cpi'],
                'assets': ['BTC', 'SPX', 'GOLD'],
                'createdAt': '2026-04-02 09:30',
                'updatedAt': '2026-04-02 09:30',
            },
            {
                'id': 'fc-002',
                'feedId': 'feed-001',
                'title': '美联储会议纪要偏鹰，风险资产短线承压',
                'url': 'https://example.com/news/fomc-hawkish',
                'summary': '会议纪要显示委员对通胀黏性仍担忧，降息预期延后。',
                'body': '最新会议纪要强调控制通胀的必要性，市场对年内降息次数预期从 3 次下修至 2 次。',
                'status': 'published',
                'tags': ['macro', 'rates'],
                'assets': ['SPX', 'BTC', 'DXY'],
                'createdAt': '2026-04-02 10:10',
                'updatedAt': '2026-04-02 10:10',
            },
            {
                'id': 'fc-003',
                'feedId': 'feed-001',
                'title': '非农数据超预期，美元指数走强',
                'url': 'https://example.com/news/nfp-strong',
                'summary': '就业市场韧性强化，美债收益率上行。',
                'body': '新增就业高于一致预期，失业率维持低位，强化了“高利率更久”的交易主线。',
                'status': 'published',
                'tags': ['macro', 'employment'],
                'assets': ['DXY', 'GOLD', 'SPX'],
                'createdAt': '2026-04-02 10:35',
                'updatedAt': '2026-04-02 10:35',
            },
            {
                'id': 'fc-004',
                'feedId': 'feed-002',
                'title': 'BTC ETF 净流入回升，链上活跃度改善',
                'url': 'https://example.com/news/btc-etf-inflow',
                'summary': 'ETF 资金回流与链上数据共振，风险偏好抬升。',
                'body': '过去 24 小时主要 ETF 产品录得净流入，交易所净流出增加，供给端压力阶段性缓解。',
                'status': 'published',
                'tags': ['crypto', 'etf'],
                'assets': ['BTC', 'ETH'],
                'createdAt': '2026-04-02 11:00',
                'updatedAt': '2026-04-02 11:00',
            },
            {
                'id': 'fc-005',
                'feedId': 'feed-002',
                'title': 'AI 服务器订单上修，半导体产业链景气延续',
                'url': 'https://example.com/news/ai-server-up',
                'summary': '上游算力需求旺盛，相关公司指引上调。',
                'body': '渠道调研显示 AI 服务器交付节奏加快，HBM 与先进封装环节维持高景气。',
                'status': 'published',
                'tags': ['ai', 'semiconductor'],
                'assets': ['NVDA', 'TSM', 'AMD'],
                'createdAt': '2026-04-02 11:20',
                'updatedAt': '2026-04-02 11:20',
            },
            {
                'id': 'fc-006',
                'feedId': 'feed-002',
                'title': '原油库存意外下降，油价短线拉升',
                'url': 'https://example.com/news/oil-inventory',
                'summary': '库存下降叠加地缘扰动，能源板块获得支撑。',
                'body': 'EIA 数据显示库存降幅高于预期，叠加航运风险，布油与 WTI 同步上行。',
                'status': 'draft',
                'tags': ['commodity', 'energy'],
                'assets': ['WTI', 'BRENT', 'XLE'],
                'createdAt': '2026-04-02 11:45',
                'updatedAt': '2026-04-02 11:45',
            },
            {
                'id': 'fc-007',
                'feedId': 'feed-001',
                'title': '欧洲通胀回落超预期，欧元区债券走强',
                'url': 'https://example.com/news/eu-cpi-down',
                'summary': '欧央行宽松预期升温，核心资产波动加大。',
                'body': '欧元区核心 CPI 继续下行，市场对降息窗口前移的定价明显提升。',
                'status': 'published',
                'tags': ['macro', 'europe'],
                'assets': ['EURUSD', 'DAX', 'EU10Y'],
                'createdAt': '2026-04-02 12:10',
                'updatedAt': '2026-04-02 12:10',
            },
            {
                'id': 'fc-008',
                'feedId': 'feed-002',
                'title': '链上稳定币发行增长，风险偏好继续修复',
                'url': 'https://example.com/news/stablecoin-growth',
                'summary': '稳定币总市值扩张，市场流动性指标改善。',
                'body': '过去一周稳定币净增量延续，场内杠杆成本回落，山寨资产成交占比提升。',
                'status': 'archived',
                'tags': ['crypto', 'liquidity'],
                'assets': ['BTC', 'SOL', 'ETH'],
                'createdAt': '2026-04-02 12:30',
                'updatedAt': '2026-04-02 12:30',
            },
        ],
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


def list_feeds(query):
    status = (query.get('status') or [''])[0].strip().lower()
    q = (query.get('q') or [''])[0].strip().lower()
    out = []
    for feed in ADMIN_STATE.get('feeds', []):
        if status and str(feed.get('status', '')).lower() != status:
            continue
        text = (str(feed.get('name', '')) + ' ' + str(feed.get('url', ''))).lower()
        if q and q not in text:
            continue
        out.append(deepcopy(feed))
    return {'ok': True, 'items': out, 'total': len(out)}


def list_feed_contents(query):
    ensure_feed_contents_seed()
    q = (query.get('q') or [''])[0].strip().lower()
    feed_id = (query.get('feedId') or [''])[0].strip()
    status = (query.get('status') or [''])[0].strip().lower()
    out = []
    for item in ADMIN_STATE.get('feedContents', []):
        if feed_id and str(item.get('feedId')) != feed_id:
            continue
        if status and str(item.get('status', '')).lower() != status:
            continue
        text = (
            str(item.get('title', '')) + ' ' +
            str(item.get('summary', '')) + ' ' +
            str(item.get('body', '')) + ' ' +
            str(item.get('url', '')) + ' ' +
            ','.join(item.get('tags', []) if isinstance(item.get('tags'), list) else []) + ' ' +
            ','.join(item.get('assets', []) if isinstance(item.get('assets'), list) else [])
        ).lower()
        if q and q not in text:
            continue
        out.append(deepcopy(item))
    return {'ok': True, 'items': out, 'total': len(out)}


def ensure_feed_contents_seed():
    contents = ADMIN_STATE.setdefault('feedContents', [])
    if len(contents) >= 8:
        return
    seeded = default_state().get('feedContents', [])
    existing_ids = {str(x.get('id')) for x in contents}
    for item in seeded:
        if str(item.get('id')) in existing_ids:
            continue
        contents.append(deepcopy(item))
        if len(contents) >= 8:
            break


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


def _safe_text(node, path):
    if node is None:
        return ''
    val = node.findtext(path) or ''
    return str(val).strip()


def parse_rss_items(xml_text: str, limit: int = 30):
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []
    out = []
    # RSS
    rss_items = root.findall('.//channel/item')
    if rss_items:
        for it in rss_items[:limit]:
            title = _safe_text(it, 'title')
            link = _safe_text(it, 'link')
            desc = _safe_text(it, 'description')
            pub = _safe_text(it, 'pubDate')
            if not title and not link:
                continue
            out.append({'title': title or link, 'url': link, 'summary': desc[:400], 'body': desc, 'publishedAt': pub})
        return out
    # Atom
    atom_items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
    for it in atom_items[:limit]:
        title = _safe_text(it, '{http://www.w3.org/2005/Atom}title')
        link = ''
        for ln in it.findall('{http://www.w3.org/2005/Atom}link'):
            href = str(ln.attrib.get('href') or '').strip()
            if href:
                link = href
                break
        summary = _safe_text(it, '{http://www.w3.org/2005/Atom}summary')
        body = _safe_text(it, '{http://www.w3.org/2005/Atom}content') or summary
        pub = _safe_text(it, '{http://www.w3.org/2005/Atom}updated') or _safe_text(it, '{http://www.w3.org/2005/Atom}published')
        if not title and not link:
            continue
        out.append({'title': title or link, 'url': link, 'summary': summary[:400], 'body': body, 'publishedAt': pub})
    return out


def normalize_datetime_str(value: str):
    raw = str(value or '').strip()
    if not raw:
        return now_str()
    dt = None
    try:
        dt = email.utils.parsedate_to_datetime(raw)
    except Exception:
        dt = None
    if dt is not None:
        return dt.strftime('%Y-%m-%d %H:%M')
    # pass-through common ISO-ish values
    return raw[:16].replace('T', ' ') if len(raw) >= 16 else raw


def sync_rss_feed(feed_id: str):
    feed = find_feed(feed_id)
    if not feed:
        return {'ok': False, 'error': 'feed not found'}
    feed_type = str(feed.get('type') or '').lower()
    if feed_type != 'rss':
        return {'ok': False, 'error': 'only rss feed can sync'}
    url = str(feed.get('url') or '').strip()
    if not url.startswith('http://') and not url.startswith('https://'):
        return {'ok': False, 'error': 'feed url must be http/https'}
    xml = fetch_text(url)
    if '<rss' not in xml and '<feed' not in xml:
        return {'ok': False, 'error': 'invalid rss xml'}
    items = parse_rss_items(xml, limit=50)
    if not items:
        return {'ok': True, 'added': 0, 'totalFetched': 0}
    contents = ADMIN_STATE.setdefault('feedContents', [])
    existing_keys = {
        (str(x.get('feedId') or ''), str(x.get('url') or '').strip(), str(x.get('title') or '').strip())
        for x in contents
    }
    added = 0
    for it in items:
        key = (feed_id, str(it.get('url') or '').strip(), str(it.get('title') or '').strip())
        if key in existing_keys:
            continue
        existing_keys.add(key)
        t = normalize_datetime_str(it.get('publishedAt') or '')
        item = {
            'id': next_id('fc'),
            'feedId': feed_id,
            'title': str(it.get('title') or '').strip()[:220] or 'Untitled',
            'url': str(it.get('url') or '').strip(),
            'summary': str(it.get('summary') or '').strip()[:500],
            'body': str(it.get('body') or '').strip()[:4000],
            'status': 'draft',
            'tags': ['rss'],
            'assets': [],
            'createdAt': t,
            'updatedAt': t,
        }
        contents.insert(0, item)
        added += 1
    return {'ok': True, 'added': added, 'totalFetched': len(items)}


def find_feed(feed_id):
    for feed in ADMIN_STATE.get('feeds', []):
        if str(feed.get('id')) == str(feed_id):
            return feed
    return None


def find_feed_content(content_id):
    for item in ADMIN_STATE.get('feedContents', []):
        if str(item.get('id')) == str(content_id):
            return item
    return None


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

    if path == '/api/admin/feeds' and method == 'GET':
        return 200, list_feeds(query)
    if path == '/api/admin/feeds' and method == 'POST':
        name = str(body.get('name') or '').strip()
        url = str(body.get('url') or '').strip()
        if not name or not url:
            return 400, {'ok': False, 'error': 'name/url required'}
        item = {
            'id': next_id('feed'),
            'name': name,
            'type': str(body.get('type') or 'rss').strip() or 'rss',
            'url': url,
            'status': str(body.get('status') or 'active').strip() or 'active',
            'createdAt': now_str(),
        }
        ADMIN_STATE.setdefault('feeds', []).insert(0, item)
        sync = None
        if str(item.get('type') or '').lower() == 'rss' and str(item.get('status') or '').lower() == 'active':
            try:
                sync = sync_rss_feed(item['id'])
            except Exception as e:
                sync = {'ok': False, 'error': str(e)}
        return 200, {'ok': True, 'item': deepcopy(item), 'sync': sync}

    if path.startswith('/api/admin/feeds/'):
        rest = path[len('/api/admin/feeds/'):].strip('/')
        parts = [p for p in rest.split('/') if p]
        feed_id = parts[0] if parts else ''
        if len(parts) == 2 and parts[1] == 'sync' and method == 'POST':
            result = sync_rss_feed(feed_id)
            code = 200 if result.get('ok') else 400
            return code, result
        feed = find_feed(feed_id)
        if not feed:
            return 404, {'ok': False, 'error': 'feed not found'}
        if method == 'GET':
            return 200, {'ok': True, 'item': deepcopy(feed)}
        if method == 'PUT':
            for key in ['name', 'type', 'url', 'status']:
                if key in body:
                    feed[key] = body.get(key)
            sync = None
            if str(feed.get('type') or '').lower() == 'rss' and str(feed.get('status') or '').lower() == 'active':
                try:
                    sync = sync_rss_feed(feed_id)
                except Exception as e:
                    sync = {'ok': False, 'error': str(e)}
            return 200, {'ok': True, 'item': deepcopy(feed), 'sync': sync}
        if method == 'DELETE':
            ADMIN_STATE['feeds'] = [f for f in ADMIN_STATE.get('feeds', []) if str(f.get('id')) != str(feed_id)]
            ADMIN_STATE['feedContents'] = [c for c in ADMIN_STATE.get('feedContents', []) if str(c.get('feedId')) != str(feed_id)]
            return 200, {'ok': True}

    if path == '/api/admin/feed-contents' and method == 'GET':
        return 200, list_feed_contents(query)
    if path == '/api/admin/feed-contents' and method == 'POST':
        feed_id = str(body.get('feedId') or '').strip()
        title = str(body.get('title') or '').strip()
        if not feed_id or not title:
            return 400, {'ok': False, 'error': 'feedId/title required'}
        if not find_feed(feed_id):
            return 404, {'ok': False, 'error': 'feed not found'}
        item = {
            'id': next_id('fc'),
            'feedId': feed_id,
            'title': title,
            'url': str(body.get('url') or '').strip(),
            'summary': str(body.get('summary') or '').strip(),
            'body': str(body.get('body') or '').strip(),
            'status': str(body.get('status') or 'draft').strip() or 'draft',
            'tags': body.get('tags') if isinstance(body.get('tags'), list) else [],
            'assets': body.get('assets') if isinstance(body.get('assets'), list) else [],
            'createdAt': now_str(),
            'updatedAt': now_str(),
        }
        ADMIN_STATE.setdefault('feedContents', []).insert(0, item)
        return 200, {'ok': True, 'item': deepcopy(item)}

    if path.startswith('/api/admin/feed-contents/'):
        content_id = path[len('/api/admin/feed-contents/'):].strip('/')
        item = find_feed_content(content_id)
        if not item:
            return 404, {'ok': False, 'error': 'content not found'}
        if method == 'GET':
            return 200, {'ok': True, 'item': deepcopy(item)}
        if method == 'PUT':
            for key in ['feedId', 'title', 'url', 'summary', 'body', 'status', 'tags', 'assets']:
                if key in body:
                    item[key] = body.get(key)
            item['updatedAt'] = now_str()
            return 200, {'ok': True, 'item': deepcopy(item)}
        if method == 'DELETE':
            ADMIN_STATE['feedContents'] = [c for c in ADMIN_STATE.get('feedContents', []) if str(c.get('id')) != str(content_id)]
            return 200, {'ok': True}

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
