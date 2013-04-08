import locale
import netrc
from netrc import NetrcParseError
import os
import shutil
import subprocess
from urlparse import urlparse

#from autohdl.hdlLogger import  logging
#log = logging.getLogger(__name__)

import requests
import sys

BB_API = 'https://api.bitbucket.org/1.0/user/repositories'
BB_HOST = 'bitbucket.org'

class Data():
#  def log_action(self, *args):
#    pass

    def __init__(self, log_action, queue):
        self.log_action = log_action
        self.queue = queue

        self.user = None
        self.password = None
        self.save_password = None

        # load repo list
        self.repos = ('https://bitbucket.org/mgolokhov/autohdl_programmator_test',
                      'https://bitbucket.org/mgolokhov/testfirmware',
                      'https://bitbucket.org/mgolokhov/testprog',
                      'dump/repo')
        self.current_repo = None

        self.firmwares = ''
        self.current_firmware = None
        self.cwd = os.getcwd()
        self.autohdl_dir = os.path.join(os.path.expanduser('~'), 'autohdl')

    def authenticate(self, auth_as_other_user=False):
        u, _, p = self.auth_load(BB_HOST)
        res = requests.get(url=BB_API, auth=(u, p))
        if auth_as_other_user or res.status_code != 200:
            res = requests.get(url=BB_API, auth=(self.user, self.password))
            print res
            if res.status_code != 200:
                self.log_action('Authentication required. Status code: {}'.format(res.status_code))
                return
            else:
                self.log_action('Authenticated as "{}" OK'.format(self.user))
        else:
            self.log_action('Authenticated as "{}" OK'.format(u))
        current_repo_name = os.path.basename(urlparse(self.current_repo).path)
        for i in res.json():
            if current_repo_name == i['name']:
                self.log_action('Permissions to read "{}" OK'.format(current_repo_name))
                if self.save_password:
                    self.auth_dump(BB_HOST, self.user, self.password)
                return True
        self.log_action('Permissions to read "{}" DENIED'.format(current_repo_name))
        return

    def _popen(self, prog):
        p = subprocess.Popen(prog.encode(locale.getpreferredencoding()),
            shell=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        out, err = p.communicate()
        out = unicode(out, encoding='utf-8')
        err = unicode(err, encoding='utf-8')
        return p, out, err

    def get_firmwares(self):
        # git clone current_repo
        # git log --all --grep "_build_" --format="%s"
        # return list
        current_repo_name = os.path.basename(urlparse(self.current_repo).path)
        if not os.path.exists(self.autohdl_dir):
            os.makedirs(self.autohdl_dir)
        current_repo_location = os.path.join(self.autohdl_dir, current_repo_name)
        p, out, err = self._popen('git clone {}.git {}'.format(self.current_repo,
            current_repo_location))
        self.log_action('')
        os.chdir(current_repo_location)
        p, out, err = self._popen('git pull --all'.format(self.current_repo))
        self.log_action('')
        if 'fatal' in err:
            print err
            return
        p, out, err = self._popen('git log --all --grep="_build_" --format="%s"')
        self.log_action('')
        if 'fatal' in err:
            print err
            return
        self.firmwares = out.splitlines()
        self.queue.put(self.firmwares)
        return self.firmwares


    def download_firmware(self, firmware):
        # git log --all --grep "current_firmware" --format="%h"
        # git checkout %h => dsn/resource/build_name.bit
        self.current_firmware = firmware
        p, out, err = self._popen(u'git log --all --grep "{}" --format="%h_#$@_%s"'.format(self.current_firmware))
        self.log_action('')
        sha, message = out.strip().split('_#$@_')
        p, out, err = self._popen('git checkout {}'.format(sha))
        self.log_action('')
        current_repo_name = os.path.basename(urlparse(self.current_repo).path)
        firmware_dir = os.path.join(self.autohdl_dir, current_repo_name, 'resource')
        firmware_ext = ['.bit', '.mcs']
        for f in os.listdir(firmware_dir):
            if os.path.splitext(f)[1] in firmware_ext:
                src = os.path.join(firmware_dir, f)
                dest = os.path.join(self.cwd, f)
                shutil.copy(src, dest)
                self.log_action('Saved as {}'.format(dest))


    def auth_dump(self, host, user, password):
        #check {host{user,password}}
        content = None
        try:
            _netrc = netrc.netrc(self.get_netrc_path())
            u, _, p = _netrc.hosts[host] # no host -> KeyError
            if user != u or password != p:
                raise KeyError
            print 'no need auth_dump'
            return
        except (IOError, netrc.NetrcParseError):
            content = 'machine {host}\n'\
                      'login {user}\n'\
                      'password {password}'.format(host=host,
                user=user,
                password=password)
        except KeyError:
            _netrc.hosts.update({host: (user, None, password)})
            content = str(_netrc).replace("'", '')
        try:
            with open(self.get_netrc_path(), 'w') as f:
                f.write(content)
        except IOError:
            self.log_action('Cant save data to ' + self.get_netrc_path())


    def get_netrc_path(self):
        home = os.path.expanduser('~')
        return os.path.join(home, '_netrc')

    def auth_load(self, hostname):
        res = {}
        try:
            res = netrc.netrc(self.get_netrc_path()).hosts
        except (IOError, netrc.NetrcParseError):
            pass
        return  res.get(hostname, (None, None, None))