# -*- coding: utf-8 -*-

# console user-interface
def show_ui(env, mch, op_list):
    show_env(env)
    string, num_of_ops = show_ops(op_list, env)
    print string
    return num_of_ops


def show_env(env):
    bstate = env.state_space.get_state()
    print_state(bstate)


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


def show_ops(op_list, env):
    i = 0
    string = "\n"
    for entry in op_list:
        op = entry[0]
        string += "["+ str(i) +"]: "
        string += _print_ret_values(entry[3])
        string += op.opName
        string += "("
        string += _print_para_values(entry[1])
        string += ")"
        i = i +1
        string += "\n"
    string += "["+ str(i) +"]: undo\n"
    string += "["+ str(i+1) +"]: leave pyB\n"
    return string, i+1


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
