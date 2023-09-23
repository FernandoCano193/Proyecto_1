from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
import re
import redis 
import uuid
import os

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


class WebRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        method = self.get_method(self.path)
        if method:
            method_name, dict_params = method
            method = getattr(self, method_name)
            method(**dict_params)
            return
        else:
            self.send_error(404, "Not Found")

    def get_book_cookie(self):
        cookies = SimpleCookie()

        cookies["sesion"] = str(uuid.uuid4())

        print("Cookie generada " + cookies["sesion"].value)
        return cookies['sesion'].value


   
    def get_index(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open('html/index.html') as f:
            html = f.read()
        self.wfile.write(html.encode('utf-8'))


    def get_book(self, book_id):
        book_html = r.get(book_id)

        if book_html:
            self.get_book_cookie()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(book_html.encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

    def get_method(self, path):
        for pattern, method in mapping:
            match = re.match(pattern, path)
            if match:
                return (method, match.groupdict())

mapping = [
            (r'^/Book/(?P<book_id>\d+)$', 'get_book'),
            (r'^/$', 'get_index')
        ]


if __name__ == "__main__":
    print("Server starting...")
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()
    
