import base64
from collections import namedtuple
import httplib
import os
import re
import subprocess
import urllib2
from urlparse import urlparse
from autohdl import toolchain
from lxml.etree import HTML, ElementTree
import sys
import time

from autohdl.hdlLogger import log_call, logging
log = logging.getLogger(__name__)


FirmWare = namedtuple('Firmware', 'name uri date size')


class PLogic():
  def __init__(self, iQueue, oQueue = None):
    self.digilent = os.path.dirname(__file__)+'/../lib/djtgcfg.exe'
    self.username = None
    self.password = None
    self.url = None
    self.authenticated = False
    self.iQueue = iQueue
    self.oQueue = oQueue
    self.firmwares = {}
    self.newData = False
    self.folders = None
    self.alias = None
    self.devices = None
    self.impact = toolchain.Tool().get('ise_impact')
    self.output = ''
    self.cable = None # digilent vs xilinx


  def authenticate(self):
    if not self.iQueue.empty():
      user, pswd, path = self.iQueue.get()
      if (user, pswd, path) == (self.username, self.password, self.url):
        return
      self.username, self.password, self.url = user, pswd, (path if path[-1] == '/' else path+'/')
      self.newData = True
      self.firmwares = {}
#      print self.username, self.password, self.url

      url = urlparse(self.url)
      conn = httplib.HTTPConnection(url.netloc)
      base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
      authheader =  "Basic %s" % base64string
      headers = { "Authorization": authheader}
      conn.request(method='HEAD', url=url.path, headers=headers)
      res = conn.getresponse()
      conn.close()
      if res.status == 200: # ok
        self.authenticated = True
      else:
        self.authenticated = False


  def getFirmwares(self):
#    print 'refreshing'
    url = urlparse(self.url)
    params =  '<?xml version="1.0" encoding="utf-8" ?>\n' +\
              '<D:propfind xmlns:D="DAV:">\n'+\
              '<D:allprop/>\n' +\
              '</D:propfind>'
    base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
    authheader =  "Basic %s" % base64string
    headers = {
      "Content-Type" :  "application/xml; charset=\"utf-8\"",
      "Authorization": authheader,
      "Depth" : "1"}
    conn = httplib.HTTPConnection(url.netloc)
    conn.request("PROPFIND", url.path, params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()

    if "Authorization Required" in data:
      self.authenticated = False
      return

    data_elements = HTML(data)
    xml_etree = ElementTree(data_elements)
    all_response_elements = xml_etree.findall("//response")
    self.folders = []
    for response in all_response_elements:
      resp_tree = ElementTree(response)
      if resp_tree.find('//collection') is None:
        uri = resp_tree.find("//href").text
        getcontentlength = getattr(resp_tree.find('//getcontentlength'), 'text', None)
        getlastmodified = getattr(resp_tree.find('//getlastmodified'), 'text', None)
        name = os.path.basename(uri)
        self.firmwares[name] = FirmWare(name,url.scheme+'://'+url.netloc+uri,getlastmodified,getcontentlength)
      else:
        self.folders.append(resp_tree.find("//href").text)



  def updateFirmwaresList(self):
    while True:
      if not self.iQueue.empty():
#        print 'queue'
        self.authenticate()
        self.getFirmwares()
        self.oQueue.put('Data updated')
      elif self.authenticated:
#        print 'get'
        self.getFirmwares()
      time.sleep(.2)



  def downloadFirmware(self, firmware):
    url = self.firmwares[firmware].uri
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(request)
    f = open(file_name, 'wb')
    f.write(u.read())
    f.close()


  def getFirmwareinfo(self, firmware):
    file = os.path.splitext(firmware)[0]+'_info'
    url = urlparse(self.firmwares[file].uri)
    uri = url.path
    host = url.netloc
    params =  ''
    base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
    authheader =  "Basic %s" % base64string
    headers = {"Authorization": authheader}

    conn = httplib.HTTPConnection(host)
    conn.request("GET", uri, params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    r = re.findall('spi:\s*(\w+)', data)
    if r:
      self.spiDevice = r[0]
    return data

  @log_call
  def program(self, fw_name, board_name, chip_idx):
    log.debug('Cable type: '+self.cable)
    if self.cable == 'digilent':
      p = subprocess.Popen("{}" \
                           " prog -d {} " \
                           "-f {} " \
                           "-i {}".format(self.digilent, self.alias, fw_name, str(chip_idx)),
                           stdin = subprocess.PIPE,
                           stdout = subprocess.PIPE
      )
      p.stdin.write('Y\n')
      self.output = p.stdout.read()
    elif self.cable == 'xilinx':
      if chip_idx == 0:
        with open('init.bat', 'w') as f:
          f.write('setMode -bs\n'
                  'setCable -p auto\n'
                  'identify\n'
                  'assignFile -p 1 -file {}\n' \
                  'program -p 1\n' \
                  'quit'.format(fw_name))
        p = subprocess.Popen(self.impact+' -batch init.bat',
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
  
        self.output = p.stdout.read()
        res =  p.stderr.read()
        self.output += res
      elif chip_idx == 1:
        with open('init.bat', 'w') as f:
          f.write('setMode -bs\n'
                  'setCable -p auto\n'
                  'identify\n'
                  'attachflash -position 1 -spi "{}"\n'
                  'assignfiletoattachedflash -position 1 -file {}\n'\
                  'Program -p 1 -spionly -e -v -loadfpga\n'\
                  'quit'.format(self.spiDevice, fw_name))
        p = subprocess.Popen(self.impact+' -batch init.bat',
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        self.output = p.stdout.read()
        res =  p.stderr.read()
        self.output += res
    return self.output

  def tryDigilent(self):
    self.output = '\nTrying digilent\n'
    resEnum = subprocess.check_output('{} enum'.format(self.digilent))
    self.output += resEnum
    it = iter(resEnum.splitlines())
    aliases = [i.split()[-1] for i in it if 'Device: 'in i and 'Not accessible' not in it.next()]
    if aliases:
      self.alias = aliases[0]
      resInit = subprocess.check_output('{} init -d {}'.format(self.digilent, aliases[0]))
      self.output += resInit
      self.devices = [i.split()[-1] for i in resInit.splitlines() if 'Device 0:' in i or 'Device 1' in i]
      self.cable = 'digilent'
      return True #devices found

  def tryImpact(self):
    self.output += '\nTrying impact\n'
    with open('init.bat', 'w') as f:
      f.write('setMode -bs\nsetCable -p auto\nidentify\nquit')
    p = subprocess.Popen(self.impact+' -batch init.bat',
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    self.output += p.stdout.read()
    res =  p.stderr.read()
    self.output += res
    if 'Cable connection failed' not in self.output:
      self.devices = re.findall('Added Device (\w+) successfully', res)
      self.cable = 'xilinx'
      self.devices += [self.spiDevice]


  def initialize(self):
    if not self.tryDigilent():
      if self.impact:
        self.tryImpact()
    self.oQueue.put('Done')
    return self.output