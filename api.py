import requests, os, rsa, ast, hashlib
from cryptography.fernet import Fernet

domain = 'http://127.0.0.1:5000'
#domain = 'http://10.0.0.41:5000'

publickey, privatekey = rsa.newkeys(2048)

recall_count = 0    # Count how many times a function has recalled to fix an issue

#print('\nPublic Key and String Public Key')
#print(publickey)
#print(str(publickey))

def decode(val):
    '''
        In order to get back to the unencrypted input, I must
        convert the string back into a list of integers,
        then convert the list back into bytes, then decrypt the
        bytes using the private key, then decode the decrypted
        value from utf-8 into a string.
    '''
    global privatekey
    array = ast.literal_eval(val)   # Convert string to list
    encrypted = bytes(array)    # Convert list of ints to bytes
    return rsa.decrypt(encrypted,privatekey).decode('utf-8')

def encode(val,key):
    '''
        Sending encrypted bytes through JSON caused the bytes
        to convert into string, which ruined the formatting and
        prevented the data from being decrypted. To get around
        this issue, I turn the encrypted bytes into an array
        of integers, which I then turn into a string, and then
        I can send the string.
    '''
    return str(list(rsa.encrypt(val.encode('utf-8'),key)))

def login(username = '',password = ''):
    global publickey, privatekey
    data = {
        'username':username,
        'password':password,
        'publickey':publickey.__getstate__()
    }
    accepted = api_request('/login',data = data)
    if accepted is None:
        print('Failed to receive valid response')
    #print(accepted)
    return decode(accepted['response'])

def logout(username = ''):
    print('Called Logout Function')
    data = {
        'username':username
    }
    accepted = api_request('/logout',data = data)
    if accepted is None:
        print('Failed to receive valid response')
    return accepted['response']

def new_user(username = None, password = None):
    data = {
        'username':username,
        'password':password,
        'publickey':publickey.__getstate__()
    }
    accepted = api_request('/new-user',data = data)
    if accepted is None:
        print('Failed to receive valid response')
    return decode(accepted['response'])

def api_request(endpoint,data=None,files=None):
    global server_publickey
    print(endpoint)

    if not data is None:
        for key in data.keys():
            if type(data[key]) is tuple:
                print('Key datatype')
                #print(data[key])
                data[key] = str(data[key])
                continue
            if key == 'file':
                continue
            data[key] = encode(data[key],server_publickey)
    timeout = 5
    if not files is None:
        timeout = 30
    r = None
    try:
        r = requests.post(domain + endpoint,data=data,files=files,timeout=timeout)
    except Exception as e:
        print('Failed to connect to server')
        print(e)
    try:
        return r.json()
    except:
        print("Returning JSON failed")
        #print(r.text)
        return r

def upload_file(username = None, directory = None, fname = None):
    global recall_count
    data = {'username':username, 'file_name':fname}
    hash = hashlib.md5(open(directory + '/' + fname,'rb').read()).hexdigest()
    sym_key = Fernet.generate_key()
    fernet = Fernet(sym_key)
    fdata = fernet.encrypt(open(directory + '/' + fname,'rb').read())
    data['sym_key'] = str(list(sym_key))
    f = open('./temp.txt','wb')
    f.write(fdata)
    f.close()
    accepted = api_request('/store-file', data = data, files = {'file':open('./temp.txt','rb')})
    if accepted is None:
        print('Failed to receive valid response')
    print(f'Local MD5: {hash}')
    remote_hash = decode(accepted['hash'])
    print(f'Remote MD5: {remote_hash}')
    if not hash == remote_hash and recall_count < 3:
        print('Failed hash check')
        print(hash)
        print(remote_hash)
        recall_count += 1
        return upload_file(username,directory,fname)
    recall_count = 0
    return decode(accepted['response'])

def remove_file(username = None, fname = None):
    data = {'username':username, 'file_name': fname}
    accepted = api_request('/remove-file',data=data)
    if accepted is None:
        print('Failed to receive valid response')
    return decode(accepted['response'])

def download_file(username = None, fname = None):
    global recall_count
    data = {'username':username,'file_name':fname}
    accepted = api_request('/retrieve-file',data=data)
    if accepted is None:
        print('Failed to receive valid response')
    sym_key = bytes(ast.literal_eval(decode(accepted['key'])))
    fernet = Fernet(sym_key)
    hash = decode(accepted['hash'])
    fdata = fernet.decrypt(bytes(ast.literal_eval(accepted['file'])))

    f = open(fname,'wb')
    f.write(fdata)
    f.close()
    local_hash = hashlib.md5(open('./' + fname,'rb').read()).hexdigest()

    if not local_hash == hash and recall_count < 3:
        print('Failed hash check')
        print(local_hash)
        print(hash)
        recall_count += 1
        return download_file(username, fname)
    recall_count = 0
    print(f'Local MD5: {local_hash}')
    print(f'Remote MD5: {hash}')

def list_stored_files(username = None):
    data = {'username':username}
    accepted = api_request('/list-stored-files',data=data)
    if accepted is None:
        print('Failed to receive a valid response')
    resp = decode(accepted['response'])
    if resp == 'Invalid User':
        print('Invalid User')
        return None
    return ast.literal_eval(resp)

def retrieve_server_key():
    accepted = api_request('/retrieve-public-key')
    if accepted is None:
        print('Failed to retrieve server key')
    #print('Retrieve Server Key')
    #print(type(accepted))
    key = rsa.PublicKey(accepted['n'],accepted['e'])
    return key

server_publickey = retrieve_server_key()
#print(f'Server Public Key:\n{server_publickey}')