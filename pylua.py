import cStringIO
import sys
import ast
import subprocess

lua_exe = r'c:\users\kevin\src\luajit-2.0\src\luajit.exe'

class PyLua(ast.NodeVisitor):
    def __init__(self):
        self.stream = cStringIO.StringIO()

    def visit(self, node):
        print node
        super(PyLua, self).visit(node)

    def visit_Print(self, node):
        self.emit('print(')
        self.generic_visit(node)
        self.emit(')')

    def visit_Num(self, node):
        self.emit(repr(node.n))

    def visit_Add(self, node):
        self.emit('+')

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

    print runjit(visitor.stream.getvalue())

def runjit(program):
    filename = 'temp.lua'
    open(filename, 'wb').write(program)

    args = [lua_exe, filename]
    process = subprocess.Popen(args, stdout = subprocess.PIPE)

    stdout, stderr = process.communicate()

    return stdout

if __name__ == '__main__':
    main()

