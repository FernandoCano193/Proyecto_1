from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
import re
import redis 
import uuid
import os

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

sesiones={}

class WebRequestHandler(BaseHTTPRequestHandler):
    @cached_property
    def cookies(self):
        # Se obtienen los cookies
        return SimpleCookie(self.headers.get('Cookie'))
    
    def do_GET(self):
        method = self.get_method(self.path)
        if method:
            method_name, dict_params = method
            method = getattr(self, method_name)
            method(**dict_params)
            return
        else:
            self.send_error(404, "Not Found")

    # Funcion encargada de verificar si existe cookies
    def get_book_cookie(self):

        #Se obtienen las cookies
        cookies = self.cookies

        if cookies:
            print('cookie existente ' + cookies['sesion'].value)
        else:
            #Si no hay cookie se manda a llamar este metodo encargado
            #de generar nueva cookie
            self.create_cookie(cookies)

        #Retorno del valor de la cookie
        return cookies['sesion'].value

    
    def create_cookie(self, cookies):
        #Se crea la cookie con la libreria uuid
        cookies['sesion']=str(uuid.uuid4())
        cookies['sesion']['max-age']=10

        #Se hace el envio de la cookie al header
        self.send_header('Set-Cookie', cookies.output(header=''))


    #Funcion encargada de obtener las recomendaciones
    def get_book_recomendation(self, sesion, book_id):

        #Se almacena el book_id con la sesion como key
        r.rpush(sesion, book_id)

        #Se obtienen los libros visitados en dicha sesion
        books = r.lrange(sesion,0,-1)

        #Se obtienen los libros disponibles en redis y que fueron almacenados
        allBooks = r.keys('[0-9]')
        print(sesion, books)

        # Encontrar los libros no interactuados por el usuario
        new_books = [book for book in allBooks if book not in books]
        
        # Devolver una recomendación basada en el primer libro no interactuado
        if new_books:
            return new_books[0]
        else:
            # Si el usuario ha interactuado con todos los libros disponibles
            return '-'

   
   #Funcion encargada de obtner el html que se mostrara en el index
    def get_index(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open('html/index.html') as f:
            html = f.read()
        self.wfile.write(html.encode('utf-8'))


    #Funcion encargada de obtener el html del libro y obtener la sesion
    def get_book(self, book_id):
        book_html = r.get(book_id)

        if book_html:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            sesion = self.get_book_cookie()
            book_recomendation = self.get_book_recomendation(sesion, book_id)
            self.end_headers()
            html = f'''
            {book_html}
            <p>sesion: {sesion}</p>
            <p>Libro recomendado:<a href="/Book/{book_recomendation}">Libro {book_recomendation}</a></p>'''
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

    
    # Funcion encargada de obtener el metodo segun el path
    def get_method(self, path):
        for pattern, method in mapping:
            match = re.match(pattern, path)
            if match:
                return (method, match.groupdict())

mapping = [
            (r'^/Book/(?P<book_id>\d+)$', 'get_book'),
            (r'^/$', 'get_index'),
            (r'^/Book/-$', 'get_index')
        ]


if __name__ == "__main__":
    print("Server starting...")
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()
    
