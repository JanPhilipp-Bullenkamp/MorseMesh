
import time
def timed(flag: bool = True):
    def time_fct(function):
        def wrapper(*args, **kwargs):
            before = time.time()
            return_value = function(*args, **kwargs)
            after = time.time()
            fname = function.__name__
            if flag:
                print(f"{fname} took {(after-before):.5f} seconds to execute!")
            return return_value
        return wrapper
    return time_fct