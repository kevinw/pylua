import cStringIO
import sys
import os
import ast
import subprocess

lua_exe = '~/src/luajit-2.0/src/luajit'
lua_exe = os.path.normpath(os.path.expanduser(lua_exe))

# a modified version of the function from ast.py, with an optional "whitespace"
# argument
def dump(node, annotate_fields=True, include_attributes=False, whitespace=False):
    """
    Return a formatted dump of the tree in *node*.  This is mainly useful for
    debugging purposes.  The returned string will show the names and the values
    for fields.  This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    *include_attributes* can be set to True.
    """
    def _format(node, indent=0):
        sp = ('  ' * (indent+1)) if whitespace else ''
        nl = '\n' if whitespace else ''

        if isinstance(node, ast.AST):
            fields = [(a, _format(b, indent+1)) for a, b in ast.iter_fields(node)]
            rv = '%s(%s%s%s' % (node.__class__.__name__, nl, sp, ', '.join(
                ('%s=%s' % field for field in fields)
                if annotate_fields else
                (b for a, b in fields)
            ))
            if include_attributes and node._attributes:
                rv += fields and ', ' or ' '
                rv += ', '.join('%s=%s' % (a, _format(getattr(node, a), indent+1))
                                for a in node._attributes)
            return rv + ')'
        elif isinstance(node, list):
            return '[%s%s%s]' % (nl, sp, ', '.join(_format(x, indent+1) for x in node))
        return repr(node)
    if not isinstance(node, ast.AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _format(node)

class PyLua(ast.NodeVisitor):
    def __init__(self):
        self.stream = cStringIO.StringIO()
        self.indent = 0

    def visit_all(self, nodes):
        for node in nodes:
            self.visit(node)

    def visit(self, node):
        super(PyLua, self).visit(node)

    def visit_Print(self, node):
        self.emit('print(')
        self.generic_visit(node)
        self.emit(')')

    def visit_Num(self, node):
        self.emit(repr(node.n))

    def visit_Add(self, node):
        self.emit('+')

    def visit_Mult(self, node):
        self.emit('*')

    def visit_Div(self, node):
        self.emit('/')

    def visit_Sub(self, node):
        self.emit('-')

    def visit_Return(self, node):
        self.emit('return ')
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        v = dict(body='foo')
        v.update(**vars(node))

        self.emit('\n')
        self.emit('%(name)s = function(' % v)
        self.visit(node.args)
        self.emit(')\n')

        self.push_scope()
        self.visit_all(node.body)
        self.pop_scope()

        self.emit('\n')
        self.emit('end\n')

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Pow):
            self.emit('math.pow(')
            self.visit(node.left)
            self.emit(', ')
            self.visit(node.right)
            self.emit(')')
        else:
            self.visit(node.left)
            self.visit(node.op)
            self.visit(node.right)

    def visit_IfExp(self, node):
        self.visit(node.test)
        self.emit(' and ')
        self.visit(node.body)
        self.emit(' or ')
        self.visit(node.orelse)

    def visit_Call(self, node):
        self.visit(node.func)
        self.emit('(')
        self.visit_all(node.args)
        self.emit(')')

    def visit_Compare(self, node):
        self.visit(node.left)
        self.visit_all(node.ops)
        self.visit_all(node.comparators)

    def visit_Eq(self, node):
        self.emit('==')

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.emit('[')
        if isinstance(node.slice, ast.Index):
            if isinstance(node.slice.value, ast.Num):
                self.emit('%d' % (node.slice.value.n + 1))
            else:
                self.visit(node.slice)
        self.emit(']')


    def visit_Tuple(self, node):
        self.emit('{')
        for el in node.elts:
            self.visit(el)
            self.emit(', ')
        self.emit('}')

    def visit_Name(self, node):
        self.emit(node.id)

    def push_scope(self):
        self.indent += 1

    def pop_scope(self):
        self.indent -= 1

    def emit(self, val):
        self.stream.write(val)

_dump_ast=dump
def run_file(filename, dump=False):
    contents = open(filename, 'rU').read()
    if not contents.endswith('\n'):
        contents += '\n'

    tree = ast.parse(contents, filename)

    visitor = PyLua()
    visitor.visit(tree)

    lua_program = visitor.stream.getvalue()
    if dump:
        print _dump_ast(tree, include_attributes=True, whitespace=True)
        print '-'*80
        print lua_program
        print '-'*80
    else:
        return runjit(lua_program)

def main():
    filename = sys.argv[1]
    print run_file(filename)

def runjit(program):
    filename = '_pylua_temp.lua'
    open(filename, 'wb').write(program)
    try:
        args = [lua_exe, filename]
        process = subprocess.Popen(args, stdout = subprocess.PIPE)
        stdout, stderr = process.communicate()
    finally:
        os.remove(filename)

    return stdout

if __name__ == '__main__':
    main()

