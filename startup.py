from urllib import request
import psycopg2
from db import get_cursor

myip = request.urlopen('https://api.ipify.org').read().decode()
myip = (myip,)


with get_cursor(commit=True) as cursor:
    query = """
            UPDATE kyhome
            SET ip = %s
            """
    cursor.execute(query, myip)
