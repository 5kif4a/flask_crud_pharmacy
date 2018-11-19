import os

url = 'postgresql://{}:{}@{}:{}/{}'
user = 'postgres'
password = 'beat7boX'
host = 'localhost'
port = 5432
database = 'postgres'

URL = url.format(user, password, host, port, database)
KEY = os.urandom(32)
