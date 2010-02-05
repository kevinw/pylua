import cStringIO
import sys
import ast
import subprocess

lua_exe = r'c:\users\kevin\src\luajit-2.0\src\luajit.exe'

class PyLua(ast.NodeVisitor):
    def __init__(self):
        self.stream = cStringIO.StringIO()
        self.indent = 0

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

    def visit_Return(self, node):
        self.emit('return ')
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        v = dict(body='foo')
        v.update(**vars(node))

        self.emit('\n')
        self.emit('%(name)s = function()\n' % v)

        self.push_scope()
        self.generic_visit(node)
        self.pop_scope()

        self.emit('\n')
        self.emit('end\n')

    def visit_Call(self, node):
        self.visit(node.func)
        self.emit('()')

    def visit_Name(self, node):
        self.emit(node.id)

    def push_scope(self):
        self.indent += 1

    def pop_scope(self):
        self.indent -= 1

    def emit(self, val):
        self.stream.write(val)

def main():
    filename = sys.argv[1]
    contents = open(filename, 'rU').read()
    if not contents.endswith('\n'):
        contents += '\n'

    tree = ast.parse(contents, filename)

    visitor = PyLua()
    visitor.visit(tree)

    lua_program = visitor.stream.getvalue()
    print ast.dump(tree, include_attributes=True)
    print '-'*80
    print lua_program
    print '-'*80
    print runjit(lua_program)

def runjit(program):
    filename = 'temp.lua'
    open(filename, 'wb').write(program)

    args = [lua_exe, filename]
    process = subprocess.Popen(args, stdout = subprocess.PIPE)

    stdout, stderr = process.communicate()

    return stdout

if __name__ == '__main__':
    main()

