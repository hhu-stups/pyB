# -*- coding: utf-8 -*-
MIN_INT = -1
MAX_INT = 5
MAX_OP_SOLUTIONS = 4    # not implemented yet
MAX_NEXT_STATES  = 20   # not implemented yet
MAX_SELECT_BRANCHES = 4 # not implemented yet 
ENABLE_ASSERTIONS = True
DEFERRED_SET_ELEMENTS_NUM = 3
SET_PARAMETER_NUM = 3   # default machine-parameter init: 3 elements 
TO_MANY_ITEMS = 2*16    # sets with more items are handeld like infinite sets
MAX_INIT      = 6       # Max number of 'initialisations' computed (see ProB)
MAX_SET_UP    = 6       # Max number of 'set up constants' computed (see ProB)
DEFAULT_INPUT_FILENAME = "input.txt"
VERBOSE = True
PRINT_WARNINGS = True   # prints deadlock warning and wrong substitution-warnings (e.g. while in abstract machine)
BMACHINE_SEARCH_DIR = "examples/"
BFILE_EXTENSION = ".mch"
# MIN_INT, MAX_INT are copied to env (environment.py) (for possible modification after module import time)