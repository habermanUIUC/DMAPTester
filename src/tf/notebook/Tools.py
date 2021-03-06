'''

# This module allows for testing colab code
# while debugging and testing, need to reload the module
import importlib
importlib.reload(Tools)

from info490.src.utils import Tools as helper
print(dir(tester))

if the notebook was already started,
THEN the notebook timestamps could be earlier than the mount_time
however, it is unknown if the notebook timestamps persist across google sessions
'''


import requests
import os
from datetime import datetime
#
# assumes src is in the path
#
from tf.utils import Client, ToolBox
from tf.utils.SandBox import SandBox
from tf.notebook import Parser, SourceCleaner

import json

'''
#
# it's important that this fails on the test/server side
# so Nop is used when the solution.py is run directly
#
def install_testing_framework(lesson_id, notebook_id):
    import sys
    sys.path.append('info490/src/')
    class Nop(object):
        def __init__(self, e): self.e = e
        def nop(self, *args, **kw): return("unable to test:" + self.e, None)
        def __getattr__(self, _): return self.nop
    try:
        from tf.notebook import Tools
        from tf.notebook import Parser
        from tf.utils import Client
        
        import importlib
        from tf.utils import ToolBox
        importlib.reload(Parser)
        importlib.reload(Tools)
        importlib.reload(Client)
        importlib.reload(ToolBox)
        
        return Tools.TestFramework(lesson_id, notebook_id)
    except ImportError as e:
        #import traceback
        #traceback.print_exc()
        #happens on the test side, or if code never mounted
        return Nop(str(e))

tester = install_testing_framework(LESSON_ID, NOTEBOOK_ID)
tester.hello_world()


def install_testing_framework(lesson_id, notebook_id):
    class Nop(object):
        def __init__(self, e): self.e = e
        def nop(self, *args, **kw): return("unable to test:" + self.e, None)
        def __getattr__(self, _): return self.nop
    try:
        from tf.notebook import Tools
        from tf.notebook import Parser
        from tf.utils import Client
        import importlib
        importlib.reload(Parser)
        importlib.reload(Tools)
        importlib.reload(Client)
        ide = Tools.TestFramework(lesson_id, notebook_id)
        reader = Tools.AssetReader(lesson_id)
        return (ide, reader)
    except ImportError as e:
        #import traceback
        #traceback.print_exc()
        # happens on the test side, or if code never mounted
        return Nop(str(e)), None
tester, reader = install_testing_framework(LESSON_ID, NOTEBOOK_ID)
tester.hello_world()

'''

# TODO:
#  ColabTestFramework a subclass
#  JupyterTestFramework a subclass
#  ReplitTestFramework a subclass
#  CliTestFramework a subclass




