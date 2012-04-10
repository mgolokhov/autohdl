from Queue import Queue
from Tkinter import *
from collections import namedtuple
from pprint import pprint
import threading
from tkFileDialog import askdirectory
from tkFont import Font
from ttk import *
import urllib2
from urlparse import urlparse

from datetime import *
import time
import httplib
from lxml.etree import Element, ElementTree, HTML
import base64
import os
import subprocess


FirmWare = namedtuple('Firmware', 'name uri date size')


class PLogic():
  def __init__(self, iQueue, oQueue = None):
    self.username = None
    self.password = None
    self.url = None
    self.authenticated = False
    self.iQueue = iQueue
    self.oQueue = oQueue
    self.firmwares = {}
    self.newData = False
    self.folders = None


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
    return data

  def program(self, fw_name, board_name, chip_idx):
    p = subprocess.Popen("{}/Lib/site-packages/autohdl/lib/djtgcfg.exe" \
                         " prog -d {} " \
                         "-f {} " \
                         "-i {}".format(sys.prefix, board_name, fw_name, str(chip_idx)),
                         stdin = subprocess.PIPE,
                         stdout = subprocess.PIPE
    )
    p.stdin.write('Y\n')
    return p.stdout.read()



class Application(Frame):
  def logAction(self, arg):
    self.text2.insert(END, str(arg)+'\n')
    self.text2.yview(END)

  def globalHotkeys(self):
    self.bind_all('<F5>', self.refreshList)
    self.bind_all('<Control-a>', self.initDeviceHandle)
    self.bind_all('<Control-s>', self.progDevice0Handle)
    self.bind_all('<Control-d>', self.progDevice1Handle)

  def createWidgets(self):
    fr1 = Frame(self)
    fr1.grid(column=0, row=0, sticky='e,w')
    fr1.columnconfigure(1, weight=1)

    Label(fr1, text = "Server:").grid(column=0, row=0)


    entry = Entry(fr1, width=50, textvariable=self.serverPath)
    entry.grid(column=1, row=0, sticky='e,w')


    button = Button(fr1, text = "Refresh")
    button["command"] = self.refreshList
    button.grid(column=2, row=0)


    Label(fr1, text="Working folder:").grid(column=0, row=1)

    self.workingDir = StringVar()
    self.workingDir.set(os.getcwd())
    entry = Entry(fr1, width=50, textvariable=self.workingDir, state=DISABLED)
    entry.grid(column=1, row=1, sticky='e,w')

    button = Button(fr1, text = "Browse", command=self.browseHandle)
    button.grid(column=2, row=1)

    fr2 = Frame(self)
    fr2.grid(column=0, row=1, sticky=E+W, padx=5, pady=5)
    fr2.columnconfigure(0, weight=1)

    self.list_val = StringVar()
    yScroll = Scrollbar(fr2, orient=VERTICAL)
    yScroll.grid(column=1, row=0, sticky=N+S)

    self.listbox = Listbox (fr2,
                            height = 5,
                            width = 50,
                            selectmode = SINGLE,
                            listvariable = self.list_val,
                            yscrollcommand=yScroll.set)
    self.listbox.grid(row=0, column=0, sticky=E+W+N+S)
    yScroll["command"] = self.listbox.yview
    self.listbox.bind("<<ListboxSelect>>", self.info)


    fr3 = Frame(fr2)
    fr3.grid(column=2, row=0)

    button = Button(fr3, text = "Initialize Device", command=self.initDeviceHandle)
    button.grid(column=0, row=0)

    self.button1 = Button(fr3, text = "Program device 0", state=DISABLED)
    self.button1['command'] = self.progDevice0Handle
    self.button1.grid(column=0, row=1)

    self.button2 = Button(fr3, text = "Program device 1", state=DISABLED)
    self.button2['command'] = self.progDevice1Handle
    self.button2.grid(column=0, row=2)

    fr4 = Frame(self)
    fr4.grid(column=0, row=2)
    yScroll = Scrollbar(fr4, orient=VERTICAL)
    yScroll.grid(column=1, row=0, sticky=N+S)

    self.text2 = Text(fr4, font=Font( family="Helvetica", size=9 ), yscrollcommand=yScroll.set)
    self.text2.grid(column=0,row=0, sticky='s,e,n,w', padx=5, pady=5)
    yScroll["command"] = self.text2.yview
    self.text2.insert(END, "Valid hot keys:\n"
                           "Refresh: F5;\n"
                           "Initialize Device: ctrl+a;\n"
                           "Program Device 0: ctrl+s;\n"
                           "Program Device 1: ctrl+d;\n")

    self.progress = Progressbar(self, orient = "horizontal", length = 200, mode = "determinate")
    self.progress.grid(column=0, row=3, sticky='e,w')


  def browseHandle(self):
    d = askdirectory()
    if d:
      os.chdir(d)
      self.workingDir.set(d)
      self.logAction('Changed working folder to ' + d)


  def info(self, *event):
    if self.listbox.curselection():
      file = self.listbox.get(self.listbox.curselection()[0])
      info = self.prg.getFirmwareinfo(file)
      self.logAction('\nFirmware info:\n'+info)


  def initDeviceHandle(self, *args):
