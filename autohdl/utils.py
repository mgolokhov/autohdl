import shutil
import os
import hashlib
import logging

log = logging.getLogger(__name__)


def copy_only_new(src, dest):
    h1 = hashlib.sha1()
    h1.update(open(src))
    h2 = hashlib.sha1()
    h2.update(open(dest))
    if h1.hexdigest() != h2.hexdigest():
        try:
            log.info("Removing " + dest)
            os.remove(dest)
            shutil.copy(src, dest)
        except Exception as e:
            log.warning(e)
    else:
        log.info("Didn't copy because same content")


def is_same_contents(file1, file2):
    h1 = hashlib.sha1()
    h2 = hashlib.sha1()
    with open(file1) as f:
        h1.update(f.read().encode('utf-8'))
    with open(file2) as f:
        h2.update(f.read().encode('utf-8'))
    return h1.hexdigest() == h2.hexdigest()
