
import json
import re

# TODO:  sanitize option
# allows to download python
# removes all ide.* code
# removes the install ide code too
#

'''
BETTER PARSER ???
only benefit is, you could remove the need to catch the
exceptions on loading the IDE/tester on the server side


IF you export ONLY functions (and constants)
then it would be safe to remove the exception handling
on IPython, etc.  May not be worth it 

better idea to hoist all scope0 code and place into a function
??

KEEP these (note they break the rules)
------------
1. CONSTANT = 3.5
2. apples = \    # crossing line boundaries
{ abc: 123 }

3. 1import xbb from abc
4. from xbb import abc
5. import x


what about 
SOME_CONSTANT = get_some_value()

sanitize 
  if line is ^def [A-Za-z_]+ OR ^class [A-Za-z_] 
     keep
  else if line starts with whitespace 
     keep  could be anything inside a function/class OR another function
  else
     # line begins with letter/digit/underscore (non whitespace)
     KEEP only if '=' is there
     allows for module level data to be kept
'''

def sanitize(code):
    code = code.strip()
    return code

def illegal_code(line):

    # bad_news = ['from google.colab', 'import google', 'import IPython', 'from IPython']
    bad_news = ['from google', 'import google', 'import IPython', 'from IPython']

    clean = line.lstrip()
    if len(clean) > 0 and clean[0] in ['!', '%', '<']:
        return True

    remove_me = False
    for b in bad_news:
        if clean.find(b) >= 0:
            remove_me = True
            break

    return remove_me

#
# assumes src/tf is in the path
#

# TODO: maybe: option to parse out individual functions
# BUT this is an issue if use external or internal helper functions
#

class Nop(object):

    def __init__(self, msg='no op'):
        self.msg = msg

    def nop(self, *args, **kw):
        return self.msg

    def __getattr__(self, _):
        return self.nop

try:
   from tf.utils.SandBox import SandBox
   logger = SandBox().get_logger()
except ImportError:
    print("logger not being used")
    logger = Nop()

from tf.notebook import SourceCleaner

class ParseValues(object):
    def __init__(self, code, user, timestamp):
        self.code = code
        self.user = user
        self.timestamp = timestamp

class NBParser(object):

    def __init__(self, options=[]):
        self.logger = logger

    def get_times(self, filename):
        with open(filename, 'r') as fd:
            text = fd.read()
            code, min_time, max_time, u = self.parse_code(text)
            return min_time, max_time

    def parse_code(self, text, as_is=False, remove_cell_if_all_magic=True):

        code = json.loads(text)

        if as_is is True and remove_cell_if_all_magic is True:
            self.logger.log("warning, is_is flag takes priority")

        # creation timestamp
        metadata = code['metadata']
        colab = metadata.get('colab', {})
        items = colab.get('provenance', [])

        min_time = 0
        if len(items) > 0:
            pass
            # use provenance time ??? hmmmmm
            #min_time = int(items[0].get('timestamp', 0))

        lines = []
        user = None
        max_time = min_time
        for cell in code['cells']:

            cell_code = []
            invalid_count = 0
            if cell['cell_type'] == 'code':
                meta = cell.get('metadata', {})
                info = meta.get('executionInfo', {})

                ts = int(info.get('timestamp', 0))
                tz = int(info.get('user_tz', 0))  # minutes off UTC
                milli = 0 # (tz * 60) * 1000
                ts = (ts - milli)/1000.0

                if ts != 0 and (ts < min_time or min_time == 0):
                    min_time = ts
                    # print('new min', ts)
                if ts > max_time:
                    max_time = ts
                    # print('new max', ts)

                user_info = info.get('user', None)
                if user is None and user_info is not None:
                    user = {'name': user_info['displayName'], 'id': user_info['userId']}

                for line in cell['source']:
                    if not as_is:
                        if illegal_code(line):
                            invalid_count += 1
                            line = SourceCleaner.comment_out(line)
                        else:
                            # we will use the original line as is
                            pass

                    # line could be empty
                    cell_code.append(line.rstrip())

                # option:  if a cell is mixed with magic and python
                '''
                !ls -la
                %% HTML 
                def build_object():
                   for r in words:
                      w = r.lower()
                   return FancyClass()
                helper = build_object()
                # we DO NOT what that entire cell 
                # to be discarded
                '''

                if remove_cell_if_all_magic:
                    if len(cell_code) == invalid_count:
                        cell_code = []

                lines.extend(cell_code)

        code = sanitize('\n'.join(lines))
        return code, min_time, max_time, user

    def parse_markdown(self, text):

        code = json.loads(text)

        text = []
        for cell in code['cells']:
            if cell['cell_type'] == 'markdown':
                for l in cell['source']:
                    line = l.strip()
                    if len(line) > 0:
                        text.append(line.strip())

        return "\n".join(text)
