
import os
import sys
import json

import urllib.parse
import urllib.request
import requests
from datetime import datetime
import time

from tf.utils.SandBox import SandBox

logger = SandBox().get_logger()


def install_gd_file(doc_id, filename=None, cache_time=1):

    n_time = time.time()
    if os.path.exists(filename):
        read_cache = False
        m_time = os.path.getmtime(filename)  # modified time
        dt0 = datetime.fromtimestamp(m_time)
        dt1 = datetime.fromtimestamp(n_time)
        age = (dt1 - dt0).total_seconds()

        if age < cache_time:
            read_cache = True

        if read_cache:
            if os.path.getsize(filename) > 0:
                logger.log("Reading cached version:", filename, ":")
                with open(filename, 'r') as fd:
                    return fd.read(), m_time, True
            else:
                logger.log("Unable to read cache: Bad file size")
    #
    # possible 403 if attempt is made too many times to download?
    # seems to be temporary -- don't fire off too many requests
    #
    baseurl = "https://docs.google.com/uc"
    baseurl = "https://drive.google.com/uc"
    #
    # can help by switching the baseurl
    #

    params = {"export": "download", "id": doc_id}
    url = baseurl + "?" + urllib.parse.urlencode(params)

    try:

        def v1():
            logger.log('fetching google doc', url)
            r = urllib.request.urlopen(url)
            status = r.getcode()
            if status != 200:
                print(r.status_code, "unable to download google doc with id:", doc_id)
                return None
            return str(r.read().decode('UTF-8'))

        def v2():
            #r = requests.get(baseurl, params)
            logger.log('fetching google doc', url)
            r = requests.get(url)
            r.encoding = 'utf-8'
            if r.status_code != 200:
                logger.log('bad request:', r.status_code)
                logger.log('headers:', r.headers)
                print("unable to download google doc with id:", doc_id)
                print('status', r.status_code)
                return None
            return r.text

        text = v2()
        if filename is not None and text is not None and len(text) > 0:
            with open(filename, 'w') as fd:
                fd.write(text)
        else:
            logger.log("Unable to write file", filename)

        return text, n_time, False

    except Exception as e:
        print("unable to load notebook at", url, str(e))
        return None


def is_ipython(text):
    return text is not None and text.find('{"nbformat') == 0


def timestamp_to_str(t):
    dt = datetime.fromtimestamp(t)
    r = dt.strftime('%Y-%m-%d %H:%M:%S')
    return r
