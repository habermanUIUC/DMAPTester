
import os
import json
import requests

from tf.utils.SandBox import SandBox
import tf.utils.ZipLib as ZipLib

try:
    VERSION = '06.20.2020'

    SERVER = 'http://localhost:8080'
    SERVER = 'http://75.156.71.78:8080'    # MEH
    SERVER = 'http://18.219.123.225:8080'  # AWS v1
    SERVER = 'http://13.59.43.215:8080'    # AWS v2
    SERVER = 'http://18.222.172.177:8080'  # AWS ec3


    import ipywidgets as widgets
    from IPython.display import display
    is_notebook = True
except ImportError as e:
    is_notebook = False


class MetaData(object):

    def __init__(self, lesson_id, notebook_id):

        self.lesson_id = lesson_id
        self.notebook_id = notebook_id

        self.u_id   = '0'
        self.u_name = 'na'
        self.min_time = 0
        self.max_time = 0

    def update(self, min_time, max_time, user=None):

        if self.min_time == 0 or min_time < self.min_time:
            self.min_time = min_time

        if self.max_time == 0 or max_time > self.max_time:
            self.max_time = max_time

        if user is not None:
            self.u_id   = user['id']
            self.u_name = user['name']

    def kv(self):

        result = {
            'lesson_id': self.lesson_id,
            'notebook_id': self.notebook_id,
            'min_time': self.min_time,
            'max_time': self.max_time,
            'u_id': self.u_id,
            'u_name': self.u_name,
        }

        return result


class ClientTest(object):

    def __init__(self, lesson_id, notebook_id=0, server=None):

        assert lesson_id is not None, "bad lesson id"
        assert notebook_id is not None, "bad notebook id"

        meta = MetaData(lesson_id, notebook_id)

        if server is None:
            server = SERVER

        self.server       = server
        self.is_notebook  = is_notebook
        self.meta = meta

        self.logger = SandBox().get_logger()

        self.logger.log("client version:", VERSION)
        self.logger.log("running in notebook:", is_notebook is False)
        self.logger.log("server:", server)
        self.logger.log("data:", lesson_id, notebook_id)


    def get_meta(self):
        return self.meta

    def _register_session(self):

        did_create, m_time = SandBox().get_session_information()
        if not did_create:
            self.logger.log('skip register')
            return

        self.logger.log("session created", m_time)

        end_point = "{:s}/register".format(self.server)
        post_data = {"notebook_id": self.meta.notebook_id,
                     "lesson_id": self.meta.lesson_id,
                     "u_id": self.meta.u_id,
                     "u_name": self.meta.u_name,
                     "mount_time": m_time}

        response = requests.post(end_point, data=post_data)
        if response.status_code != 200:
            self.logger.log('session did not register', response.status_code)
        else:
            self.logger.log('register session at', m_time)

        return None

    def get_tests(self):
        end_point = "{:s}/list".format(self.server)
        post_data = {"lesson_id": self.meta.lesson_id,
                     "u_id": self.meta.u_id,
                     "u_name": self.meta.u_name}

        response = requests.post(end_point, data=post_data)
        error = None
        data = None
        if response.status_code != 200:
            error = str(response.status_code)
            self.logger.log('unable to list', error)
        else:
            r_data = response.json()  # json.loads(r.text)
            error = r_data['error_code']
            if error is None:
                data = r_data['payload']

        return error, data

    def send_zip(self, zipfile, extra_kv={}):

        try:
            self._register_session()
        except Exception as e:
            #except (ConnectionError, ConnectionRefusedError) as e:
            self.logger.log('ERROR (is server running?)', str(e))
            msg = {'error_code': 'Unable to connect to server'}
            return msg

        end_point = "{:s}/testzip".format(self.server)
        # add in the meta data (notebook, assignment, etc)
        post_data = extra_kv
        kv = self.meta.kv()
        for k in kv:
            v = kv[k]
            # self.logger.log('adding', k, v, ' TO ', post_data)
            if isinstance(v, dict):
                v = json.dumps(kv[k])
            post_data[k] = v

        self.logger.log('sending to test')
        filename = os.path.basename(zipfile)
        with open(zipfile, 'rb') as fd:
            response = requests.post(end_point, data=post_data,
                                     files={"archive": (filename, fd)})

            data = {'error_code': None, 'payload': {}}
            if response.status_code == 200:
                data = response.json()  # json.loads(r.text)
            else:
                data['error_code'] = response.status_code

            return data
    #
    # all tests must return TWO values (so NoOp will always work)
    #
    def test_file(self, filename, fn_name=None, syntax_only=False):
        import os

        extra_kv = {"syntax_only": syntax_only,
                    "fn": fn_name}

        zip_file = ZipLib.create_zipfile(filename, SandBox().get_sandbox_dir())
        # print('ZIP', zip_file, os.getcwd())

        response = self.send_zip(zip_file, extra_kv=extra_kv)
        self.logger.log(response)

        error = response['error_code']
        if error is None:
            payload = response['payload']
            result  = payload['test_result']

            if result['score'] != 100:
                # this gives some info back
                self.logger.log(json.dumps(result))
            return None, result
        else:
            return error, None

    def test_function(self, filename, fn_name):
        error, result = self.test_file(filename, fn_name)
        if error is None:
            message = "0:0:no tests for " + fn_name
            # it's possible that the test matched a few possibilities
            # so search for the exact match
            for t in result['tests']:
                if t['name'] == fn_name:
                    score = t.get('score', 0)
                    max_score = t.get('max_score', 100)
                    output = t.get('output', "")
                    if score == max_score:
                        output = "Passed " + output
                    else:
                        output = "Incomplete " + output
                    message = "{}:{}:{}".format(score, max_score, output.strip())
                    break
            return None, message
        else:
            return error, "0:0:NA"

