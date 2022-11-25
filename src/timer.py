
import time

def timed(function, flag=True):
    def wrapper(*args, **kwargs):
        before = time.time()
        return_value = function(*args, **kwargs)
        after = time.time()
        fname = function.__name__
        if flag:
            print(f"{fname} took {(after-before):.5f} seconds to execute!")
        return return_value
    return wrapper