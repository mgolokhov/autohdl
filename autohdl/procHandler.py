import subprocess
import os
import json


def getConfigure():
    home = os.path.expanduser('~')
    return os.path.join(home, 'autohdl_proc')


def dump(pid, arg):
    config = getConfigure()
    if not os.path.exists(config):
        with open(config, 'w') as f:
            f.write(json.dumps({pid: arg}))
    else:
        with open(config) as f:
            data = json.loads(f.read())
            data.update({pid: arg})
            with open(config, 'w') as fw:
                fw.write(json.dumps(data, indent=4))


def load():
    config = getConfigure()
    try:
        with open(config) as f:
            data = json.loads(f.read())
    except:
        data = {}
    return data


def popen(*args, **kw):
    p = subprocess.Popen(*args, **kw)
    dump(pid=p.pid, arg=str(args) + str(kw))
    return p


def killAll():
    pythonPids = []
    for k in ['python.exe', 'pythonw.exe']:
        p = subprocess.check_output('cmd /c "tasklist /fo list  /fi "imagename eq {}""'.format(k))
        print(p)
        for i in p.splitlines():
            if "pid" in i.lower():
                pythonPids.append(i.split(':')[1].strip())
    autohdlPids = load()
    for i in pythonPids:
        if i in list(autohdlPids.keys()):
            print('killing ', i)
            #      os.kill(int(i), signal.CTRL_C_EVENT)
            kill(int(i))
        # clean proc list
    try:
        os.remove(getConfigure())
    except:
        pass


import ctypes

def kill(pid):
    """kill function for Win32"""
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(1, 0, pid)
    return (0 != kernel32.TerminateProcess(handle, 0))

if __name__ == '__main__':
#  popen('python drafts/aaadraft2.py')
#  popen('pythonw drafts/aaadraft2.py')

    killAll()