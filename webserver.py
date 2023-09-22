from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
import re
import redis 

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class WebRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        
        self.url = urlparse(self.path)

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body>')
            self.wfile.write(b'<h1>Lista de Libros</h1>')
            keys = r.keys('libro*')
            print(keys)
            
            self.wfile.write(b'<ul>')
            for book in keys:
                datos = r.hgetall(book)
                print(datos)
                titulo = datos.get('titulo')
                print(titulo)
##                self.wfile.write(f'<li>{titulo}</li>')
            self.wfile.write(b'</ul>')

        book_id = re.findall(r'^/Book/(\d+)',self.url.path)


        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(self.get_response(book_id).encode("utf-8"))

    def get_response(self, book_id):
            if book_id:
                if book_id[0] in books:
                    return f"""
                    <h1> Hola Web </h1>
                    <p>  {books[book_id[0]]}   </p>
                    """
            return f"""
        <h1> Hola Web </h1>
        <p>  {self.path}   </p>
    """

books = {'1':'Harry',
         '2':'Potter'}


if __name__ == "__main__":
    print("Server starting...")
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()
