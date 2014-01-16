import time
from ast_nodes import *
from btypes import *
from environment import Environment
from interp import interpret
from util import arbitrary_init_machine
from helpers import file_to_AST_str, string_to_file

file_name = "input.txt"
#  maximum size of a python list on a 32 bit system is 536,870,912 elements

"""
0 : 0.000975 seconds. Itmes: 1
1 : 0.000113 seconds. Itmes: 2
2 : 0.00012 seconds. Itmes: 4
3 : 0.000115 seconds. Itmes: 8
4 : 0.000136 seconds. Itmes: 16
5 : 0.000147 seconds. Itmes: 32
6 : 0.000179 seconds. Itmes: 64
7 : 0.000355 seconds. Itmes: 128
8 : 0.000384 seconds. Itmes: 256
9 : 0.000843 seconds. Itmes: 512
10 : 0.003433 seconds. Itmes: 1024
11 : 0.003242 seconds. Itmes: 2048
12 : 0.007831 seconds. Itmes: 4096
13 : 0.01994 seconds. Itmes: 8192
14 : 0.045013 seconds. Itmes: 16384
15 : 0.127834 seconds. Itmes: 32768
16 : 0.270705 seconds. Itmes: 65536
17 : 0.827482 seconds. Itmes: 131072
18 : 2.215682 seconds. Itmes: 262144
19 : 7.781686 seconds. Itmes: 524288
"""
def test_performance_cart_prod():
	# Build AST:
	string = "#EXPRESSION S*T"
	string_to_file(string, file_name)
	ast_string = file_to_AST_str(file_name)
	exec ast_string
	print string 
	print "card(S) and card(T)"
	# Test
	for i in range(1):
	#for i in range(501):   
		env = Environment()
		env.add_ids_to_frame(["T","S"])
		env.set_value("S", frozenset(range(i)))
		env.set_value("T", frozenset(range(i)))
		t = time.clock()
		result = interpret(root.children[0],env)
		print i ,":", time.clock()-t,"seconds. Itmes:",len(result)  


"""
0 : 0.000986 seconds. Itmes: 1
1 : 0.000112 seconds. Itmes: 2
2 : 0.000119 seconds. Itmes: 4
3 : 0.000116 seconds. Itmes: 8
4 : 0.000153 seconds. Itmes: 16
5 : 0.000158 seconds. Itmes: 32
6 : 0.000192 seconds. Itmes: 64
7 : 0.000342 seconds. Itmes: 128
8 : 0.000364 seconds. Itmes: 256
9 : 0.000781 seconds. Itmes: 512
10 : 0.003389 seconds. Itmes: 1024
11 : 0.003229 seconds. Itmes: 2048
12 : 0.00804 seconds. Itmes: 4096
13 : 0.019807 seconds. Itmes: 8192
14 : 0.044683 seconds. Itmes: 16384
15 : 0.127603 seconds. Itmes: 32768
16 : 0.269252 seconds. Itmes: 65536
17 : 0.827626 seconds. Itmes: 131072
18 : 2.210819 seconds. Itmes: 262144
19 : 7.807196 seconds. Itmes: 524288
20 : 30.239897 seconds. Itmes: 1048576
21 : 117.759619 seconds. Itmes: 2097152
22 : 488.313926 seconds. Itmes: 4194304
"""
def test_performance_cart_prod():
	# Build AST:
	string = "#EXPRESSION POW(S)"
	string_to_file(string, file_name)
	ast_string = file_to_AST_str(file_name)
	exec ast_string
	print string 
	print "card(S)"
	# Test
	for i in range(1):
	#for i in range(22):   
		env = Environment()
		env.add_ids_to_frame(["T","S"])
		env.set_value("S", frozenset(range(i)))
		t = time.clock()
		result = interpret(root.children[0],env)
		print i ,":", time.clock()-t,"seconds. Itmes:",len(result)  

#test_performance_cart_prod()
test_performance_cart_prod()