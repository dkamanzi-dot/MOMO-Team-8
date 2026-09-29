# REST API for MoMo SMS transactions using only http.server
# Run: python api/server.py
import base64
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dsa"))
from parse_xml import JSON_FILE, XML_FILE, parse, save  # noqa: E402


def load_env():
    # read key=value lines from .env so passwords are not in the code
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)


load_env()
USERNAME = os.environ.get("API_USERNAME")
PASSWORD = os.environ.get("API_PASSWORD")
PORT = int(os.environ.get("API_PORT", 8000))

REQUIRED = ["type", "amount", "sender", "receiver", "timestamp"]


def load_data():
    if not os.path.exists(JSON_FILE):
        save(parse(XML_FILE))
    with open(JSON_FILE, encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)}


transactions = load_data()


def persist():
    save(list(transactions.values()))


class Handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if status == 401:
            self.send_header("WWW-Authenticate", 'Basic realm="MoMo API"')
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            user, pwd = base64.b64decode(header[6:]).decode().split(":", 1)
        except Exception:
            return False
        return user == USERNAME and pwd == PASSWORD

    def get_id(self):
        # returns (matched, id) for /transactions/{id}
        parts = self.path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "transactions":
            return True, int(parts[1]) if parts[1].isdigit() else None
        return False, None

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None

    def check(self):
        if not self.authorized():
            self.send_json(401, {"error": "Unauthorized"})
            return False
        return True

    def do_GET(self):
        if not self.check():
            return
        if self.path.rstrip("/") == "/transactions":
            return self.send_json(200, list(transactions.values()))
        matched, tx_id = self.get_id()
        if not matched:
            return self.send_json(404, {"error": "Not found"})
        if tx_id not in transactions:
            return self.send_json(404, {"error": "Transaction not found"})
        self.send_json(200, transactions[tx_id])

    def do_POST(self):
        if not self.check():
            return
        if self.path.rstrip("/") != "/transactions":
            return self.send_json(404, {"error": "Not found"})
        data = self.read_body()
        if data is None:
            return self.send_json(400, {"error": "Invalid JSON"})
        missing = [f for f in REQUIRED if f not in data]
        if missing:
            return self.send_json(400, {"error": f"Missing fields: {missing}"})
        new_id = max(transactions, default=0) + 1
        data["id"] = new_id
        transactions[new_id] = data
        persist()
        self.send_json(201, data)

    def do_PUT(self):
        if not self.check():
            return
        matched, tx_id = self.get_id()
        if not matched:
            return self.send_json(404, {"error": "Not found"})
        if tx_id not in transactions:
            return self.send_json(404, {"error": "Transaction not found"})
        data = self.read_body()
        if data is None:
            return self.send_json(400, {"error": "Invalid JSON"})
        data.pop("id", None)
        transactions[tx_id].update(data)
        persist()
        self.send_json(200, transactions[tx_id])

    def do_DELETE(self):
        if not self.check():
            return
        matched, tx_id = self.get_id()
        if not matched:
            return self.send_json(404, {"error": "Not found"})
        if tx_id not in transactions:
            return self.send_json(404, {"error": "Transaction not found"})
        deleted = transactions.pop(tx_id)
        persist()
        self.send_json(200, {"message": "Deleted", "transaction": deleted})


if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        sys.exit("Set API_USERNAME and API_PASSWORD in .env first")
    print(f"Loaded {len(transactions)} transactions")
    print(f"Running on http://localhost:{PORT}")
    HTTPServer(("", PORT), Handler).serve_forever()
