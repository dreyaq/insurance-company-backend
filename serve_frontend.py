from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

PORT = 3000

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    # Изменяем текущую директорию на директорию frontend
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend'))
    
    handler = CORSRequestHandler
    httpd = HTTPServer(("", PORT), handler)
    
    print(f"Serving frontend at http://localhost:{PORT}")
    httpd.serve_forever()
