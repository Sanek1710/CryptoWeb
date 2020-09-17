import CryptoWeb

#examples of uid and key
#uid must be  8 bytes len
#key must be 16 bytes len
uid1 = 0x1020304050607080
key1 = b'\xb7\xf8\xce\x15\x49\x24\x2b\xa1\xba\x9b\xc8\x67\x15\xc5\x37\x98'

uid2 = 0x49af1dacb4151b1c
key1 = b'\xba\x9b\xc8\x67\x15\xc5\x37\x98\xb7\xf8\xce\x15\x49\x24\x2b\xa1'


#Path to main storage dir
CryptoWeb.STORAGE_PATH = 'D:/WEB_STORAGE/'

def __main__():
    #connect to db server
    if not CryptoWeb.connect(dbname='cryptoweb_storage_db', user='postgres', 
                            password='12345', host='localhost'):
        return False

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

if __name__ == '__main__':
    __main__()
    

