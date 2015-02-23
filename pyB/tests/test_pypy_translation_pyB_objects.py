# assumes pypy checkout at PYPYDIR
file_name = "input.txt"
PYPY_DIR  = "/Users/johnwitulski/witulski/git/pyB/pypy/" # change this line to your checkout


def translate_and_compare(code):
	# 1. Generate Python code as String
	code += "def target(*args):\n"
	code += " 	return main, None # returns the entry point\n"
	code += "\n"
	code += "if __name__ == '__main__':\n"
	code += "	import sys\n"
	code += "	main(sys.argv)\n"
	# 2. write to temp file
	f = open("temp.py",'w')
	f.write(code)
	f.close()
	from subprocess import Popen, PIPE
	# 3. call python version
	python_result = Popen("python temp.py", shell=True, stdout=PIPE).stdout.read()
	# 4. generate and call c Version
	pwd = Popen("pwd", shell=True, stdout=PIPE).stdout.read()
	assert pwd[-4:]=='pyB\n'
	Popen("PYTHONPATH="+PYPY_DIR+":. python ../pypy/rpython/translator/goal/translate.py temp.py", shell=True, stdout=PIPE).stdout.read()
	c_result = Popen("./temp-c", shell=True, stdout=PIPE).stdout.read()
	# 5. delete temp. file
	import os
	os.remove("temp.py")
	os.remove("temp-c")
	# 6. compare c and python result
	return python_result==c_result


class TestPyPyTranslationObjects():
    def test_pypy_genAST_expr_number(self):
        code =  "def main(argv):\n"
        code += "    from ast_nodes import AIntegerExpression\n"
        code += "    node = AIntegerExpression(41)\n"
        code += "    print node.intValue\n"
        code += "    return 0\n"
        assert translate_and_compare(code)