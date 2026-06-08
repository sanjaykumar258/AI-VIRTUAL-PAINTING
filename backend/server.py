import json
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os

class StateHandler(BaseHTTPRequestHandler):
    state = None # Set by run_server

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            try:
                while True:
                    frame = self.state.get('frame_bytes')
                    if frame is not None:
                        self.wfile.write(b'--frame\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                    time.sleep(0.033) # roughly 30fps target
            except Exception:
                pass
            return
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {
                'colorIndex': self.state.get('colorIndex', 0),
                'brushSize': self.state.get('brushSize', 5),
                'mode': self.state.get('mode', 'Hover'),
                'fps': self.state.get('fps', 0)
            }
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        # Serve static files from frontend/
        try:
            frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
            path = os.path.normpath(self.path.lstrip('/'))
            file_path = os.path.join(frontend_dir, path)
            
            # Basic security check
            if not file_path.startswith(frontend_dir):
                self.send_error(403)
                return
                
            if os.path.exists(file_path) and not os.path.isdir(file_path):
                self.send_response(200)
                # Apply cache busting headers for development/immediate reload
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                
                if path.endswith('.html'):
                    self.send_header('Content-Type', 'text/html')
                elif path.endswith('.css'):
                    self.send_header('Content-Type', 'text/css')
                elif path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404)
                return
        except Exception:
            self.send_error(500)
            return

    def do_POST(self):
        if self.path == '/api/command':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    cmd = json.loads(post_data.decode('utf-8'))
                    self.state.setdefault('commands', []).append(cmd)
                except json.JSONDecodeError:
                    pass
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))

    def log_message(self, format, *args):
        pass # Suppress HTTP access logging in console

def run_server(state, port=5000):
    StateHandler.state = state
    server = ThreadingHTTPServer(('0.0.0.0', port), StateHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
