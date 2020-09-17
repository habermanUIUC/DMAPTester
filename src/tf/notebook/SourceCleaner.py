
import ast
import astunparse
import re


# print calls don't need to be run
print_regex  = re.compile(r'^\s*print\s*\(')
INDENT_REGEX = re.compile(r'^(\s*)[^\s]')

# function calls never assigned to a value
# allow ide.tester.some_function()
scope0_function_call = re.compile(r'^[a-z_][.a-z0-9_]*\s*\(', re.IGNORECASE)
# removing scope0 function calls may not be too useful
# r = some_dumb_fn()
# print(r)
# unless you comment out print first
# then do dead code elimination

def comment_out(line):
    # respects the current indentation level
    clean = line.rstrip()
    m = INDENT_REGEX.match(clean)
    # print('found space', m.start(1), m.end(1))
    total = m.end(1) - m.start(1)
    new_line = " " * total + 'pass #' + line.lstrip()
    return new_line


def single_line_matches(line, options):
    if len(options) > 0:
        clean = line.rstrip()
        for regex in options:
            if regex.match(clean):
                #print('found pattern:', clean + ':')
                return True
    return False


class CodeCleaner(object):

    def __init__(self):
        self.do_match = [print_regex, scope0_function_call]

    def clean(self, code):

        # an ast parse tree, followed by an unparse:
        #    * normalize all function calls that span multiple lines, into a single line
        #    * remove comments
        #    * note dictionary will still span lines

        # does the full AST parse, and unparse
        # unparse 1.6.3 keeps dictionaries as a single line
        cleaner = IDECodeReplacer()
        code = cleaner.replace_function(code)
        lines = code.split("\n")

        # before we did function cleaning
        # tree = ast.parse(code)
        # lines = astunparse.unparse(tree).split("\n")

        clean = []
        for line in lines:
            found = single_line_matches(line, self.do_match)
            if found:
                line = comment_out(line)
            clean.append(line)
        return '\n'.join(clean)


class FunctionReplacer(ast.NodeTransformer):
    def __init__(self, function_name, new_node):
        self.node = new_node
        self.function_name = function_name

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.function_name:
            return self.node
        return node


class FunctionFinder(ast.NodeVisitor):
    def __init__(self, name):
        self.node = None
        self.function_name = name

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.function_name:
            self.node = node

        # this call is not needed, since we are done visiting
        # self.generic_visit(node)


class IDECodeReplacer(object):

    def __init__(self):

        self.node = None
        self.replace =\
'''
def install_ide(lesson_id, nb_id, reload=True):
    class Nop(object):
        def __init__(self, e): self.e = e
        def nop(self, *args, **kw): return ("unable to test:" + self.e, None)
        def __getattr__(self, _): return self.nop
    class IDE():
        tester = Nop("")
        reader = Nop("")
    return IDE()
'''
        self.function_name = 'install_ide'
        tree = ast.parse(self.replace)
        finder = FunctionFinder(self.function_name)
        finder.visit(tree)
        self.node = finder.node

    def replace_function(self, code):

        if self.node is None:
            print('unable to transform')
            return code

        tree = ast.parse(code)
        cleaner = FunctionReplacer(self.function_name, self.node)
        clean = cleaner.visit(tree)
        return astunparse.unparse(clean)
