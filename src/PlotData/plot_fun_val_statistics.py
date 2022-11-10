import numpy as np
import matplotlib.pyplot as plt
import timeit
from collections import Counter

def plot_fun_val_histogramm(vert_dict, nb_bins = 15, log=False, save = False, filepath = None, show = True):
    fun_vals = []
    for vert in vert_dict.values():
        fun_vals.append(vert.fun_val)
        
    plt.hist(fun_vals, bins=nb_bins, log=log)
    plt.xlabel("Function Value")
    plt.ylabel("Counts")
    plt.title("Function Value Histogram")
    if save == True:
        plt.savefig(filepath, dpi=600)
    if show:
        plt.show()
    
    stat = {}
    stat['mean'] = sum(fun_vals)/len(fun_vals)
    stat['std'] = np.sqrt( np.square(sum(fun_vals - stat['mean'])) / len(fun_vals) )
    stat['fun_vals'] = fun_vals
    return stat

def plot_critical_fun_val_histogramm(MSComplex, nb_bins = 15, log=False, save = False, filepath = None, show = True):
    fun_vals_CritV = []
    for vert in MSComplex.CritVertices.values():
        fun_vals_CritV.append(vert.fun_val)
    fun_vals_CritE = []
    for edge in MSComplex.CritEdges.values():
        for fun_val in edge.fun_val:
            fun_vals_CritE.append(fun_val)
    fun_vals_CritF = []
    for face in MSComplex.CritFaces.values():
        for fun_val in face.fun_val:
            fun_vals_CritF.append(fun_val)
        
    # plot Crit Vertices histogram
    plt.hist(fun_vals_CritV, bins=nb_bins, log=log)
    plt.xlabel("Function Value")
    plt.ylabel("Counts")
    plt.title("Critical Vertices Function Value Histogram")
    if save == True:
        plt.savefig(filepath + 'critV', dpi=600)
    if show:
        plt.show()

    # plot crit edges histogram
    plt.hist(fun_vals_CritE, bins=nb_bins, log=log)
    plt.xlabel("Function Value")
    plt.ylabel("Counts")
    plt.title("Critical Edges Function Value Histogram")
    if save == True:
        plt.savefig(filepath + 'critE', dpi=600)
    if show:
        plt.show()
    
    # plot crit faces histogram
    plt.hist(fun_vals_CritF, bins=nb_bins, log=log)
    plt.xlabel("Function Value")
    plt.ylabel("Counts")
    plt.title("Critical Faces Function Value Histogram")
    if save == True:
        plt.savefig(filepath + 'critF', dpi=600)
    if show:
        plt.show()

       
    stat = {}
    stat['V'] = {}
    stat['E'] = {}
    stat['F'] = {}
    
    stat['V']['mean'] = sum(fun_vals_CritV)/len(fun_vals_CritV)
    stat['V']['std'] = np.sqrt( np.square(sum(fun_vals_CritV - stat['V']['mean'])) / len(fun_vals_CritV) )
    stat['V']['fun_vals'] = fun_vals_CritV
    
    stat['E']['mean'] = sum(fun_vals_CritE)/len(fun_vals_CritE)
    stat['E']['std'] = np.sqrt( np.square(sum(fun_vals_CritE - stat['E']['mean'])) / len(fun_vals_CritE) )
    stat['E']['fun_vals'] = fun_vals_CritE
    
    stat['F']['mean'] = sum(fun_vals_CritF)/len(fun_vals_CritF)
    stat['F']['std'] = np.sqrt( np.square(sum(fun_vals_CritF - stat['F']['mean'])) / len(fun_vals_CritF) )
    stat['F']['fun_vals'] = fun_vals_CritF
    return stat