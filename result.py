from http.server import BaseHTTPRequestHandler
import json, urllib.request, urllib.error

UPSTREAM_URL = "https://rbse.rankguruji.com/api/result"

FAKE_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept":          "application/json, text/plain, */*",
    "Content-Type":    "application/json",
    "Origin":          "https://rankguruji.com",
    "Referer":         "https://rankguruji.com/",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
}

CORS = [
    ("Access-Control-Allow-Origin",  "*"),
    ("Access-Control-Allow-Methods", "POST, OPTIONS"),
    ("Access-Control-Allow-Headers", "Content-Type"),
    ("Content-Type",                 "application/json"),
]

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in CORS: self.send_header(k, v)
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length) or b"{}")
            roll_no = body.get("roll_no")
            if not roll_no:
                return self._out(400, {"error": "roll_no missing"})

            payload = json.dumps({
                "board":   body.get("board", "rj"),
                "year":    body.get("year",  "2026"),
                "std":     str(body.get("std", "10")).strip(),
                "roll_no": int(roll_no),
            }).encode()

            req = urllib.request.Request(UPSTREAM_URL, data=payload, headers=FAKE_HEADERS, method="POST")
            with urllib.request.urlopen(req, timeout=15) as r:
                self._out(200, r.read(), raw=True)

        except urllib.error.HTTPError as e:
            self._out(502, {"error": f"Upstream {e.code}"})
        except Exception as e:
            self._out(500, {"error": str(e)})

    def _out(self, code, body, raw=False):
        self.send_response(code)
        for k, v in CORS: self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body if raw else json.dumps(body).encode())

    def log_message(self, *a): pass
