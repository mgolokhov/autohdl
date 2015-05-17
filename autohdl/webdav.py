import getpass
import locale
import os
from netrc import netrc
import requests
from urllib.parse import urlparse
import logging
import sys

try:
    import autohdl.hdl_logger
except ImportError:
    import hdlLogger
alog = logging.getLogger(__name__)


#src type could be string or path to file
def upload(src, dst, src_type='file'):
    c = Client()
    c.upload(src, dst, src_type)


class Client(object):
    def __init__(self):
        self.session = requests.session()
        #self.session.headers = {'Content-Type': 'application/octet-stream'}
        self.auth = None
        self.host = None
        self.baseurl = None
        self.path = None
        self.content = None
        self.dirs = None
        self.path_to_check_auth = None
        self.username = None
        self.password = None

    def read_src(self, path):
        with open(path, 'rb') as f:
            self.content = f.read()

    def parse_dst(self, url):
        url = url.strip('/')
        res = urlparse(url)
        if res.scheme and res.netloc and res.path:
            self.host = res.netloc
            self.baseurl = res.scheme+'://'+res.netloc
            self.path = res.path
            self.dirs = [i for i in res.path.split('/') if i]
            self.path_to_check_auth = self.baseurl+'/'+self.dirs[0]
        else:
            raise TypeError("Wrong url: " + str(res))

    def check_auth(self, default=True):
        #auto check ~/_netrc
        if default:
            auth = ()
        else:
            auth = (self.username, self.password)
        if self.session.request(method='head',
                                url=self.path_to_check_auth,
                                auth=auth).status_code == 200:
            alog.info('Authentication Ok')
            return True

    def authenticate(self):
        alog.info('Authentication...')
        if self.check_auth():
            return
        state = 'ask'
        while True:
            if state == 'check':
                if self.check_auth(default=False):
                    state = 'dump'
                else:
                    state = 'ask'
            elif state == 'ask':
                self.ask_auth()
                state = 'check'
            elif state == 'dump':
                self.dump_auth()
                return

    def ask_auth(self):
        quitung = input('Need Authentication. To cancel hit Q or Enter to continue: ')
        if quitung.lower() == 'q':
            alog.info('Exit...')
            sys.exit(0)
        self.username = input('user: ')
        self.password = getpass.getpass('password: ')

    def dump_auth(self):
        path = os.path.expanduser("~\\_netrc")
        try:
            n = netrc(path)
            n.hosts.update({self.host:
                          (self.username, None, self.password)})
            new_content = str(n).replace("'", '')
        except Exception as e:
            alog.warning(e)
            new_content = 'machine {host}\n' \
                          'login {user}\n' \
                          'password {password}'.format(host=self.host,
                                                       user=self.username,
                                                       password=self.password)
        try:
            with open(path, 'w') as f:
                f.write(new_content)
        except IOError as e:
            alog.warning(e)
            alog.warning('Cannot save auth to file: '+path)

    def upload(self, src, dst, src_type='file'):
        alog.info('Uploading\nsrc = {}\ndst = {}'.format(src, dst))
        self.parse_dst(dst)
        if src_type == 'file':
            self.read_src(src)
        else:
            self.content = src.encode('utf-8')
        self.authenticate()
        start = self.baseurl
        for i in self.dirs[:-1]:
            start = start + '/' + i
            if self.session.request(method='HEAD', url=start).status_code != 200:
                self.session.request(method='MKCOL', url=start)
        self.session.request(method='PUT', url=dst, data=self.content)
        r = self.session.request(method='get', url=dst)
        alog.info('Status: {}({})'.format(r.reason, r.status_code))


if __name__ == '__main__':
    alog.info('ping')
    i = "русишь нихт nicht"

    print("default enc: {}\npreferred enc: {}\nstdin enc: {}".format(sys.getdefaultencoding(),
                                                                    locale.getpreferredencoding(),
                                                                    sys.stdin.encoding))
    upload(i, 'http://cs.scircus.ru/test/distout/rtl/info.txt', src_type='string')
    upload('drafts/a1.py', 'http://cs.scircus.ru/test/distout/rtl/pypy.txt')