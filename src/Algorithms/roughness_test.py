import numpy as np

def variance_heat_map(vert_dict: dict, mean_fun_val: float, n: int):
    variance = {}

    for ind, vert in vert_dict.items():
        n_neighborhood = vert.get_n_neighborhood(vert_dict, n)
        fun_vals = []
        for elt in n_neighborhood:
            fun_vals.append(np.square(vert_dict[elt].fun_val-mean_fun_val))
        variance[ind] = np.sum(fun_vals)/len(fun_vals)

    return variance


def extremal_points_ratio(vert_dict: dict, extremal_points: set, n: int):
    ratio = {}

    for ind, vert in vert_dict.items():
        n_neighborhood = vert.get_n_neighborhood(vert_dict, n)
        ratio[ind] = len(n_neighborhood.intersection(extremal_points)) / len(n_neighborhood)

    return ratio