#    print self.listbox.curselection()
    resEnum = subprocess.check_output('{}/Lib/site-packages/autohdl/lib/djtgcfg.exe' \
                                      ' enum'.format(sys.prefix))
    self.logAction(resEnum)
    it = iter(resEnum.splitlines())
    aliases = [i.split()[-1] for i in it if 'Device: 'in i and 'Not accessible' not in it.next()]
    self.alias = aliases[0]
    resInit = subprocess.check_output('{}/Lib/site-packages/autohdl/lib/djtgcfg.exe' \
                                      ' init -d {}'.format(sys.prefix, aliases[0]))
    self.logAction(resInit)
    devices = [i.split()[-1] for i in resInit.splitlines() if 'Device 0:' in i or 'Device 1' in i]
    if devices:
      self.button1['text'] = 'Program ' + devices[0]
      self.button1['state'] = NORMAL
      self.button2['text'] = 'Program ' + devices[1]
      self.button2['state'] = NORMAL

  def progDevice0Handle(self, *args):
    self.program(0)


  def progDevice1Handle(self, *args):
    self.program(1)

  def program(self, index):
    if self.alias:
      self.logAction('programming')
      if self.listbox.curselection():
        file = self.listbox.get(self.listbox.curselection()[0])
        self.prg.downloadFirmware(file)
        self.logAction(self.prg.program(file, self.alias, index))
      else:
        self.logAction('Firmware is not selected')
    else:
      self.logAction('Device is not initialized')


  def updateList(self):
    self.logAction("Logged in")
    res = sorted(self.prg.firmwares,
                 key=lambda k: time.strptime(self.prg.firmwares[k].date, '%a, %d %b %Y %H:%M:%S %Z'),
                 reverse =True)
    self.list_val.set(' '.join([i for i in res if '.bit' in i]))
    size = self.listbox.size()
    if size:
      self.listbox.select_clear(0, size)
      self.listbox.see(0)
      self.listbox.select_set(0)
      self.info()
    else:
      self.logAction('Found folders: '+'\n'.join(self.prg.folders))
    self.progress.stop()

  def refreshList(self, *args):
    self.logAction('Refreshing firmwares list')
    self.win = Toplevel()
    self.login_submit()


  def login(self, *args):
    self.win = Toplevel()
    self.win.title("Login")
    Label(self.win, text="User:").grid(column=0,row=0)
    e = Entry(self.win, textvariable= self.user)
    e.grid(column=1,row=0)
    Label(self.win, text='Password:').grid(column=0,row=1)
    Entry(self.win, textvariable=self.password, show="*").grid(column=1,row=1)
    Button(self.win, text='OK', command=self.login_submit).grid(column=0,row=2, columnspan=2)
    self.win.bind('<Return>', self.login_submit)
    e.focus_set()


  def isNewData(self):
    if (self.userOld, self.pswdOld, self.pathOld) !=\
       (self.user.get(), self.password.get(), self.serverPath.get()):
      self.userOld, self.pswdOld, self.pathOld = self.user.get(), self.password.get(), self.serverPath.get()
      return True

  def login_submit(self, *args):
    self.logAction('Authentication')
    self.progress.start()
    self.win.destroy()
    if self.isNewData():
      self.queueToPLogic.put((self.user.get(), self.password.get(), self.serverPath.get()))
      while self.queueFromPLogic.empty():
        self.update()
      self.queueFromPLogic.get()
    if not self.prg.authenticated:
      self.logAction("Authorization Required")
      self.login()
    else:
      self.updateList()
      return



  def __init__(self, master=None):
    Frame.__init__(self, master)
    self.grid(sticky=N+S+E+W)

    top = self.winfo_toplevel()
    top.title('AutoHDL progammator v0.1')
    top.rowconfigure(0, weight=1)
    top.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight =1)
    self.columnconfigure(0, weight=1)


    self.queueToPLogic = Queue()
    self.queueFromPLogic = Queue()
    self.prg = PLogic(iQueue=self.queueToPLogic, oQueue=self.queueFromPLogic)
    self.alias = None
    self.user = StringVar()
    self.userOld = None
    self.pswdOld = None
    self.pathOld = None
#    self.user.set("_mgolokhov")
    self.password = StringVar()
    self.serverPath = StringVar()
#    self.serverPath.set('http://cs.scircus.ru/test/distout/rtl/autohdl_programmator_test/')
    self.serverPath.set('http://cs.scircus.ru/test/distout/rtl/')
    t = threading.Thread(target=self.prg.updateFirmwaresList)
    t.setDaemon(True)
    t.start()
    self.createWidgets()
    self.globalHotkeys()



def run():
  root = Tk()
  app = Application(master=root)
  app.mainloop()


if __name__ == '__main__':
  run()