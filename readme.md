# CryptoWeb module
## Python libs
```sh
pip install pycryptodomex
pip install psycopg2
pip install zipfile
```
## Users
All users has uid and key 
- uid -  8 bytes user id
- key - 16 bytes key

Set path to file storage in file system
```python
CryptoWeb.STORAGE_PATH = 'F:/ull/path'
```
***DATABASE SHOULD BE INSTALLED!***
*run self_check to check something*

# Discription
## Connect to the database
```python
CryptoWeb.connect(dbname='cryptoweb_storage_db', user='postgres', 
                            password='12345', host='localhost')
```
## make uid and key example:
```python
uid2 = 0x49af1dacb4151b1c #8 bytes
key2 = b'\xb7\xf8\xce\x15\x49\x24\x2b\xa1\xba\x9b\xc8\x67\x15\xc5\x37\x98' #16 bytes
```
## create root folder
```python
CryptoWeb.mkroot(uid)
```
## remove root folder:
```python
CryptoWeb.rmroot(uid)
```
## create child folders for this user:
```python
CryptoWeb.mkdir(uid, '/dir1/dir2')
```
*All the dirs must begin with '/'*
**returns**: true/false or None if there is some shit

## list all the directories tree in json like format:
```python
CryptoWeb.tree(uid)
```
**returns**: something like:
```python
        { '/': { 'f1.txt': 'file', { 'dir1': { } } } 
```

## list all files/folders of concrete folder in json like format:
```python
CryptoWeb.ls(uid, '/path/to/dir')
```
**returns**: something like:
 ```python
        { 'f1.txt': 'f', 'dir1': 'd' } 
```

## check if this file/folder not exists:
```python
CryptoWeb.not_exists(uid, '/some/file' [, type])
```
**type**: 'f' or 'd'
**returns**: true/false

## get file/folder information:
```python
CryptoWeb.object_info(uid, '/path/to/obj')
```
**returns**: None if not exists, or something like this:
```py
        { 'uid': uid, 'path': '/path/to', 'name': 'obj', 'type': 'f' }
```

## upload data as new file
```python
CryptoWeb.upload(uid, key, '/fpath/fname.ext', b'data')
```
**returns**: true/false

## download data from file/folder
```python
CryptoWeb.download(uid, key, '/fpath/fname.ext')
CryptoWeb.download(uid, key, '/fpath/dirname')
```
**returns**: b'data'
*if directory downloading was tried it returns zip archieve data as bytes*

## remove file/folder
```python
CryptoWeb.remove(uid, key, '/fpath/fname.ext')
CryptoWeb.remove(uid, key, '/fpath/dirname')
```
**returns**: true/false
  *if directory removing was tried then removes all the files it contains*

