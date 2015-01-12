import threading
import time
import sys

done = False

def progressBar(l=['|', '/', '-', '\\', 0]):
    while not done:
        sys.stdout.write('\r{}\r'.format(l[l[-1]]))
        l[-1] = (l[-1] + 1) % (len(l) - 1)
        time.sleep(0.4)


def progress_bar2():
    while not done:
        sys.stdout.write(".")
        time.sleep(1)

def run():
    t = threading.Thread(target=progress_bar2)
    t.setDaemon(1)
    t.start()


def stop():
    global done
    done = True
