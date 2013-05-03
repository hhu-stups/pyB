# -*- coding: utf-8 -*-
MIN_INT = -2**32	
MAX_INT = 2**32
MAX_OP_SOLUTIONS = 4    # negative = explore all!
MAX_NEXT_STATES  = 20   # not implemented yet
MAX_SELECT_BRANCHES = 4 # not implemented yet 
ENABLE_ASSERTIONS = True
DEFERRED_SET_ELEMENTS_NUM = 3
TO_MANY_ITEMS = 2*16    # sets with more items are handeld like infinite sets
DEFAULT_INPUT_FILENAME = "input.txt"
VERBOSE = False
# MIN_INT, MAX_INT are copied to env (environment.py) (for possible modification after module import time)