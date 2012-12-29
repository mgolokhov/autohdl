import Queue
from Tkinter import *
from threading import Thread
import threading
from ttk import *
from tkFileDialog import askdirectory
from tkFont import Font
import os
import time

import model

from dialog_ import Dialog


class MyDialog(Dialog):

  def body(self, master):
    Label(master, text="User:").grid(row=0, sticky='w')
    Label(master, text="Password:").grid(row=1, sticky='w')

    self.entry_user = Entry(master)
    self.entry_password = Entry(master, show="*")
    self.entry_user.grid(row=0, column=1)
    self.entry_password.grid(row=1, column=1)

    self.save_password = BooleanVar()
    Checkbutton(master,
                text='save (caution: in plain text)',
                variable=self.save_password).grid(row=2, columnspan=2)
    self.result = None, None, None
    return self.entry_user # initial focus

  def apply(self):
    self.result = (self.entry_user.get(),
                   self.entry_password.get(),
                   self.save_password.get())



class Application(Frame):
  def log_action(self, arg):
    if arg:
      if not isinstance(arg, basestring):
        arg = str(arg)
      if type(arg) is not unicode:
        arg = unicode(arg, encoding='utf-8')
      self.text2.insert(END, arg + '\n')
      self.text2.yview(END)
#    self.update()
    self.update_idletasks()

  def global_hotkeys(self):
    self.bind_all('<F5>', self.refresh_firmwares)

  def auth_current_repo(self, auth_as_other_user=False):
    self.data.current_repo = self.entry_repo.get()
    while not self.data.authenticate(auth_as_other_user=auth_as_other_user):
      d = MyDialog(self, title='login')
      if d.give_up:
        return
      self.data.user, self.data.password, self.data.save_password = d.result
    return True

  def refresh_listbox(self):
    try:
      if not self.queue.empty():
        self.listbox.delete(0, END)
        for i in self.queue.get(0):
          self.listbox.insert(END, i)
    except Queue.Empty:
      pass
    self.after(100, self.refresh_listbox)

  def refresh_firmwares(self, event=None):
    if not self.auth_current_repo():
      return
    t = threading.Thread(target=self.data.get_firmwares)
    t.setDaemon(1)
    t.start()

  def browse_handle(self):
    d = askdirectory()
    if d:
      os.chdir(d)
      self.data.cwd = d
      self.working_dir.set(d)
      self.log_action('Changed working folder to ' + d)

  def filter_handle(self, event=None):
    filtered = [i for i in self.data.firmwares if self.afilter.get() in i]
    self.listbox.delete(0, END)
    for i in filtered:
      self.listbox.insert(END, i)

  def info_handle(self, event=None):
    res = self.listbox.get(self.listbox.curselection()).split(':')[1]
    self.log_action('Comment message:\n'+res)
    self.data.download_firmware(self.listbox.get(self.listbox.curselection()))

  def auto_refresh_handle(self, event=None):
    self.update()
    if self.auto_refresh.get():
      self.refresh_firmwares()
      self.data.download_firmware(self.listbox.get(0))
      self.auto_refresher_id = self.after(5000, self.auto_refresh_handle)
    else:
      self.after_cancel(self.auto_refresher_id)

  def create_widgets(self):
    fr1 = Frame(self)
    fr1.grid(column=0, row=0, sticky='e,w')
    fr1.columnconfigure(1, weight=1)

    Label(fr1, text = "Server:").grid(column=0, row=0)

    self.entry_repo = Combobox(fr1, width=50, textvariable=self.data.current_repo)
    self.entry_repo['values'] = self.data.repos
    self.entry_repo.current(0)
    self.entry_repo.grid(column=1, row=0, sticky='e,w')
    self.entry_repo.bind('<<ComboboxSelected>>', self.refresh_firmwares)
    self.entry_repo.bind('<Return>', self.refresh_firmwares)

    button = Button(fr1, text = "Refresh")
    button["command"] = self.refresh_firmwares
    button.grid(column=2, row=0)

    Label(fr1, text="CWD:").grid(column=0, row=1)
    self.working_dir = StringVar()
    self.working_dir.set(os.getcwd())
    entry = Entry(fr1, width=50, textvariable=self.working_dir, state=DISABLED)
    entry.grid(column=1, row=1, sticky='e,w')

    button = Button(fr1, text = "Browse", command=self.browse_handle)
    button.grid(column=2, row=1)

    self.auto_refresh = IntVar()
    checkbutton = Checkbutton(fr1)
    checkbutton['text'] = 'Automatically refresh and save latest firmware in current working directory (CWD)'
    checkbutton['variable'] = self.auto_refresh
    checkbutton['command'] = self.auto_refresh_handle
    checkbutton.grid(column=1, row=2, columnspan=1, sticky='w')

    button = Button(fr1, text='Login as')
    button['command'] = lambda: self.auth_current_repo(auth_as_other_user=True)
    button.grid(column=2, row=2)

    self.afilter = StringVar()
    entry = Entry(fr1, textvariable=self.afilter)
    entry.grid(column=0, columnspan=3, row=3, sticky='e,w', padx=5, pady=1)
    entry.bind('<KeyRelease>', self.filter_handle)

    fr2 = Frame(self)
    fr2.grid(column=0, row=1, sticky=E+W)
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
    self.listbox.grid(row=0, column=0, sticky=E+W+N+S, padx=5, pady=2)
    yScroll["command"] = self.listbox.yview
    self.listbox.bind("<<ListboxSelect>>", self.info_handle)


    fr4 = Frame(self)
    fr4.grid(column=0, row=2)
    yScroll = Scrollbar(fr4, orient=VERTICAL)
    yScroll.grid(column=1, row=0, sticky=N+S)

    self.text2 = Text(fr4, font=Font( family="Helvetica", size=9 ), yscrollcommand=yScroll.set)
    self.text2.grid(column=0,row=0, sticky='s,e,n,w', padx=5, pady=2)
    yScroll["command"] = self.text2.yview
    self.text2.insert(END, "Valid shortcuts: Refresh- F5\n\n")

    self.progress = Progressbar(self, orient = "horizontal", length = 200, mode = "determinate")
    self.progress.grid(column=0, row=3, sticky='e,w')


  def __init__(self, master=None):
    Frame.__init__(self, master)
    self.grid(sticky=N+S+E+W)

    top = self.winfo_toplevel()
    top.title('AutoHDL progammator v0.4')
    top.resizable(width=FALSE, height=FALSE)

    self.queue = Queue.Queue()
    self.data = model.Data(log_action=self.log_action, queue=self.queue)
    self.create_widgets()
    self.global_hotkeys()
    self.refresh_listbox()



def run():
  root = Tk()
  app = Application(master=root)
  app.mainloop()


if __name__ == '__main__':
  os.chdir('d:/00')
  run()

