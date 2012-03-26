# -*- coding: utf-8 -*-

# console user-interface
def show_ui(env, mch):
    op_list = mch.find_possible_ops(env)
    show_env(env)
    string, num_of_ops = show_ops(op_list, env)
    print string
    return num_of_ops


def show_env(env):
    env.print_env()


def show_ops(op_list, env):
    i = 0
    string = "\n"
    for op in op_list:
        string += "["+ str(i) +"]: "
        if not op.return_Num==0:
            string += "("
            for r in range(op.return_Num):
                string +="r " #TODO:
            string += ") <-- "
        string += op.opName
        string += "("
        for p in range(op.parameter_Num):
            string +="p " #TODO:
        string += ")"
        i = i +1
        string += "\n"
    string += "["+ str(i) +"]: undo\n"
    string += "["+ str(i+1) +"]: leave pyB\n"
    return string, i+1