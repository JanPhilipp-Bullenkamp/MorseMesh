import numpy as np
import matplotlib.pyplot as plt
import timeit
from collections import Counter

def plot_fun_val_histogramm(vert_dict, nb_bins = 15, log=False, save = False, filepath = None):
    fun_vals = []
    for vert in vert_dict.values():
        fun_vals.append(vert.fun_val)
        
    plt.hist(fun_vals, bins=nb_bins, log=log)
    plt.xlabel("Function Value")
    plt.ylabel("Counts")
    plt.title("Function Value Histogram")
    if save == True:
        plt.savefig(filepath, dpi=600)
    plt.show()