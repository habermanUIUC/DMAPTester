
import json
import re

print_regex  = re.compile(r'^\s*print\(')
INDENT_REGEX = re.compile(r'^(\s*)[^\s]')
scope0_function_call = re.compile(r'^[a-z_][a-z0-9_]*\(', re.IGNORECASE)
# removing scope0 function calls may not be too useful
# r = some_dumb_fn()
# print(r)
# unless you comment out print first
# then do dead code elimination

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



class ParseValues(object):
    def __init__(self, code, user, timestamp):
        self.code = code
        self.user = user
        self.timestamp = timestamp


def comment_out(line):
    # respects the current indentation level
    clean = line.rstrip()
    m = INDENT_REGEX.match(clean)
    # print('found space', m.start(1), m.end(1))
    total = m.end(1) - m.start(1)
    new_line = " " * total + 'pass #' + line.lstrip()
    return new_line


def matches(line, options):
    if len(options) > 0:
        clean = line.rstrip()
        for regex in options:
            if regex.match(clean):
                #print('found pattern:', clean + ':')
                return True
    return False


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


class NBParser(object):

    def __init__(self, options=[]):
        self.logger = logger
        self.options = [print_regex, scope0_function_call]
        for o in options:
            self.options.append(o)

    def get_times(self, filename):
        with open(filename, 'r') as fd:
            text = fd.read()
            code, min_time, max_time, u = self.parse_code(text)
            return min_time, max_time

    def parse_code(self, text, as_is=False, remove_cell_if_has_magic=False):

        code = json.loads(text)

        if as_is is True and remove_cell_if_has_magic is True:
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
                        found = matches(line, self.options)
                        if found:
                            line = comment_out(line)
                        elif illegal_code(line):
                            if remove_cell_if_has_magic:
                                cell_code = []
                                break
                            else:
                                line = comment_out(line)
                        else:
                            # we will use the original line as is
                            pass

                    if len(line) > 0:
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

                # 1.  if the cell is all magic remove it
                lines.extend(cell_code)

        return '\n'.join(lines), min_time, max_time, user

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
