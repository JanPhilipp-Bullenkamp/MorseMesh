import numpy as np

def compute_gradient(vert_dict, V12):
    gradient = {}

    for ind, vert in vert_dict.items():
        gradient[ind] = np.abs(vert.fun_val - )