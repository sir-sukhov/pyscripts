#!/usr/bin/python3
#
# MIT License
#
# Copyright (c) 2023 sir-sukhov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, socket

PORT = 8080
HOSTNAME = socket.gethostname()
class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if (self.path == '/ping'):
            self.send_response(200)
            self.end_headers()
        elif (self.path == '/status'):
            self.send_response(202)
            self.send_header("content-type", "application/json")
            self.end_headers()
            response={"status": "OK", "hostname": HOSTNAME}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        elif (self.path == "/headers"):
            self.send_response(202)
            self.send_header("content-type", "application/json")
            self.end_headers()
            headers=[{i[0]:i[1]} for i in self.headers.items()]
            response={"request_headers": headers}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_error(404)

with HTTPServer(('', PORT), RequestHandler) as httpd:
    httpd.serve_forever()