class TestFramework(object):

    JSON_FILE    = '{:s}/solution.json'.format(SandBox().get_sandbox_dir())
    PYTHON_FILE = '{:s}/solution.py'.format(SandBox().get_sandbox_dir())
    TMP_PYTHON_FILE = '{:s}/tmp.py'.format(SandBox().get_sandbox_dir())
    ERROR_MSG = "Make notebook viewable"

    def __init__(self, lesson_id, notebook_id, client=None):

        if client is None:
            client = Client.ClientTest(lesson_id, notebook_id)
        else:
            print('TestFramework using custom client')

        self.logger = SandBox().get_logger()
        self.client = client
        self.parser = Parser.NBParser()

        text, m_time, is_cache = ToolBox.install_gd_file(notebook_id, filename=TestFramework.JSON_FILE)
        if not ToolBox.is_ipython(text):
            print(TestFramework.ERROR_MSG)
            raise IOError(TestFramework.ERROR_MSG)

        # parse sets the meta data, do before anything else
        self.parse_code(text)
        self.lesson_id = lesson_id
        self.nb_id = notebook_id

    def parse_code(self, text, as_is=False):
        try:
            py_code, min_ts, max_ts, user = self.parser.parse_code(text, as_is=as_is)
            self.client.get_meta().update(min_ts, max_ts, user)
            return py_code, min_ts, max_ts, user
        except Exception as e:
            self.logger.log('ERROR on parse', e)
            print('code was unable to be parsed: ask for help')
            return '', 0, 0, ''

    def write_file(self, as_is=False):
        """
           Downloads the ipython file
           parses the ipython file
           writes the ipython file to .py file
        """

        ipy_fn = TestFramework.JSON_FILE
        py_fn  = TestFramework.PYTHON_FILE

        # download the notebook (it's a json file) if it's readable
        nb_id = self.client.get_meta().notebook_id
        text, m_time, is_cache = ToolBox.install_gd_file(nb_id, filename=ipy_fn)
        if not ToolBox.is_ipython(text):
            print(TestFramework.ERROR_MSG)
            raise Exception(TestFramework.ERROR_MSG)

        # convert the code from .ipynb to .py
        # a tuple of values
        results = self.parse_code(text, as_is=as_is)
        code = results[0]

        self.logger.log('before parsing', TestFramework.TMP_PYTHON_FILE)
        with open(TestFramework.TMP_PYTHON_FILE, 'w') as fd:
            fd.write(code)

        # clean the code (remove comments, superfluous calls)
        if not as_is:
            cleaner = SourceCleaner.CodeCleaner()
            code = cleaner.clean(code)

        self.logger.log('creating', py_fn)
        with open(py_fn, 'w') as fd:
            fd.write(code)
        return py_fn

    #
    # PUBLIC API
    #

    def hello_world(self):

        min_ts = self.client.get_meta().min_time
        max_ts = self.client.get_meta().max_time

        min_dt = datetime.fromtimestamp(min_ts)
        max_dt = datetime.fromtimestamp(max_ts)

        hrs = (max_dt - min_dt).total_seconds()/(60.0*60.0)
        min_s = ToolBox.timestamp_to_str(min_ts)
        max_s = ToolBox.timestamp_to_str(max_ts)

        if self.client.is_notebook:
            print("Hello! (notebook)")
        else:
            print("Hello!")
        print("{:s}\n{:s} ({:f})".format(min_s, max_s, hrs))

    def is_notebook_valid_python(self):
        filename = self.write_file(as_is=True)
        e, r = self.client.test_file(filename, syntax_only=True)
        return e is None, e

    def clean_notebook_for_download(self):
        # remove magic cells
        # will remove the entire download_notebook cell
        # since it using google.files (see parser)
        filename = self.write_file(as_is=False)
        e, r = self.client.test_file(filename, syntax_only=True)
        if e is None:
            return True, filename
        else:
            return False, e

    def list_tests(self):
        e, r = self.client.get_tests()
        if e is None:
            print(r)
        else:
            print('Error', e)
        return None

    def test_notebook(self, verbose=False, as_is=False, max_score=100):
        filename = self.write_file(as_is=False)
        e, r = self.client.test_file(filename)

        if e is not None:
            return "ERROR: {:s}".format(str(e))

        if as_is:
            return e, r

        score = int(float(r.get('score', 0)))
        score_msg = "Score {:d}/{:d}\n".format(score, max_score)
        if not verbose:
            return score_msg

        # verbose output
        buffer = [score_msg]
        for t in r.get('tests', []):
            name = t.get('name', 'n/a')
            score = t.get('score', 0)
            max_score = t.get('max_score', 0)
            output = t.get('output', '').strip()
            buffer.append("{} {}/{}\n{}".format(name, score, max_score, output))

        return "\n".join(buffer)

    def test_function(self, fn, verbose=True):

        assert fn is not None, "fn is None"

        what = "your code"
        if callable(fn):
            fn = fn.__name__
            what = fn

        filename = self.write_file(as_is=False)
        error, msg = self.client.test_function(filename, fn)

        if verbose:
            # if it's verbose, just return a single string
            # to make for easy printing
            warning = "If you change " + what + ", SAVE the notebook (⌘/Ctrl s) before retesting"
            if error is not None:
                return "Tested: {:s}\nError: {:s}\n{:s}".format(fn, str(error), warning)
            else:
                score, max_score, msg = msg.split(':', maxsplit=2)
                try:
                    score = int(float(score))         # could be 0.0 (gradescope default)
                    max_score = int(float(max_score))
                    if score == max_score:
                        warning = ''
                except Exception as e:
                    self.logger.log('ERROR on verbose', e)

                return "Tested: {:s}\nScore: {:d}\nMax Score: {:d}\nOutput: {:s}\n{:s}".format(fn, score, max_score, msg, warning)

        return error, msg

    def test_with_button(self, fn):

        if not self.client.is_notebook:
            return 'unable to test with gui on server side'

        if callable(fn):
            fn = fn.__name__

        try:
            import ipywidgets as widgets
            from IPython.display import display, clear_output

            button = widgets.Button(description="Test " + fn)
            output = widgets.Output()

            def on_button_clicked(input):
                error, msg = self.test_function(fn, verbose=False)
                # print("Button clicked.", fn, input)
                # Display the message within the output widget.
                with output:
                    clear_output()  # also removes the button if put before output
                    print_warning = True

                    if error is None:
                        score, max_score, msg = msg.split(':', maxsplit=2)
                        score = int(float(score))  # floats (e.g 0.0) are possible
                        max_score = int(float(max_score))

                        if msg.find('no tests') >= 0:
                            button.style = widgets.ButtonStyle(button_color='yellow')
                            button.description = 'No Tests'
                        elif score > 0 and score == max_score:
                            button.style = widgets.ButtonStyle(button_color='green')
                            button.description = 'Pass!'
                            print_warning = False
                        elif score > 0:
                            button.style = widgets.ButtonStyle(button_color='yellow')
                            button.description = 'More Work'
                        else:
                            button.style = widgets.ButtonStyle(button_color='red')
                            button.description = 'Fail'
                    else:
                        msg = ''
                        button.style = widgets.ButtonStyle(button_color='red')
                        button.description = 'FAIL: {}'.format(fn)
                        print("Error:", error)

                    if print_warning:
                        print(msg)
                        print("If you change", fn + ", SAVE the notebook (⌘/Ctrl s) before retesting")

                    # since the button text changes
                    # disabling the button, makes sense
                    # otherwise, it's not clear that the user COULD press it again
                    # this way it forces the user to reload the cell
                    button.disabled = True

            button.on_click(on_button_clicked)
            display(button, output)

        except ImportError as e:
            return 'unable to test with gui: ', str(e)

    def download_solution(self):
        valid, file_or_error = self.clean_notebook_for_download()
        if valid:
            print("solution.py contains valid python; it will be downloaded")
            try:
                from google.colab import files
                files.download(file_or_error)
            except ImportError:
                # server side
                pass
        else:
            print("solution.py contains invalid python")
            print("FIX the following Errors")
            print("You can tag questions on Piazza with", "{}".format(self.lesson_id))
            print(file_or_error)

    def test_functionality(self, fn, verbose=True):
        return self.test_function(fn, verbose=verbose)

#
# assumes this file Tools.py is already installed via install_file
#

'''
in a notebook to install a single file that's on a google drive:
TOOL_ID = '1JaBOzRUM3pgbYVFpU640SjxCjH7SH98N'   # keep this: google id of Tools.py
install_file(TOOL_ID, 'Tool.py', True)
'''
