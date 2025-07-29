from datetime import datetime


def exec_time(func_arg):
    """
    Prints the execution time for a function
    :param func_arg:
    :return:
    """
    def inner_exec_time():
        dt1 = datetime.now()
        func_arg()
        dt2 = datetime.now()
        print(f"{func_arg.__name__} ran in {dt2 - dt1}")
    return inner_exec_time
