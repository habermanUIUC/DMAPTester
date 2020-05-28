import os

import time
from datetime import datetime

from tf.utils.SimpleLogger import SimpleLogger


def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


SANDBOX_DIR = "./sandbox_tmp"
SESSION_FILE = "{:s}/session.txt".format(SANDBOX_DIR)


@singleton
class SandBox(object):

    def __init__(self):
        if not os.path.isdir(SANDBOX_DIR):
            os.mkdir(SANDBOX_DIR)
        self._logger = SimpleLogger(SANDBOX_DIR)
        self._sandbox = SANDBOX_DIR

        # a session has to do with persistence
        # on line editors (colab, replit) will timeout after
        # non activity
        self.session_created = False
        if not os.path.exists(SESSION_FILE):
            self.session_created = True
            with open(SESSION_FILE, 'w') as fd:
                now = time.time()
                dt = datetime.fromtimestamp(now)
                fd.write(dt.strftime('%Y-%m-%d %H:%M:%S'))
                fd.close()

        #print(os.getcwd())
        #print('SANDBOX init', SESSION_FILE, self.session_created, os.path.exists(SESSION_FILE))

    def get_logger(self):
        return self._logger

    def get_sandbox_dir(self):
        return self._sandbox

    def get_session_information(self):
        #print(os.getcwd())
        #print('SANDBOX info', SESSION_FILE, self.session_created, os.path.exists(SESSION_FILE))
        s_time = os.path.getmtime(SESSION_FILE)  # modified time
        return self.session_created, s_time


# class SandBox(object):
#
#     __instance = None
#     __logger = None
#     SANDBOX_DIR = "./sandbox_tmp"
#
#     def __new__(cls):
#         if SandBox.__instance is None:
#             SandBox.__instance = object.__new__(cls)
#             SandBox.__logger = SimpleLogger.SimpleLogger(SANDBOX_DIR)
#         return SandBox.__instance
#
#     def __init__(self):
#         print('INIT')
#         if not os.path.isdir(SANDBOX_DIR):
#             os.mkdir(SANDBOX_DIR)

