import pylua
import sys
import subprocess
import os.path

tests_dir = os.path.join(os.path.dirname(__file__), 'tests')

def find_tests(path):
    for f in os.listdir(path):
        if f.endswith('.py') and f != '__init__.py':
            yield os.path.join(path, f)

def compare(n1, n2, output, expected):
    if output.strip() != expected.strip():
        print 'ERROR: %s output does not match %s output' % (n1, n2)
        print 'output:'
        print '-'*80
        print output
        print

        print 'expected:'
        print '-'*80
        print expected
        return False

    return True

def main():
    for test in find_tests(tests_dir):
        # run python first
        print test,'...',

        output = runpy(test)

        expected = open(test + '.expected').read()

        if not compare('python', 'expected', output, expected):
            sys.exit(-1)

        lua_output = pylua.run_file(test)
        if not compare('lua', 'expected', lua_output, expected):
            print
            pylua.run_file(test, dump=True)
            sys.exit(-1)

        print 'OK'

def runpy(filename):
    proc = subprocess.Popen([sys.executable, filename], stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return stdout


if __name__ == '__main__':
    main()
