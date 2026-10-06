import hmac
import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .core import Platform


def main():
    key = os.environ.get('AEGIS_API_KEY', '')
    if len(key) < 24:
        raise SystemExit('Set AEGIS_API_KEY to at least 24 characters')
    platform = Platform(os.getenv('DATABASE_PATH', '/data/aegis.db'), os.getenv('BACKEND', 'mock'),
                        os.getenv('OLLAMA_URL', 'http://ollama:11434'), int(os.getenv('RATE_LIMIT_RPM', '60')))

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, status, body, content_type='application/json'):
            raw = body.encode() if isinstance(body, str) else json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('X-Request-ID', self.request_id)
            self.end_headers()
            self.wfile.write(raw)
            print(json.dumps({'request_id': self.request_id, 'path': self.path, 'status': status}), flush=True)

        def handle_request(self):
            self.request_id = uuid.uuid4().hex
            if self.command == 'GET' and self.path in ('/health/live', '/health/ready'):
                return self.send(200, {'status': 'ok', 'scope': 'gateway and sqlite; model availability checked per request'})
            if not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer '+key):
                return self.send(401, {'error': 'unauthorized'})
            try:
                platform.admit()
                if self.command == 'GET':
                    if self.path == '/v1/models':
                        return self.send(200, {'data': [{'id': 'demo'}, {'id': 'local', 'enabled': platform.backend == 'ollama'}]})
                    if self.path == '/metrics':
                        return self.send(200, f'aegis_completions_total {platform.calls}\naegis_errors_total {platform.errors}\naegis_estimated_tokens_total {platform.tokens}\n', 'text/plain')
                if self.command == 'POST':
                    length = int(self.headers.get('Content-Length', '0'))
                    if not 0 < length <= 120000:
                        return self.send(413, {'error': 'invalid_body_size'})
                    data = json.loads(self.rfile.read(length))
                    if not isinstance(data, dict):
                        raise ValueError('invalid_body')
                    if self.path == '/v1/chat/completions':
                        if data.get('stream'):
                            raise ValueError('streaming_not_supported')
                        result = platform.chat(data.get('messages'), data.get('model', 'demo'), data.get('rag', False), data.get('max_tokens', 256))
                        result.update(id='chatcmpl-'+uuid.uuid4().hex, created=int(time.time()))
                        return self.send(200, result)
                    if self.path == '/v1/documents':
                        return self.send(201, {'chunks': platform.ingest(data.get('source'), data.get('text'))})
                    if self.path == '/v1/evaluations':
                        return self.send(200, platform.evaluate())
                return self.send(404, {'error': 'not_found'})
            except (ValueError, TypeError) as exc:
                platform.errors += 1
                return self.send(429 if str(exc) == 'rate_limit' else 400, {'error': str(exc)})
            except Exception:
                platform.errors += 1
                return self.send(502, {'error': 'backend_failure'})

        do_GET = handle_request
        do_POST = handle_request

    ThreadingHTTPServer(('0.0.0.0', int(os.getenv('PORT', '8080'))), Handler).serve_forever()


if __name__ == '__main__':
    main()
