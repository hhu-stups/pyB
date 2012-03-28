# -*- coding: utf-8 -*-

# console user-interface
def show_ui(env, mch, op_and_state_list):
    show_env(env)
    string, num_of_ops = show_ops(op_and_state_list, env)
    print string
    return num_of_ops


def show_env(env):
    env.print_env()


def show_ops(op_list, env):
    i = 0
    string = "\n"
    for entry in op_list:
        op = entry[0]
        string += "["+ str(i) +"]: "
        string += str(entry[2])
        string += " <-- "
        string += op.opName
        string += str(entry[1])
        i = i +1
        string += "\n"
    string += "["+ str(i) +"]: undo\n"
    string += "["+ str(i+1) +"]: leave pyB\n"
    return string, i+1