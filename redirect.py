#!/usr/bin/env python3
"""Simple HTTP-to-HTTPS redirect server"""
import http.server

class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)
        host = self.headers.get("Host", "localhost")
        self.send_header("Location", f"https://{host}{self.path}")
        self.end_headers()
    do_POST = do_GET

http.server.HTTPServer(("0.0.0.0", 8080), RedirectHandler).serve_forever()
