from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
import psycopg2
import shutil
import zipfile
import tempfile
import os.path
import os

cursor = None
conn = None
#Path to main storage dir
STORAGE_PATH = None

def tmpprint(*args):
    return
tmpprint = print

def connect(dbname, user, password, host):
    global cursor, conn
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, 
                            password=password, host=host)
        cursor = conn.cursor()
    except psycopg2.OperationalError:
        print('no connection')
        return False
    return True



def ls(uid, dirpath):
    if not cursor: return None
    postgres_select_query = "SELECT _name, _type FROM file_db "\
                            "WHERE file_db._uid = %s AND file_db._path = %s "\
                            "ORDER BY _name"
    record_to_select = (uid, dirpath)
    cursor.execute(postgres_select_query, record_to_select)
    return dict(cursor)



def tree(uid):
    if not cursor: return None
    postgres_select_query = "SELECT _name, _type, _path FROM file_db "\
                            "WHERE file_db._uid = %s AND file_db._path like '/%%' "\
                            "ORDER BY _path"
    record_to_select = tuple([uid])
    cursor.execute(postgres_select_query, record_to_select)

    result_tree = { '/': {} }

    for (fname, ftype, fpath) in cursor.fetchall():
        fpath, tmp_dir = os.path.split(fpath)
        path_list = []
        while tmp_dir:
            path_list = [tmp_dir] + path_list
            fpath, tmp_dir = os.path.split(fpath)
        path_list = [fpath] + path_list

        result_sub_tree = result_tree
        for tmp_dir in path_list:
            result_sub_tree = result_sub_tree[tmp_dir]
        
        if ftype == 'd':
            result_sub_tree[fname] = {}
        else:
            result_sub_tree[fname] = 'file'
    return result_tree



def not_exists(uid, filename, ftype = None):
    if not cursor: return None
    fpath, fname = os.path.split(filename)
    postgres_select_query = "SELECT _uid FROM file_db "\
                            "WHERE file_db._uid = %s AND file_db._path = %s AND file_db._name = %s "
    if ftype:
        postgres_select_query += "AND file_db._type = %s"
        record_to_select = (uid, fpath, fname, ftype)
    else:
        record_to_select = (uid, fpath, fname)
    cursor.execute(postgres_select_query, record_to_select)
    tmpprint('not_exists:', uid, fpath, fname, ':', ftype)
    return not cursor.fetchone()



def object_info(uid, filename):
    if not cursor: return None
    fpath, fname = os.path.split(filename)
    postgres_select_query = "SELECT _uid, _path, _name, _type FROM file_db "\
                            "WHERE file_db._uid = %s AND file_db._path = %s AND file_db._name = %s "
    record_to_select = (uid, fpath, fname)
    cursor.execute(postgres_select_query, record_to_select)
    rec = cursor.fetchone()
    if not rec:
        return None
    return { 'uid': rec[0], 'path': rec[1], 'name': rec[2], 'type': rec[3] }



def uploaded(uid, filename): #(uid, fpath, fname)
    #filename = fpath + fname
    part_name = str(SHA256.new(bytes(str(uid) + filename, 'utf-8')).hexdigest())
    tmpprint('check uploaded:', uid, filename, ':')
    #tmpprint('  [vv]', os.path.exists(STORAGE_PATH + str(uid) + '/' + part_name))
    return os.path.exists(STORAGE_PATH + str(uid) + '/' + part_name)



def mkroot(uid):
    if not cursor: return None
    if os.path.exists(STORAGE_PATH + str(uid)):
        tmpprint('make root dir:', uid, ':')
        tmpprint('  already exists')
        return False
    os.mkdir(STORAGE_PATH + str(uid))
    postgres_insert_query = "INSERT INTO file_db (_uid, _name, _type, _path) VALUES (%s,%s,%s,%s)"
    record_to_insert = (uid, '/', 'd', '')
    cursor.execute(postgres_insert_query, record_to_insert)
    conn.commit()
    tmpprint('make root dir:', uid, ':')
    tmpprint('  created')
    return True

def rmroot(uid):
    if not cursor: return None
    if not os.path.exists(STORAGE_PATH + str(uid)):
        tmpprint('rm root dir:', uid, ':')
        tmpprint('  not exists')
        return False
    shutil.rmtree(STORAGE_PATH + str(uid), True)

    postgres_insert_query = "DELETE FROM file_db "\
                            "WHERE file_db._uid = %s "
    record_to_insert = tuple([uid])
    cursor.execute(postgres_insert_query, record_to_insert)
    conn.commit()

    tmpprint('rm root dir:', uid, ':')
    tmpprint('  success')
    return True



