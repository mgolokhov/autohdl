import base64
import os
import socket
import sys
import getpass

import tinydav
from tinydav.exception import HTTPUserError
import yaml
from autohdl.hdlLogger import logging


log = logging.getLogger(__name__)

def loadAuth(iPath):
    username, password = '', ''
    try:
        with open(iPath) as f:
            content = yaml.load(f)
            username = base64.decodebytes(content[base64.encodebytes('username')])
            password = base64.decodebytes(content[base64.encodebytes('password')])
    except Exception as e:
        # logging e
        logging.debug(e)
    return username, password


def checkAuth(host, iUsername, iPassword):
    client = tinydav.HTTPClient(host)
    print("OH "*100)
    print(iUsername, iPassword)
    print(type(iUsername), type(iPassword))
    input('next')
    client.setbasicauth(iUsername.encode('utf-8'), iPassword.encode('utf-8'))
    try:
        print(client.head('/test'))
    except HTTPUserError as e:
        #logging
        print(e)
        logging.debug(e)
        return False
    return True


def dumpAuth(iPath, iUsername, iPassword):
    contentYaml = {base64.decodebytes('username'): base64.encodebytes(iUsername),
                   base64.decodebytes('password'): base64.encodebytes(iPassword)}
    try:
        with open(iPath, 'wb') as f:
            yaml.dump(contentYaml, f, default_flow_style=False)
    except IOError as e:
        print(e)


def askAuth():
    quit = input('To cancel hit Q, Enter to continue: ')
    if quit.lower() == 'q':
        print('Exit...')
        sys.exit(0)
    username = input('user: ')
    password = getpass.getpass('password: ')
    return username, password


def dump_netrc(host, username, password):
    path = os.environ['USERPROFILE'] + '/_netrc'
    addNew = False
    try:
        with open(path, 'r') as f:
            context = f.read()
            for i in [host, username, password]:
                if i not in context:
                    addNew = True
    except IOError as e:
        log.debug(e)
        addNew = True
    if addNew:
        data = 'machine {0}\nlogin {1}\npassword {2}\n'.format(host, username, password)
        with open(path, 'w') as f:
            f.write(data)


def authenticate(host='cs.scircus.ru'):
    print('Authentication', end=' ')
    path = sys.prefix + '/Lib/site-packages/autohdl_cfg/open_sesame'
    username, password = loadAuth(path)
    state = 'check'
    while True:
        if state == 'check':
            if checkAuth(host, username, password):
                state = 'dump'
            else:
                state = 'ask'
        elif state == 'ask':
            username, password = askAuth()
            state = 'check'
        elif state == 'dump':
            dumpAuth(path, username, password)
            dump_netrc(host, username, password)
            return username, password


def exists(path, client):
    try:
        client.get(path)
    except HTTPUserError:
        sys.exit()


def upload_fw(config):
    # dsn_name/implement/file
    client = connect(config['hdlManager']['host'])
    dsn_name = config['hdlManager']['dsn_name']
    for i in config['publisher']['webdave_files']:
        try:
            with open(i, 'rb') as f:
                content = f.read()
        except IOError:
            print('Cant open file ' + os.path.abspath(i))
            continue

        root, ext = os.path.splitext(os.path.basename(i))
        name = os.path.basename(root)
        folder = config['hdlManager']['webdavBuildPath'] + '/' + dsn_name
        print('Uploading folder: ', folder, end=' ')
        print(client.mkcol(folder))
        path = '{folder}/{name}'.format(folder=folder,
            name=name,
        )

        dst = path + '_info'
        info = "charset=utf-8\n"
        info += config['publisher']['message'].decode(sys.stdin.encoding or 'utf-8').encode('utf-8')
        print('Uploading info: ', dst, end=' ')
        print(client.put(dst, info))

        dst = path + ext
        print('Uploading file: ', dst, end=' ')
        print(client.put(dst, content))


def getContent(iFile):
    try:
        with open(iFile, "rb") as f:
            data = f.read()
    except IOError as e:
        print(e)
        sys.exit()
    return data


def connect(host='cs.scircus.ru'):
    try:
        username, password = authenticate(host)
        client = tinydav.WebDAVClient(host)
        client.setbasicauth(username, password)
        return client
    except socket.gaierror as e:
        print(e)
        print('Cant connect to server')
        sys.exit()


#@log_call
def upload(src, dst, host='cs.scircus.ru'):
    #TODO: atomic uploading
    client = connect(host)
    try:
        d = dst if dst[-1] != '/' else dst[:-1]
        client.get(os.path.dirname(d))
    except HTTPUserError as e:
        print('Wrong destination:', dst, e)
        sys.exit()

    try:
        if 'HTTP/1.1 200 OK' in client.propfind(dst + '//').content:
            print('Already exists: ', dst)
            sys.exit()
    except HTTPUserError:
        pass

    if os.path.isfile(src):
        content = getContent(src)
        print('Uploading file: ', dst, end=' ')
        print(client.put(dst, content))
    else:
        path_was = os.getcwd()
        print(dst, client.mkcol(dst))
        try:
            os.chdir(src)
            for root, dirs, files in os.walk('.'):
                for d in dirs:
                    ad = os.path.join(root, d).replace('\\', '/')
                    web_dst = '{0}{1}'.format(dst, ad.replace('./', '/'))
                    print(web_dst, end=' ')
                    print(client.mkcol(web_dst))
                for f in files:
                    af = os.path.join(root, f).replace('\\', '/')
                    web_dst = '{0}{1}'.format(dst, af.replace('./', '/'))
                    print(web_dst, end=' ')
                    content = open(af).read()

                    headers = None if content else {'Content-Length': 0}
                    print(client.put(web_dst,
                        content,
                        headers=headers))
        finally:
            os.chdir(path_was)


if __name__ == '__main__':
    print(authenticate())