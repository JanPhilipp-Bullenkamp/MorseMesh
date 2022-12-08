import numpy as np

def variance_heat_map(vert_dict, n=3):
    variance = {}

    for ind, vert in vert_dict.items():
        n_neighborhood = vert.get_n_neighborhood(vert_dict, n)
        fun_vals = []
        for elt in n_neighborhood:
            fun_vals.append(vert_dict[elt].fun_val)
        variance[ind] = np.std(fun_vals)

    return variance