def mkdir(uid, dirpath):
    if not cursor: return None
    dpath, dname = os.path.split(dirpath)

    if dpath == '' or dname == '':
        return None
    if (dpath != '/'):
        parpath, parname = os.path.split(dpath)
        if not_exists(uid, dpath, 'd'):
            return False

    if (not_exists(uid, dirpath)):
        postgres_insert_query = "INSERT INTO file_db (_uid, _name, _type, _path) VALUES (%s,%s,%s,%s)"
        record_to_insert = (uid, dname, 'd', dpath)
        cursor.execute(postgres_insert_query, record_to_insert)
        conn.commit()
        return True
    return False
    pass



def upload(uid, key, filename, fdata): #(uid, key, fpath, fname)
    if not cursor: return None
    
    #filename = fpath + fname

    tmpprint('storing:', uid, filename, ':')

    iv = b'\xb7\xf8\xce\x15\x49\x24\x2b\xa1\xba\x9b\xc8\x67\x15\xc5\x37\x98'
    aes = AES.new(key, AES.MODE_EAX, iv)
    
    first_part_index = SHA256.new(bytes(str(uid) + filename, 'utf-8')).digest()
    part_name = first_part_index.hex()

    #already exists
    if (os.path.exists(STORAGE_PATH + str(uid) + '/' + part_name)):
        tmpprint(' ', filename, 'Already uploaded')
        return False

    size = len(fdata)
    part_count = int(pow(size//1024 + 1, 0.5))
    BYTES_IN_PART = size // part_count

    for i in range(0, part_count):
        #tmpprint('  [->]:', part_name)

        data, fdata = fdata[0:BYTES_IN_PART], fdata[BYTES_IN_PART:]
        part_file = open(STORAGE_PATH + str(uid) + '/' + part_name, 'wb')

        if (i < part_count - 1):
            part_index = get_random_bytes(32)
            part_name = part_index.hex()
            while (os.path.exists(STORAGE_PATH + str(uid) + '/' + part_name)):
                part_index = get_random_bytes(32)
                part_name = part_index.hex()
        else:
            part_index = first_part_index

        data += part_index
        data = aes.encrypt(data)

        part_file.write(data)
        part_file.close()

    postgres_insert_query = "INSERT INTO file_db (_uid, _name, _type, _path) VALUES (%s,%s,%s,%s)"
    fpath, fname = os.path.split(filename) 
    record_to_insert = (uid, fname, 'f', fpath)
    cursor.execute(postgres_insert_query, record_to_insert)
    conn.commit()
    return True



def download_file(uid, key, filename) -> bytes:
    tmpprint('downloading:', str(uid), filename, ':')

    iv = b'\xb7\xf8\xce\x15\x49\x24\x2b\xa1\xba\x9b\xc8\x67\x15\xc5\x37\x98'
    aes = AES.new(key, AES.MODE_EAX, iv)

    first_part_index = SHA256.new(bytes(str(uid) + filename, 'utf-8')).digest()
    part_name = first_part_index.hex()

    if (not os.path.exists(STORAGE_PATH + str(uid) + '/' + part_name)):
        tmpprint(' ', str(uid) + filename, 'No such file')
        return None

    fdata = b''

    while(True):
        #tmpprint('  [<-]:', part_name)

        try:
            part_file = open(STORAGE_PATH + str(uid) + '/' + part_name, 'rb')
        except:
            tmpprint('  Incorrect Key')
            return None

        data = part_file.read()
        part_file.close()
    
        data = aes.decrypt(data)
        data, part_index = data[:-32], data[-32:]

        fdata += data
        if (part_index == first_part_index):
            break

        part_name = part_index.hex()

    return fdata

def download_folder(uid, key, dirpath):
    if not cursor: return None
    postgres_select_query = "SELECT _path, _name, _type FROM file_db "\
                            "WHERE file_db._path like CONCAT(%s, \'%%\') AND file_db._uid = %s "\
                            "ORDER BY _path"
    record_to_select = (dirpath, uid)
    cursor.execute(postgres_select_query, record_to_select)
    
    temp_folder = os.path.join(STORAGE_PATH, '~' + str(uid))
    dirpath, dirname = os.path.split(dirpath)
    load_folder = os.path.join(temp_folder, dirname)
    tmpprint(load_folder)
    os.makedirs(load_folder, exist_ok=True)

    if dirpath == '/':
        dirpath = ''
    path_offset = len(dirpath) if dirpath != '/' else 0
    print('@@@@', dirpath)
    print('@@@+', path_offset)

    for fpath, fname, ftype in cursor.fetchall():
        if ftype == 'd':
            print('@@@@', dirpath)
            dr = os.path.join(fpath[path_offset:], fname)
            tmpprint('  foldering:', uid, dr)
            os.makedirs(temp_folder + dr, exist_ok=True)
        else:
            fdata = download(uid, key, fpath + '/' + fname)
            if fdata:
                dr = os.path.join(fpath[path_offset:], fname)
                tmpf = open(temp_folder + dr, 'wb')
                tmpf.write(fdata)
                tmpf.close()
    
    shutil.make_archive(load_folder, 'zip', temp_folder, dirname)
    zip_file = open(load_folder + '.zip', 'rb')
    zip_data = zip_file.read()
    zip_file.close()
    shutil.rmtree(temp_folder, True)


    return zip_data

def download(uid, key, filename) -> bytes:
    finfo = object_info(uid, filename)
    if not finfo: 
        return None

    if finfo['type'] == 'f':
        return download_file(uid, key, filename)
    else:
        return download_folder(uid, key, filename)



def remove_file(uid, key, filename):
    if not cursor: return None
    tmpprint('rmoving:', str(uid), filename, ':')

    iv = b'\xb7\xf8\xce\x15\x49\x24\x2b\xa1\xba\x9b\xc8\x67\x15\xc5\x37\x98'
    aes = AES.new(key, AES.MODE_EAX, iv)

    first_part_index = SHA256.new(bytes(str(uid) + filename, 'utf-8')).digest()
    part_name = first_part_index.hex()

    if (not os.path.exists(STORAGE_PATH + str(uid) + '/' + part_name)):
        tmpprint(' ', str(uid) + filename, 'No such file')
        return False
    #BLOCK_SIZE = os.path.getsize(STORAGE_PATH + str(uid) + '/' + part_name)

    while True:
        #tmpprint('  [XX]:', part_name)
        part_file = open(STORAGE_PATH + str(uid) + '/' + part_name, 'rb')
        data = part_file.read()
        part_file.close()
        os.remove(STORAGE_PATH + str(uid) + '/' + part_name)

        part_index = aes.decrypt(data)[-32:]
        if (part_index == first_part_index):
            break
        part_name = part_index.hex()

    postgres_insert_query = "DELETE FROM file_db "\
                            "WHERE file_db._uid = %s "\
                                "AND file_db._name = %s "\
                                "AND file_db._path = %s"
    fpath, fname = os.path.split(filename) 
    record_to_insert = (uid, fname, fpath)
    cursor.execute(postgres_insert_query, record_to_insert)
    conn.commit()
    return True

def remove_folder(uid, key, dirname):
    if not cursor: return None
    postgres_select_query = "SELECT _path, _name, _type FROM file_db "\
                            "WHERE file_db._uid = %s "\
                                "AND file_db._path like CONCAT(%s, \'%%\') "\
                            "ORDER BY _path"
    record_to_select = (uid, dirname)
    cursor.execute(postgres_select_query, record_to_select)

    for fpath, fname, ftype in cursor.fetchall():
        if (ftype == 'f'):
            remove_file(uid, key, fpath + '/' + fname)
        else: #remove directory
            tmpprint('rmoving:', uid, fpath + '/' + fname, ':d')
            postgres_delete_query = "DELETE FROM file_db "\
                                    "WHERE file_db._uid = %s "\
                                        "AND file_db._name = %s "\
                                        "AND file_db._path = %s "
            record_to_delete = (uid, fname, fpath)
            cursor.execute(postgres_delete_query, record_to_delete)
            conn.commit()

    postgres_delete_query = "DELETE FROM file_db "\
                            "WHERE file_db._uid = %s "\
                                "AND file_db._name = %s "\
                                "AND file_db._path = %s "
    fpath, fname = os.path.split(dirname)
    record_to_delete = (uid, fname, fpath)
    cursor.execute(postgres_delete_query, record_to_delete)
    conn.commit()
    return True

def remove(uid, key, filename) -> bytes:
    finfo = object_info(uid, filename)
    if not finfo: 
        tmpprint('remove(', uid, filename, '): no such object')
        return None

    if finfo['type'] == 'f':
        return remove_file(uid, key, filename)
    else:
        return remove_folder(uid, key, filename)