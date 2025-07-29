def make_dict_path(a_dict, a_path):
    set_dict_path(a_dict, a_path, {})


def set_dict_path(a_dict, a_path, a_val):
    curr_obj = a_dict
    path_len = len(a_path)
    counter = 0
    for iter_attr in a_path:
        counter += 1
        if counter == path_len:
            curr_obj[iter_attr] = a_val
        if not iter_attr in curr_obj:
            curr_obj[iter_attr] = {}
        curr_obj = curr_obj[iter_attr]


