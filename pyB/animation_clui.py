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
                string += name + ":" + str(value_map[name]) + " "
            print string


def show_ops(op_list, env):
    i = 0
    string = "\n"
    for entry in op_list:
        op = entry[0]
        string += "["+ str(i) +"]: "
        #string += str(entry[2])
        #string += " <-- "
        string += op.opName
        string += str(entry[1])
        i = i +1
        string += "\n"
    string += "["+ str(i) +"]: undo\n"
    string += "["+ str(i+1) +"]: leave pyB\n"
    return string, i+1