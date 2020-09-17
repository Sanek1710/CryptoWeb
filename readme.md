# Base info
## Users
- all users has uid and key 
  - uid -  8 bytes user id
  - key - 16 bytes key

> CryptoWeb.STORAGE_PATH = 'F:/ull/path'
- path to file storage in file system

DATABASE SHOULD BE INSTALLED!

**run self_check to check something**

## Python libs
> pip install pycryptodomex
> pip install psycopg2
> pip install zipfile

# Create user
firstly you should create root folder
> CryptoWeb.mkroot(uid)

once you did it you can also create child folders for this user:
> CryptoWeb.mkdir(uid, '/dir1/dir2')
**All the dirs must begin with '/'**
- returns: true/false or None if there is some shit

list all the directories tree in json like format:
> CryptoWeb.tree(uid1)
- returns: {'/': {'f1.txt':'file', {'dir1':{}}}

check if this directory (or file) not exists:
> CryptoWeb.not_exists(uid, '/some/file' [, type])
- type = 'f' or 'd'
- returns: true/false

upload data as new file
> CryptoWeb.upload(uid, key, '/fpath/fname.ext', b'data')
- returns true/false

download data from file
> CryptoWeb.upload(uid, key, '/fpath/fname.ext')
- returns b'data'