##
# @file statistics.py
#
# @brief Contains functions to get statistics on function values of vertices, critical simplices and 
# separatrix persistence as well as plotting their histograms.
#
# @section libraries_plot_statistics Libraries/Modules
# - numpy standard library
# - collections standard library
#   - need Counter
# - matplotlib.pyplot standard library
#   - for histogram plotting

#  imports
import numpy as np
import matplotlib.pyplot as plt

def fun_val_statistics(vert_dict, nb_bins = 15, log=False, save = False, filepath = 'histogram', show = True):
    """! @brief Creates statistics of function values on all vertices and allows to optionally plot 
    and save a histogram as well.
    
    @param vert_dict A dictionary of Vertex class objects that have function values.
    @param nb_bins (Optional) Integer. The number of bins for the histogram. Default is 15.
    @param log (Optional) Bool. Use logarithmic scale for the counts /y-axis in the 
    histogram. Default is False.
    @param save (Optional) Bool. Whether to save the histogram as a file. Default is False.
    @param filepath (Optional) The filepath to use if the histogram should be saved. Default is 'histogram'.
    @param show (Optional) Bool. Whether to plot the histogram or not. Default is True.
    
    @return stat A dictionary containing the keys 'mean', 'std' and 'fun_vals' containing the mean, 
    the standard deviation and a list of the function values.
    """
    fun_vals = []
    for vert in vert_dict.values():
        fun_vals.append(vert.fun_val)
        
    if save or show:
        plt.hist(fun_vals, bins=nb_bins, log=log)
        plt.xlabel("Function Value")
        plt.ylabel("Counts")
        plt.title("Function Value Histogram")
    if save == True:
        plt.savefig(filepath, dpi=600)
    if show:
        plt.show()
    
    stat = {}
    stat['mean'] = np.mean(fun_vals)
    stat['std'] = np.std(fun_vals)
    stat['fun_vals'] = fun_vals
    return stat

def critical_fun_val_statistics(MSComplex, nb_bins = 15, log=False, save = False, filepath = 'histogram', show = True):
    """! @brief Creates statistics of function values on all critical vertices, edges and faces separately and 
    allows to optionally plot and save the histograms as well.
    
    @details the histograms will be plotted adding 'critV', 'critE' and 'critF' to the filepath.
    
    @param MSComplex The Morse Complex we want to have the function value statistics of (will use CritV, CritE and CritF).
    @param nb_bins (Optional) Integer. The number of bins for the histogram. Default is 15.
    @param log (Optional) Bool. Use logarithmic scale for the counts /y-axis in the 
    histogram. Default is False.
    @param save (Optional) Bool. Whether to save the histogram as a file. Default is False.
    @param filepath (Optional) The filepath to use if the histogram should be saved. Default is 'histogram'.
    @param show (Optional) Bool. Whether to plot the histogram or not. Default is True.
    
    @return stat A dictionary containing the keys 'V', 'E' and 'F' each containing dictionaries with keys 'mean', 
    'std' and 'fun_vals' containing the mean, the standard deviation and a list of the function values for the critical 
    vertices, edges or faces respectively.
    """
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
    if save or show:
        plt.hist(fun_vals_CritV, bins=nb_bins, log=log)
        plt.xlabel("Function Value")
        plt.ylabel("Counts")
        plt.title("Critical Vertices Function Value Histogram")
    if save == True:
        plt.savefig(filepath + 'critV', dpi=600)
    if show:
        plt.show()

    # plot crit edges histogram
    if save or show:
        plt.hist(fun_vals_CritE, bins=nb_bins, log=log)
        plt.xlabel("Function Value")
        plt.ylabel("Counts")
        plt.title("Critical Edges Function Value Histogram")
    if save == True:
        plt.savefig(filepath + 'critE', dpi=600)
    if show:
        plt.show()
    
    # plot crit faces histogram
    if save or show:
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
    
    stat['V']['mean'] = np.mean(fun_vals_CritV)
    stat['V']['std'] = np.std(fun_vals_CritV)
    stat['V']['fun_vals'] = fun_vals_CritV
    
    stat['E']['mean'] = np.mean(fun_vals_CritE)
    stat['E']['std'] = np.std(fun_vals_CritE)
    stat['E']['fun_vals'] = fun_vals_CritE
    
    stat['F']['mean'] = np.mean(fun_vals_CritF)
    stat['F']['std'] = np.std(fun_vals_CritF)
    stat['F']['fun_vals'] = fun_vals_CritF
    return stat

def salient_edge_statistics(Complex, nb_bins=15, log=False, save=False, filepath='histogram', show=True):
    """! @brief Creates statistics of the separatrix persistences of the cancelled separatrices in the given 
    Morse Complex and allows to optionally plot and save a histogram as well.
    
    @param Complex The Morse Complex we want to have the separatrix persistence statistics of.
    @param nb_bins (Optional) Integer. The number of bins for the histogram. Default is 15.
    @param log (Optional) Bool. Use logarithmic scale for the counts /y-axis in the 
    histogram. Default is False.
    @param save (Optional) Bool. Whether to save the histogram as a file. Default is False.
    @param filepath (Optional) The filepath to use if the histogram should be saved. Default is 'histogram'.
    @param show (Optional) Bool. Whether to plot the histogram or not. Default is True.
    
    @return stat A dictionary containing the keys 'mean', 'std' and 'persistences' containing the mean, 
    the standard deviation and a list of the separatrix persistences.
    """
    persistences = []
    for pers, _ in Complex.Separatrices:
        persistences.append(pers)
        
    if save or show:
        plt.hist(persistences, bins=nb_bins, log=log)
        plt.xlabel("Separatrix Persistence")
        plt.ylabel("Counts")
        plt.title("Separatrix Persistence Histogram")
    if save == True:
        plt.savefig(filepath, dpi=600)
    if show:
        plt.show()
    
    stat = {}
    stat['mean'] = np.mean(persistences)
    stat['std'] = np.std(persistences)
    stat['persistences'] = persistences
    return stat