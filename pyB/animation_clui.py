# -*- coding: utf-8 -*-
# console user-interface

def show_ui(env, mch, op_list):
    show_env(env)
    string = show_ops(op_list, env)
    print string


def show_env(env):
    bstate = env.state_space.get_state()
    print_state(bstate)
    


def __get_child_set_up_names(mch, done):
    lst = []
    if mch.name in done:
        return []
    done.append(mch.name)
    for m in mch.included_mch + mch.extended_mch + mch.seen_mch + mch.used_mch:
        lst += __get_child_set_up_names(m, done)
    const_names = mch.const_names
    set_names   = mch.dset_names + mch.eset_names
    para_names  = [n.idName for n in mch.scalar_params + mch.set_params]
    all_names   = const_names + set_names + para_names
    return lst + [(all_names, mch)] 
    
    
def print_set_up_bstates(bstates, root_mch):
    i=0
    set_up_names = __get_child_set_up_names(root_mch, [])
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
    
    
def __get_child_var_names(mch, done):
    lst = []
    if mch.name in done:
        return []
    done.append(mch.name)
    for m in mch.included_mch + mch.extended_mch + mch.seen_mch + mch.used_mch:
        lst += __get_child_var_names(m, done)
    return lst + [(mch.var_names, mch)] 


def print_init_bstates(bstates, root_mch, undo_possible):
    i=0
    var_lst = __get_child_var_names(root_mch, [])
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
