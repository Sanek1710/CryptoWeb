import Cryptodome
import CryptoWeb
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
import psycopg2
import zipfile
import os.path
import os

if not CryptoWeb.connect(dbname='cryptoweb_storage_db', user='postgres', 
                            password='12345', host='localhost'):
    print('[-] ERROR: no db')

cursor = CryptoWeb.conn.cursor()
postgres_select_query = "SELECT _uid, _id, _name, _type, _path FROM file_db "
cursor.execute(postgres_select_query)
res = cursor.fetchall()
print(res)


