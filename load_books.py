import os
import redis
import re

r = redis.Redis(host='localhost', port=6379, db=0)

def load_books(path):
    files = os.listdir(path)
    print(files)
    
    for i, file in enumerate(files, start =1):
        if file.endswith('.html'):
            with open(path+file) as f:
                html = f.read()
                r.set(i, html)

load_books('html/books/')
