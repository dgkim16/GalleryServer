import http.server
import socketserver
import json
import os
from datetime import datetime
# import socket
import threading

# HOST = socket.gethostbyname(socket.gethostname())
HOST = ""
PORT = 8080
SHUTDOWN_TOKEN = "secret123"  # Optional token for safety
PAGES_JSON = "pages.json"
TARGET_DIR = "Root Gallery"

def load_pages():
    """Load existing pages.json content or create a fresh structure."""
    if os.path.exists(PAGES_JSON):
        with open(PAGES_JSON, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                pass
    return {"root": TARGET_DIR, "pages": []}

def save_pages(data):
    with open(PAGES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def sync_folders_with_json():
    data = load_pages()
    known = {entry["page"] for entry in data["pages"]}
    today = datetime.now().strftime("%Y-%m-%d")

    for name in sorted(os.listdir(TARGET_DIR)):
        path = os.path.join(TARGET_DIR, name)
        if os.path.isdir(path) and name not in known:
            data["pages"].append({
                "page": name,
                "meta": {
                    "title": name,
                    "date": today,
                    "views": 0,
                    "starred": False
                }
            })
            print(f"📁 Added new folder to pages.json: {name}")

    save_pages(data)
    return data

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        if "code 404" in format % args and any(ext in self.path for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]):
            return  # Silence thumbnail 404 logs
        super().log_message(format, *args)
        
    def do_GET(self):
        if self.path == "/pages.json":
            data = sync_folders_with_json()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        elif self.path.startswith("/shutdown"):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            token = query.get("token", [None])[0]

            if token == SHUTDOWN_TOKEN:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Server shutting down...")
                print("Shutdown signal received. Server shutting down.")
                threading.Thread(target=httpd.shutdown).start()
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden")
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length))
        path = self.path

        if path == "/update-starred":
            self.handle_star_update(body)
        elif path == "/update-views":
            self.handle_view_update(body)
        else:
            self.send_error(404, "Not Found")

    def handle_star_update(self, body):
        page = body.get("page")
        new_value = body.get("starred")

        data = load_pages()
        for entry in data["pages"]:
            if entry["page"] == page:
                entry["meta"]["starred"] = new_value
                break
        save_pages(data)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def handle_view_update(self, body):
        page = body.get("page")

        data = load_pages()
        for entry in data["pages"]:
            if entry["page"] == page:
                entry["meta"]["views"] = entry["meta"].get("views", 0) + 1
                break
        save_pages(data)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

if __name__ == "__main__":
    print(f"🌐 Starting server at http://localhost:{PORT}")
    sync_folders_with_json()
    with socketserver.TCPServer((HOST, PORT), CustomHandler) as httpd:
        httpd.serve_forever()