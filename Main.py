import CryptoWeb
import os
import shutil


#examples of uid and key
#uid must be  8 bytes len
#key must be 16 bytes len
uid1 = 0x1020304050607080
key1 = b'\xba\x9b\xc8\x67\x15\xc5\x37\x98\xb7\xf8\xce\x15\x49\x24\x2b\xa1'

uid2 = 0x49af1dacb4151b1c
key2 = b'\xb7\xf8\xce\x15\x49\x24\x2b\xa1\xba\x9b\xc8\x67\x15\xc5\x37\x98'


#Path to main storage dir
CryptoWeb.STORAGE_PATH = 'D:\\WEB_STORAGE\\'


#/
#|--d1
#|  |--1.txt
#|  |--d1_1
#|      |--1.txt
#|      |--1.jpg
#|--d2
#|  |--1.txt
#|  |--1.jpg
#|--1.txt
#|--1.jpg
def create_db():
    CryptoWeb.mkroot(uid2)
    CryptoWeb.mkdir(uid2, '/d1')
    data_1_txt = open('1.txt', 'rb').read()
    data_1_jpg = open('1.jpg', 'rb').read()
    CryptoWeb.upload(uid2, key2, '/d1/1.txt', data_1_txt)
    CryptoWeb.mkdir(uid2, '/d1/d1_1')
    CryptoWeb.upload(uid2, key2, '/d1/d1_1/1.txt', data_1_txt)
    CryptoWeb.upload(uid2, key2, '/d1/d1_1/1.jpg', data_1_jpg)
    CryptoWeb.mkdir(uid2, '/d2')
    CryptoWeb.upload(uid2, key2, '/d2/1.txt', data_1_txt)
    CryptoWeb.upload(uid2, key2, '/d2/1.jpg', data_1_jpg)
    CryptoWeb.upload(uid2, key2, '/1.txt', data_1_txt)
    CryptoWeb.upload(uid2, key2, '/1.jpg', data_1_jpg)
    print(CryptoWeb.tree(uid2))

def clear_db():
    postgres_delete_query = "DELETE FROM file_db"
    CryptoWeb.cursor.execute(postgres_delete_query)
    CryptoWeb.conn.commit()
    shutil.rmtree(CryptoWeb.STORAGE_PATH, True)
    os.makedirs(CryptoWeb.STORAGE_PATH, exist_ok=True)


def __main__():
    #connect to db server
    if not CryptoWeb.connect(dbname='cryptoweb_storage_db', user='postgres', 
                            password='12345', host='localhost'):
        return False
    clear_db()
    create_db()
    data = CryptoWeb.download(uid2, key2, '/d1/d1_1')
    open('d1_1.zip', 'wb').write(data)




"""
    #create root dir for user uid1
    CryptoWeb.mkroot(uid1)

    #list tree for user uid1
    res = CryptoWeb.tree(uid1)
    print(res)

    #check if file /1.jpg 
    res = CryptoWeb.not_exists(uid1, '/1.jpg')
    print(res)

    #create directory /dir1 for uid1
    res = CryptoWeb.mkdir(uid1, '/dir1/dir2')
    print(res) #error as /dir1 wasn't created firstly

    #retry create directory /dir1 for uid1
    res = CryptoWeb.mkdir(uid1, '/dir1')
    print(res)
    #create directory /dir1/dir2
    res = CryptoWeb.mkdir(uid1, '/dir1/dir2')
    print(res) #now okay


    CryptoWeb.upload(uid1, key1, '/dir1/dir2/1.txt', b'Hello world')
    
    #upload real file
    data = open('1.jpg', 'rb').read()
    CryptoWeb.upload(uid1, key1, '/dir1/1.jpg', data)

    #upload file: res - file data
    res = CryptoWeb.download(uid1, key1, '/1.txt')
    print(res)

    res = CryptoWeb.download(uid1, key1, '/dir1/1.txt')
    print(res)

    #upload file: res - file data writes to file
    res = CryptoWeb.download(uid1, key1, '/dir1/1.jpg')
    open('2.jpg', 'wb').write(res)

    #show tree now 
    res = CryptoWeb.tree(uid1)
    print(res)

    #removing file 
    #CryptoWeb.remove(uid1, key1, '/dir1/1.jpg')
    res = CryptoWeb.tree(uid1)
    print(res)
"""

if __name__ == '__main__':
    __main__()
    

