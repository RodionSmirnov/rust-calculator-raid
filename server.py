"""Run with python3 server.py --port 3000."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from calculator import TARGETS, WEAPONS, calculate

ROOT = Path(__file__).resolve().parent
STATIC = {'/': ('index.html', 'text/html'), '/index.html': ('index.html', 'text/html'),
          '/style.css': ('style.css', 'text/css'), '/app.js': ('app.js', 'text/javascript')}


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, mime='application/json'):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/catalog':
            self.send(200, dict(targets=TARGETS, weapons=WEAPONS))
        elif path in STATIC:
            filename, mime = STATIC[path]
            self.send(200, (ROOT / filename).read_bytes(), mime)
        else:
            self.send(404, {'error': 'Не найдено'})

    def do_POST(self):
        if urlsplit(self.path).path != '/api/calculate':
            self.send(404, {'error': 'Не найдено'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 100000:
                self.send(413, {'error': 'Неверный размер запроса'})
                return
            payload = json.loads(self.rfile.read(length))
            self.send(200, calculate(payload))
        except (ValueError, TypeError, KeyError) as error:
            self.send(400, {'error': str(error)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=3000)
    parser.add_argument('--host', default='0.0.0.0')
    args = parser.parse_args()
    print(f'Rust raid calculator: port {args.port}', flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
