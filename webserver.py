from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
import re
import redis 

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class WebRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.url = urlparse(self.path)

        if self.url.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode('utf-8'))

    def get_html(self):
        libros=r.keys('libro*')
        print(libros)
        html = """<!DOCTYPE html>
    <html lang="es-mx">
    <head>
        <meta charset="UTF-8">
        <title>Lista de Libros</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>Lista de Libros</h1>
        <ul>
        """
        for libro_id in libros:
                libro = r.hgetall(libro_id)
                html += f"<li><strong>Título:</strong> {libro.get('titulo')}<br>"
                html += f"<strong>Autor:</strong> {libro.get('autor')}<br>"
                html += """
        </ul>
    </body>
    </html>
    """
        return html

books = {'1':'Harry',
         '2':'Potter'}


if __name__ == "__main__":
    print("Server starting...")
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()
