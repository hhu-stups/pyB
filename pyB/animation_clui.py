# -*- coding: utf-8 -*-
# console user-interface

def show_ui(env, mch, op_list):
    show_env(env)
    string = show_ops(op_list, env)
    print string


def show_env(env):
    bstate = env.state_space.get_state()
    print_state(bstate)
    

def print_set_up_bstates(bstates, root_mch):
    i=0
    const_names = root_mch.const_names
    set_names   = root_mch.dset_names + root_mch.eset_names
    for bstate in bstates:
        string = "[%s]: SET_UP_CONSTANTS" % i
        if not const_names+set_names==[]:
            args = "("
            for name in const_names + set_names:
                value = print_values_b_style(bstate.get_value(name, root_mch))
                args += "%s=%s " % (name, value)            
            args += ")"
            string += args    
        print string
        i = i +1
    print "["+ str(i) +"]: leave pyB\n"
    

def print_init_bstates(bstates, root_mch, undo_possible):
    i=0
    var_names = root_mch.var_names
    for bstate in bstates:
        string = "[%s]: INITIALISATION" % i
        if not var_names==[]:
            args = "("
            for name in var_names:
                value = print_values_b_style(bstate.get_value(name, root_mch))
                args += "%s=%s " % (name, value)
            args += ")"
            string += args    
        print string
        i = i +1
    if undo_possible:
        print "["+ str(i) +"]: undo"
        i = i+1
    print "["+ str(i) +"]: leave pyB\n"
    

def print_state(bstate):
    for bmachine in bstate.bmch_dict:
        if not bmachine==None:
            bmachine.name
        value_stack = bstate.bmch_dict[bmachine]
        for value_map in value_stack:
            string = ""
            for name in value_map:
                string += name + "=" + print_values_b_style(value_map[name]) + " "
            print string


def show_ops(next_states, env):
    i = 0
    string = "\n"
    for entry in next_states:
        op_name = entry[0]
        string += "["+ str(i) +"]: "
        string += _print_ret_values(entry[2])
        string += op_name
        string += "("
        string += _print_para_values(entry[1])
        string += ")"
        i = i +1
        string += "\n"
    if not env.state_space.empty():
        string += "["+ str(i) +"]: undo\n"
        i = i +1
    string += "["+ str(i) +"]: leave pyB\n"
    return string


def _print_para_values(para_list):
    string = ""
    if not para_list:
        return ""
    for pair in para_list:
        string += pair[0]
        string += "="
        string += print_values_b_style(pair[1])
        string += " "
    return string


def _print_ret_values(ret_list):
    string = ""
    if not ret_list:
        return ""
    for pair in ret_list:
        string += pair[0]
        string += "="
        string += print_values_b_style(pair[1])
        string += " "
    string += " <-- "
    return string


# Prints frozensets like this: {a,b,c}
def print_values_b_style(value):
    if isinstance(value, frozenset):
        string = "{"
        value = list(value)
        for i in range(len(value)):
            entry = value[i]
            string += print_values_b_style(entry)
            if i < len(value)-1:
                string += ", "
        string += "}"
        return string
    return str(value)
