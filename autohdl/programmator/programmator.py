from Queue import Queue
from Tkinter import *
from collections import namedtuple
import threading
from tkFileDialog import askdirectory
from tkFont import Font
from ttk import *

import time
import os
import subprocess
from autohdl.programmator.model import PLogic
import json
from urlparse import urlparse


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


    entry = Combobox(fr1, width=50, textvariable=self.serverPath)
    self.serverPath.set('http://cs.scircus.ru/test/distout/rtl/intercom/')
    entry['values'] = (
        'http://cs.scircus.ru/test/distout/rtl/intercom',
                    'http://cs.scircus.ru/test/distout/rtl/autohdl_programmator_test/',
        )
    entry.grid(column=1, row=0, sticky='e,w')
    entry.bind('<<ComboboxSelected>>', self.refreshList)
    entry.bind('<Return>', self.refreshList)


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

    Label(fr1, text="Filter:").grid(column=0, row=2)
    self.afilter = StringVar()
    entry = Entry(fr1, textvariable=self.afilter)
    entry.grid(column=1, row=2, sticky='e,w')
    entry.bind('<KeyRelease>', self._filter)

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
                           "Program Device 1: ctrl+d;\n\n")

    self.progress = Progressbar(self, orient = "horizontal", length = 200, mode = "determinate")
    self.progress.grid(column=0, row=3, sticky='e,w')

  def _filter(self, *args):
    res = sorted(self.prg.firmwares,
                 key=lambda k: time.strptime(self.prg.firmwares[k].date, '%a, %d %b %Y %H:%M:%S %Z'),
                 reverse =True)
    res = ' '.join([i for i in res
      if self.afilter.get() in i and os.path.splitext(i)[1] in [".bit",".mcs"]])
    self.list_val.set(res)


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
    self.logAction('Initializing devices...')
    self.progress.start()
    t = threading.Thread(target=self.prg.initialize)
    t.setDaemon(True)
    t.start()
    while self.queueFromPLogic.empty():
      self.update()
      time.sleep(.2)
    self.queueFromPLogic.get()
    self.logAction(self.prg.output)
    self.progress.stop()

#    self.logAction(self.prg.initialize())
    devices = self.prg.devices
    if devices:
      self.button1['text'] = 'Program ' + devices[0]
      self.button1['state'] = NORMAL
      if len(devices) == 2:
        self.button2['text'] = 'Program ' + devices[1]
        self.button2['state'] = NORMAL

  def progDevice0Handle(self, *args):
    self.program(0)


  def progDevice1Handle(self, *args):
    self.program(1)

  def program(self, index):
    if self.prg.cable:
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
    self.list_val.set(' '.join([i for i in res if os.path.splitext(i)[1] in ['.bit', '.mcs']]))
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
    Button(self.win, text='OK', command=self.login_submit).grid(column=1,row=2)
    Checkbutton(self.win, text='save', variable=self.save_auth).grid(column=0,row=2)
    self.win.bind('<Return>', self.login_submit)
    e.focus_set()


  def isNewData(self):
    if (self.userOld, self.pswdOld, self.pathOld) !=\
       (self.user.get(), self.password.get(), self.serverPath.get()):
      self.userOld, self.pswdOld, self.pathOld = self.user.get(), self.password.get(), self.serverPath.get()
      return True

  def auth_dump(self, d):
  #check {host{user,password}}
    if os.path.exists('auth'):
      f = open('auth')
      dd = json.load(f)
      f.close()
      if d.keys():
        host = d.keys()[0]
        if host in dd.keys() and d[host] != dd[host]:
          dd.update(d)
          f = open('auth', 'w')
          f.write(json.dumps(dd))
          f.close()
    else:
      f = open('auth', 'w')
      f.write(json.dumps(d))
      f.close()

  def auth_load(self, hostname):
    if os.path.exists('auth'):
      f = open('auth')
      d = json.load(f)
      f.close()
      return d[hostname]
    return {}

  def login_submit(self, *args):
    self.logAction('Authentication')
    self.progress.start()
    self.win.destroy()
    hostname = urlparse(self.serverPath.get()).hostname
    if self.isNewData():
      #load user pass
      if not self.user.get() and not self.password.get():
        d = self.auth_load(hostname)
        if d:
          self.user.set(d.get('user'))
          self.password.set(d.get('password'))
      self.queueToPLogic.put((self.user.get(), self.password.get(), self.serverPath.get()))
      while self.queueFromPLogic.empty():
        self.update()
        time.sleep(.2)
      self.queueFromPLogic.get()
    if not self.prg.authenticated:
      self.logAction("Authorization Required")
      self.login()
    else:
      if self.save_auth.get() == 1:
        self.auth_dump({hostname:{'user':self.user.get(),
                                  'password':self.password.get()}
                 })
      self.updateList()
      return



  def __init__(self, master=None):
    Frame.__init__(self, master)
    self.grid(sticky=N+S+E+W)

    top = self.winfo_toplevel()
    top.title('AutoHDL progammator v0.2')
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
    self.password = StringVar()
    self.save_auth = IntVar()
    self.serverPath = StringVar()
    t = threading.Thread(target=self.prg.updateFirmwaresList)
    t.setDaemon(True)
    t.start()
    self.createWidgets()
    self.globalHotkeys()



def run():
  root = Tk()
  app = Application(master=root)
  app.mainloop()


def run_debug():
  root = Tk()
  app = Application(master=root)
  app.prg.firmwares = 'qwer1 qwer2 qwer3 dfsd gfgf'.split()
  app.list_val.set('qwer1 qwer2 qwer3')
  app.mainloop()


def run_another_proc():
  subprocess.Popen('python {}/programmator.py'.format(os.path.dirname(__file__)))


if __name__ == '__main__':
  run()

