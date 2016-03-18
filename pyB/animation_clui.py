from symbolic_sets import SymbolicSet
# -*- coding: utf-8 -*-
#
# module-description: 
# console user-interface
from config import USE_RPYTHON_CODE
if USE_RPYTHON_CODE:
     from rpython_b_objmodel import frozenset

# prints user-interface: state and options
def show_ui(env, mch, op_list):
    _show_env(env)
    string = show_ops(op_list, env)
    print string
    

# prints options at set up phase    
def print_set_up_bstates(bstates, root_mch):
    i=0
    set_up_names = _get_child_set_up_names(root_mch, [])
    for bstate in bstates:
        string = "[%s]: SET_UP_CONSTANTS" % i
        if not set_up_names==[]:
            args = "("
            for tup in set_up_names:
                name_lst = tup[0]
                owner    = tup[1]
                for name in name_lst:
                    value = print_values_b_style(bstate.get_value(name, owner))
                    args += "%s=%s " % (name, value)            
            args += ")"
            string += args    
        print string
        i = i +1
    print "["+ str(i) +"]: leave pyB\n"


# prints options at init phase 
def print_init_bstates(bstates, root_mch, undo_possible):
    i=0
    var_lst = _get_child_var_names(root_mch, [])
    for bstate in bstates:
        string = "[%s]: INITIALISATION" % i
        if not var_lst==[]:
            args = "("
            for tup in var_lst:
                var_names = tup[0]
                owner     = tup[1]
                for name in var_names:
                    value = print_values_b_style(bstate.get_value(name, owner))
                    args += "%s=%s " % (name, value)
            args += ")"
            string += args    
        print string
        i = i +1
    if undo_possible:
        print "["+ str(i) +"]: undo"
        i = i+1
    print "["+ str(i) +"]: leave pyB\n"


# prints enabled operations, undo and quit options
def show_ops(next_states, env):
    i = 0
    string = "\n"
    for entry in next_states:
        op_name = entry.opName
        string += "["+ str(i) +"]: "
        string += _print_ret_values(entry.return_names, entry.return_values)
        string += op_name
        string += "("
        string += _print_para_values(entry.parameter_names, entry.parameter_values)
        string += ")"
        i = i +1
        string += "\n"
    if not env.state_space.empty():
        string += "["+ str(i) +"]: undo\n"
        i = i +1
    string += "["+ str(i) +"]: leave pyB\n"
    return string


# prints frozensets (e.g. frozenset(["a","b","c"]) ) like this: {a,b,c}
def print_values_b_style(value):
    # TODO: check if finite
    if isinstance(value, SymbolicSet):
        value = value.enumerate_all()
    if isinstance(value, frozenset):
        string = "{"
        if USE_RPYTHON_CODE:
            value_list = value.lst
        else:
            value_list = list(value)
        for i in range(len(value_list)):
            entry = value_list[i]
            string += print_values_b_style(entry)
            if i < len(value_list)-1:
                string += ", "
        string += "}"
        return string
    if USE_RPYTHON_CODE:
        return value.__repr__()
    else:
        return repr(value)
    

# - private method -
# helper function, prints environment (machine-status)
def _show_env(env):
    bstate = env.state_space.get_state()
    _print_state(bstate)
    

# - private method -
# helper function, prints B state (values of variables)
def _print_state(bstate):
    for bmachine in bstate.bmch_dict:
        if not bmachine is None:
            print bmachine.mch_name
        value_stack = bstate.bmch_dict[bmachine]
        for value_map in value_stack:
            string = ""
            for name in value_map.keys():
                string += name + "=" + print_values_b_style(value_map[name]) + " "
            print string
            
            
# - private method -
# helper function, returns list of set and constant names of all machines
def _get_child_set_up_names(bmachine, done):
    lst = []
    if bmachine.mch_name in done:
        return []
    done.append(bmachine.mch_name)
    for m in bmachine.included_mch + bmachine.extended_mch + bmachine.seen_mch + bmachine.used_mch:
        lst += _get_child_set_up_names(m, done)
    const_names = bmachine.const_names
    set_names   = bmachine.dset_names + bmachine.eset_names
    para_names  = [n.idName for n in bmachine.scalar_params + bmachine.set_params]
    all_names   = const_names + set_names + para_names
    return lst + [(all_names, bmachine)] 


# - private method -
# helper function, returns list of variables of all machines    
def _get_child_var_names(bmachine, done):
    lst = []
    if bmachine.mch_name in done:
        return []
    done.append(bmachine.mch_name)
    for m in bmachine.included_mch + bmachine.extended_mch + bmachine.seen_mch + bmachine.used_mch:
        lst += _get_child_var_names(m, done)
    return lst + [(bmachine.var_names, bmachine)] 
    
    
# - private method -
# helper function, prints parameter values of operations
def _print_para_values(names, values):
    string = ""
    if not names:
        return ""
    for i in range(len(names)):
        string += names[i]
        string += "="
        string += print_values_b_style(values[i])
        string += " "
    return string


# - private method -
# helper function, prints return values of operations
def _print_ret_values(names, values):
    string = ""
    if not names:
        return ""
    for i in range(len(names)):
        string += names[i]
        string += "="
        string += print_values_b_style(values[i])
        string += " "
    string += " <-- "
    return string