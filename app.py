#!/usr/bin/env python3
import base64
import html
import hashlib
import hmac
import json
import math
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


OKX_BASE = "https://www.okx.com"
SOSO_MIRROR_URL = "https://r.jina.ai/http://sosovalue.com/zh"
PANEWS_CALENDAR_URL = "https://www.panewslab.com/zh/calendar"
OKX_KEY = os.getenv("OKX_API_KEY", "").strip()
OKX_SECRET = os.getenv("OKX_API_SECRET", "").strip()
OKX_PASSPHRASE = os.getenv("OKX_API_PASSPHRASE", "").strip()
OKX_SIMULATED = os.getenv("OKX_SIMULATED_TRADING", "").strip() == "1"
PANEWS_CACHE = {}


def json_resp(handler: SimpleHTTPRequestHandler, code: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def okx_private_get(path: str, params: dict = None):
    return okx_private_request("GET", path, params=params)


def okx_private_post(path: str, body: dict = None):
    return okx_private_request("POST", path, body=body)


def okx_private_request(method: str, path: str, params: dict = None, body: dict = None):
    if not OKX_KEY or not OKX_SECRET:
        raise RuntimeError("OKX_API_KEY/OKX_API_SECRET not configured")
    if not OKX_PASSPHRASE:
        raise RuntimeError("OKX_API_PASSPHRASE not configured")
    m = method.upper()
    query = urllib.parse.urlencode(params or {})
    request_path = f"{path}?{query}" if query else path
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    body_str = ""
    if m == "POST":
        body_str = json.dumps(body or {}, separators=(",", ":"))
    prehash = f"{timestamp}{m}{request_path}{body_str}"
    sign = base64.b64encode(hmac.new(OKX_SECRET.encode("utf-8"), prehash.encode("utf-8"), hashlib.sha256).digest()).decode("utf-8")
    data = body_str.encode("utf-8") if m == "POST" else None
    last_err = None
    for _ in range(3):
        req = urllib.request.Request(
            f"{OKX_BASE}{request_path}",
            data=data,
            method=m,
            headers={
                "OK-ACCESS-KEY": OKX_KEY,
                "OK-ACCESS-SIGN": sign,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": OKX_PASSPHRASE,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                **({"x-simulated-trading": "1"} if OKX_SIMULATED else {}),
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            try:
                detail = json.loads(body)
                raise RuntimeError(f"OKX_HTTP_{e.code}: {json.dumps(detail, ensure_ascii=False)}")
            except Exception:
                detail = body.strip().replace("\n", " ")[:300]
                raise RuntimeError(f"OKX_HTTP_{e.code}: {detail}")
        except Exception as e:
            last_err = e
            time.sleep(0.25)
    raise last_err if last_err else RuntimeError("OKX private request failed")


def okx_public_get(path: str, params: dict = None):
    query = urllib.parse.urlencode(params or {})
    url = f"{OKX_BASE}{path}" + (f"?{query}" if query else "")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        },
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_okx_positions():
    positions = okx_private_get("/api/v5/account/positions")
    if str(positions.get("code", "")) not in {"0", ""}:
        raise RuntimeError(f"OKX_POSITIONS_ERR: {positions.get('msg') or positions.get('code')}")

    rows = []
    pos_list = positions.get("data", [])
    for p in pos_list if isinstance(pos_list, list) else []:
        pos = float(p.get("pos", 0) or 0)
        if abs(pos) < 1e-12:
            continue
        inst_id = str(p.get("instId", ""))
        symbol = (inst_id.split("-")[0] if inst_id else "").upper()
        if not symbol:
            continue
        pos_side = str(p.get("posSide", "")).lower()
        if pos_side == "long":
            side = "LONG"
        elif pos_side == "short":
            side = "SHORT"
        else:
            side = "LONG" if pos > 0 else "SHORT"
        notional = abs(float(p.get("notionalUsd", 0) or 0))
        if notional <= 0:
            notional = abs(float(p.get("notional", 0) or 0))
        mark_px = float(p.get("markPx", 0) or 0)
        if notional <= 0 and mark_px > 0:
            notional = abs(pos) * mark_px
        if notional <= 1:
            continue
        entry_px = float(p.get("avgPx", 0) or 0)
        leverage = str(p.get("lever", "")).strip() or "1"
        upl = float(p.get("upl", 0) or 0)
        pnl_pct = float(p.get("uplRatio", 0) or 0) * 100.0
        if abs(pnl_pct) < 1e-12:
            pnl_pct = (upl / notional * 100) if notional else 0.0
        rows.append(
            {
                "asset": symbol,
                "symbol": symbol,
                "qty": abs(pos),
                "side": side,
                "source": "derivative",
                "usdtValue": notional,
                "pair": inst_id or f"{symbol}-USDT",
                "pnlPct": pnl_pct,
                "pnlValue": upl,
                "instrument": inst_id,
                "leverage": leverage,
                "markPx": mark_px,
                "entryPx": entry_px,
            }
        )

    return rows


def fetch_okx_ticker(inst_id: str):
    data = okx_public_get("/api/v5/market/ticker", {"instId": inst_id})
    if str(data.get("code", "")) not in {"0", ""}:
        raise RuntimeError(f"OKX_TICKER_ERR: {data.get('msg') or data.get('code')}")
    item = (data.get("data") or [{}])[0]
    return {
        "instId": inst_id,
        "last": float(item.get("last", 0) or 0),
        "markPx": float(item.get("markPx", 0) or 0),
        "bidPx": float(item.get("bidPx", 0) or 0),
        "askPx": float(item.get("askPx", 0) or 0),
    }


def fetch_okx_account_overview():
    bal = okx_private_get("/api/v5/account/balance", {"ccy": "USDT"})
    if str(bal.get("code", "")) not in {"0", ""}:
        raise RuntimeError(f"OKX_BALANCE_ERR: {bal.get('msg') or bal.get('code')}")
    d0 = (bal.get("data") or [{}])[0]
    details = d0.get("details", []) if isinstance(d0, dict) else []
    usdt = None
    for x in details if isinstance(details, list) else []:
        if str(x.get("ccy", "")).upper() == "USDT":
            usdt = x
            break
    usdt = usdt or {}
    usdt_avail = float(usdt.get("availBal", 0) or 0)
    usdt_cash = float(usdt.get("cashBal", 0) or 0)
    if usdt_avail <= 0 and usdt_cash > 0:
        usdt_avail = usdt_cash
    return {
        "ok": True,
        "simulated": OKX_SIMULATED,
        "usdtAvail": usdt_avail,
        "usdtCash": usdt_cash,
        "totalEqUsd": float(d0.get("totalEq", 0) or 0),
    }


def fetch_soso_sector_board():
    req = urllib.request.Request(
        SOSO_MIRROR_URL,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        text = resp.read().decode("utf-8", errors="ignore")

    # Example fragment:
    # [57.40%BTC+3.14%](http://sosovalue.com/zh/sectors/btc)
    pat = re.compile(
        r"\[(\d+(?:\.\d+)?)%([A-Za-z][A-Za-z0-9]*)\s*([+-]\d+(?:\.\d+)?)%\]\((https?://sosovalue\.com/zh/sectors/[^)]+)\)"
    )
    rows = []
    seen = set()
    for m in pat.finditer(text):
        share = float(m.group(1))
        name = m.group(2)
        change = float(m.group(3))
        link = m.group(4)
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        rows.append({"name": name, "share": share, "change": change, "link": link})

    if len(rows) < 5:
        raise RuntimeError("SOSO_SECTOR_PARSE_FAILED")

    return rows[:16]


def fetch_panews_calendar(date_str: str, period: str = "week"):
    safe_period = period if period in {"week", "month"} else "week"
    safe_date = date_str if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str or "") else time.strftime("%Y-%m-%d", time.gmtime())
    q = urllib.parse.urlencode({"mode": "calendar", "period": safe_period, "date": safe_date})
    req = urllib.request.Request(
        f"{PANEWS_CALENDAR_URL}?{q}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        page = resp.read().decode("utf-8", errors="ignore")

    m = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', page, flags=re.S | re.I)
    if not m:
        raise RuntimeError("PANEWS_PARSE_FAILED: __NUXT_DATA__ missing")
    blob = html.unescape(m.group(1))

    # Event object carries id/startAt index pair. The resolved ISO string appears right after the object.
    time_map = {}
    for mm in re.finditer(r'\{"id":(\d+),"startAt":\d+,[^{}]*?\},"[^"]*","([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:\.]+Z)"', blob):
        eid = mm.group(1)
        if eid not in time_map:
            time_map[eid] = mm.group(2)

    # Translation object carries eventId/title index pair. Resolved title appears right after the object.
    title_map = {}
    for mm in re.finditer(r'\{"id":\d+,"lang":\d+,"title":\d+,"eventId":(\d+)[^{}]*?\},"[^"]*","([^"]+)"', blob):
        eid = mm.group(1)
        title = mm.group(2).strip()
        if eid not in title_map and title:
            title_map[eid] = title

    items = []
    seen = set()
    for eid, ts in time_map.items():
        title = title_map.get(eid, "").strip()
        if not title:
            continue
        key = f"{ts}|{title}"
        if key in seen:
            continue
        seen.add(key)
        items.append({"eventId": eid, "title": title, "startAt": ts})

    items.sort(key=lambda x: x.get("startAt", ""))
    if not items:
        raise RuntimeError("PANEWS_PARSE_FAILED: no events")
    return items[:200]


def _format_step(v: float):
    s = f"{v:.12f}".rstrip("0").rstrip(".")
    return s or "0"


def _floor_to_step(val: float, step: float):
    if step <= 0:
        return val
    return math.floor(val / step) * step


def place_okx_order(payload: dict):
    inst_id = str(payload.get("instId", "")).upper().strip()
    if not inst_id:
        raise RuntimeError("instId required")
    if not inst_id.endswith("-SWAP"):
        raise RuntimeError("only SWAP instruments supported")

    side = str(payload.get("side", "")).lower().strip()
    if side not in {"buy", "sell"}:
        raise RuntimeError("side must be buy/sell")
    pos_side = str(payload.get("posSide", "")).lower().strip()
    if pos_side and pos_side not in {"long", "short", "net"}:
        raise RuntimeError("invalid posSide")

    ord_type = str(payload.get("ordType", "market")).lower().strip()
    if ord_type not in {"market", "limit"}:
        raise RuntimeError("ordType must be market/limit")

    qty_base = float(payload.get("qtyBase", 0) or 0)
    if qty_base <= 0:
        raise RuntimeError("qtyBase must be > 0")

    px = float(payload.get("px", 0) or 0)
    if ord_type == "limit" and px <= 0:
        raise RuntimeError("limit order px must be > 0")
    tp = float(payload.get("tp", 0) or 0)
    sl = float(payload.get("sl", 0) or 0)

    lever = float(payload.get("lever", 0) or 0)
    if lever > 0:
        lev_body = {"instId": inst_id, "mgnMode": "cross", "lever": _format_step(lever)}
        if pos_side in {"long", "short"}:
            lev_body["posSide"] = pos_side
        try:
            okx_private_post("/api/v5/account/set-leverage", lev_body)
        except Exception:
            pass

    ins = okx_public_get("/api/v5/public/instruments", {"instType": "SWAP", "instId": inst_id})
    if str(ins.get("code", "")) not in {"0", ""}:
        raise RuntimeError(f"OKX_INSTRUMENT_ERR: {ins.get('msg') or ins.get('code')}")
    d = (ins.get("data") or [{}])[0]
    ct_val = float(d.get("ctVal", 0) or 0)
    lot_sz = float(d.get("lotSz", 0) or 0)
    min_sz = float(d.get("minSz", 0) or 0)
    if ct_val <= 0:
        raise RuntimeError("invalid ctVal for instrument")

    sz = qty_base / ct_val
    if lot_sz > 0:
        sz = _floor_to_step(sz, lot_sz)
    if min_sz > 0 and sz < min_sz:
        sz = min_sz
    if sz <= 0:
        raise RuntimeError("computed order size is 0")

    order = {
        "instId": inst_id,
        "tdMode": "cross",
        "side": side,
        "ordType": ord_type,
        "sz": _format_step(sz),
    }
    if pos_side in {"long", "short", "net"}:
        order["posSide"] = pos_side
    if ord_type == "limit":
        order["px"] = _format_step(px)
    if tp > 0 or sl > 0:
        algo = {}
        if tp > 0:
            algo["tpTriggerPx"] = _format_step(tp)
            algo["tpOrdPx"] = "-1"
        if sl > 0:
            algo["slTriggerPx"] = _format_step(sl)
            algo["slOrdPx"] = "-1"
        order["attachAlgoOrds"] = [algo]

    result = okx_private_post("/api/v5/trade/order", order)
    if str(result.get("code", "")) not in {"0", ""} and "posSide" in order:
        # Some accounts run in net mode where posSide is rejected; retry once without posSide.
        order2 = dict(order)
        order2.pop("posSide", None)
        result = okx_private_post("/api/v5/trade/order", order2)
        if str(result.get("code", "")) in {"0", ""}:
            order = order2
    if str(result.get("code", "")) not in {"0", ""}:
        d0 = (result.get("data") or [{}])[0]
        detail = d0.get("sMsg") or result.get("msg") or result.get("code")
        raise RuntimeError(f"OKX_ORDER_ERR: {detail}")
    od = (result.get("data") or [{}])[0]
    return {
        "ok": True,
        "instId": inst_id,
        "ordId": od.get("ordId", ""),
        "clOrdId": od.get("clOrdId", ""),
        "sCode": od.get("sCode", ""),
        "sMsg": od.get("sMsg", ""),
        "side": side,
        "ordType": ord_type,
        "sz": order["sz"],
        "px": order.get("px", ""),
        "simulated": OKX_SIMULATED,
    }


def place_okx_close_position(payload: dict):
    inst_id = str(payload.get("instId", "")).upper().strip()
    if not inst_id:
        raise RuntimeError("instId required")
    if not inst_id.endswith("-SWAP"):
        raise RuntimeError("only SWAP instruments supported")

    pos_side = str(payload.get("positionSide", "")).lower().strip()
    if pos_side not in {"", "long", "short"}:
        raise RuntimeError("positionSide must be long/short")
    qty = float(payload.get("qty", 0) or 0)

    if qty <= 0:
        pos_resp = okx_private_get("/api/v5/account/positions", {"instId": inst_id})
        if str(pos_resp.get("code", "")) not in {"0", ""}:
            raise RuntimeError(f"OKX_POSITIONS_ERR: {pos_resp.get('msg') or pos_resp.get('code')}")
        candidates = []
        for p in pos_resp.get("data", []) if isinstance(pos_resp.get("data", []), list) else []:
            p_pos = float(p.get("pos", 0) or 0)
            if abs(p_pos) < 1e-12:
                continue
            p_side = str(p.get("posSide", "")).lower().strip()
            if p_side not in {"long", "short"}:
                p_side = "long" if p_pos > 0 else "short"
            candidates.append((abs(p_pos), p_side))
        if not candidates:
            raise RuntimeError("no open position to close")
        if pos_side in {"long", "short"}:
            same_side = [x for x in candidates if x[1] == pos_side]
            if same_side:
                qty = same_side[0][0]
            else:
                raise RuntimeError(f"no {pos_side} position to close")
        else:
            qty, pos_side = candidates[0]

    if pos_side not in {"long", "short"}:
        raise RuntimeError("positionSide required when qty is provided")

    side = "sell" if pos_side == "long" else "buy"
    order = {
        "instId": inst_id,
        "tdMode": "cross",
        "side": side,
        "ordType": "market",
        "sz": _format_step(qty),
        "reduceOnly": "true",
        "posSide": pos_side,
    }
    result = okx_private_post("/api/v5/trade/order", order)
    if str(result.get("code", "")) not in {"0", ""} and "posSide" in order:
        order2 = dict(order)
        order2.pop("posSide", None)
        result = okx_private_post("/api/v5/trade/order", order2)
        if str(result.get("code", "")) in {"0", ""}:
            order = order2
    if str(result.get("code", "")) not in {"0", ""}:
        d0 = (result.get("data") or [{}])[0]
        detail = d0.get("sMsg") or result.get("msg") or result.get("code")
        raise RuntimeError(f"OKX_CLOSE_ERR: {detail}")
    od = (result.get("data") or [{}])[0]
    return {
        "ok": True,
        "instId": inst_id,
        "ordId": od.get("ordId", ""),
        "closedQty": order["sz"],
        "positionSide": pos_side,
        "simulated": OKX_SIMULATED,
    }


class Handler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith("/api/okx/positions") or path.startswith("/api/binance/positions"):
            try:
                positions = fetch_okx_positions()
                positions.sort(key=lambda x: float(x.get("usdtValue", 0) or 0), reverse=True)
                json_resp(
                    self,
                    200,
                    {
                        "ok": True,
                        "positions": positions[:20],
                        "configured": bool(OKX_KEY and OKX_SECRET),
                        "source": "okx",
                        "timestamp": int(time.time()),
                    },
                )
            except Exception as e:
                json_resp(
                    self,
                    500,
                    {
                        "ok": False,
                        "configured": bool(OKX_KEY and OKX_SECRET),
                        "source": "okx",
                        "error": str(e),
                        "positions": [],
                    },
                )
            return

        if path == "/api/okx/ticker":
            try:
                inst_id = (query.get("instId") or [""])[0].strip().upper()
                if not inst_id:
                    raise RuntimeError("instId required")
                json_resp(self, 200, {"ok": True, "ticker": fetch_okx_ticker(inst_id)})
            except Exception as e:
                json_resp(self, 500, {"ok": False, "error": str(e)})
            return
        if path == "/api/okx/account":
            try:
                json_resp(self, 200, fetch_okx_account_overview())
            except Exception as e:
                json_resp(self, 500, {"ok": False, "error": str(e)})
            return
        if path == "/api/soso/sectors":
            try:
                data = fetch_soso_sector_board()
                json_resp(self, 200, {"ok": True, "source": "sosovalue", "items": data, "timestamp": int(time.time())})
            except Exception as e:
                json_resp(self, 500, {"ok": False, "error": str(e), "items": []})
            return
        if path == "/api/panews/calendar":
            date_str = (query.get("date") or [""])[0]
            period = (query.get("period") or ["week"])[0]
            cache_key = f"{period}:{date_str}"
            try:
                items = fetch_panews_calendar(date_str, period)
                now_ts = int(time.time())
                PANEWS_CACHE[cache_key] = {"items": items, "timestamp": now_ts}
                json_resp(self, 200, {"ok": True, "source": "panews", "items": items, "timestamp": now_ts, "stale": False})
            except Exception as e:
                cached = PANEWS_CACHE.get(cache_key)
                if not cached and PANEWS_CACHE:
                    cached = max(PANEWS_CACHE.values(), key=lambda x: int(x.get("timestamp", 0)))
                json_resp(
                    self,
                    200,
                    {
                        "ok": True,
                        "source": "panews-cache" if cached else "panews",
                        "items": (cached or {}).get("items", []),
                        "timestamp": int(time.time()),
                        "stale": True,
                        "error": str(e),
                    },
                )
            return

        if path in ["/", "/index.html"]:
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/api/okx/order":
            try:
                cl = int(self.headers.get("Content-Length", "0") or 0)
                raw = self.rfile.read(cl) if cl > 0 else b"{}"
                payload = json.loads(raw.decode("utf-8") or "{}")
                data = place_okx_order(payload if isinstance(payload, dict) else {})
                json_resp(self, 200, data)
            except Exception as e:
                json_resp(self, 500, {"ok": False, "error": str(e)})
            return
        if path == "/api/okx/close-position":
            try:
                cl = int(self.headers.get("Content-Length", "0") or 0)
                raw = self.rfile.read(cl) if cl > 0 else b"{}"
                payload = json.loads(raw.decode("utf-8") or "{}")
                data = place_okx_close_position(payload if isinstance(payload, dict) else {})
                json_resp(self, 200, data)
            except Exception as e:
                json_resp(self, 500, {"ok": False, "error": str(e)})
            return
        json_resp(self, 404, {"ok": False, "error": "not found"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "80"))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving on 0.0.0.0:{port}")
    server.serve_forever()
