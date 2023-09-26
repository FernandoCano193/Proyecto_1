import os
import redis
import re
from bs4 import BeautifulSoup

r = redis.Redis(host='localhost', port=6379, db=0)

def load_books(path):
    files = os.listdir(path)
    print(files)
    
    for id, file in enumerate(files, start =1):
        if file.endswith('.html'):
            with open(path+file) as f:
                html = f.read()
                r.set(id, html)
                create_index(id, html)

def create_index(book_id, html):
    soup = BeautifulSoup(html, 'html.parser')
    content_book = soup.get_text().split(' ')

    for term in content_book:
        r.sadd(term, book_id)

load_books('html/books/')
