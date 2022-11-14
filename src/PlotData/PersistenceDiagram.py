##
# @file PersistenceDiagram.py
#
# @brief Contains function to plot persistence diagrams.
#
# @section libraries_PersistenceDiagram Libraries/Modules
# - numpy standard library
# - matplotlib.pyplot standard library

# imports
import numpy as np
import matplotlib.pyplot as plt


def PersistenceDiagram(MorseComplex, partner, maxval, minval, pointsize = 4, save = False, filepath = 'persistenceDiagram'):
    """! @brief Plots a persistence diagram of the given Morse Complex and optionally saves the figure.
    
    @param MorseComplex The Morse Complex we want to take the persistence diagram of.
    @param partner The dictionary containing the paired up cells, giving the non-infinte points in the diagram.
    @param maxval The maximum possible function value in the mesh.
    @param minval The minimum possible function value in the mesh.
    @param pointsize (Optional) The pointsize in the diagram. Default is 4. 
    @param save Optional) Bool. Whether to save the diagram or not. Default is False.
    @param filepath (Optional) The filename under which the diagram should be stored. Default is 'persistenceDiagram'.
    """
    points = {}
    M = {}
    M[0] = MorseComplex.CritVertices
    M[1] = MorseComplex.CritEdges
    M[2] = MorseComplex.CritFaces
    
    for p in range(3):
        points[p] = {}
        points[p]['x'] = []
        points[p]['y'] = []
        points[p]['infinite cycles'] = []
        
        for key in M[p].keys():
            if np.array(partner[p][key]).size == 1:
                if p == 0: # 0-1 persistence
                    points[p]['x'].append(M[p][key].fun_val)
                    points[p]['y'].append(M[p+1][partner[p][key]].fun_val[0])
                if p == 2: # 1-2 persistence
                    points[p-1]['x'].append(M[p-1][partner[p][key]].fun_val[0])
                    points[p-1]['y'].append(M[p][key].fun_val[0])
            elif np.array(partner[p][key]).size == 0:
                if p == 0:
                    points[p]['infinite cycles'].append(M[p][key].fun_val)
                else:
                    points[p]['infinite cycles'].append(M[p][key].fun_val[0])

    linsp = np.linspace(minval, maxval, 1000)
    plt.plot(linsp, linsp, color='black', linewidth=0.4)
    plt.scatter(points[0]['x'],points[0]['y'], s = 0.1*pointsize, c = 'r', alpha=1, label = None)
    plt.scatter(points[1]['x'],points[1]['y'], s = 0.1*pointsize, c = 'g', alpha=1, label = None)
    for x in points[0]['infinite cycles']:
        plt.scatter(x,[maxval+0.2*maxval], s = 5*pointsize, c = 'r', marker = 'x')
    for x in points[1]['infinite cycles']:
        plt.scatter(x,[maxval+0.2*maxval], s = 5*pointsize, c = 'g', marker = 'x')
    for x in points[2]['infinite cycles']:
        plt.scatter(x,[maxval+0.2*maxval], s = 5*pointsize, c = 'b', marker = 'x', label = None)
    
    plt.scatter([],[], c='r', marker='.', s= 5*pointsize, label = '0 cells')
    plt.scatter([],[], c='g', marker='.', s= 5*pointsize, label = '1 cells')
    plt.scatter([],[], c='b', marker='.', s= 5*pointsize, label = '2 cells')
    
    plt.plot([minval,minval],[maxval,maxval], c = 'g', linestyle = '-')
    plt.legend()
    plt.xlabel('birth times')
    plt.ylabel('death times')
    if MorseComplex.persistence == 0:
        plt.title('Persistence Diagram')
    else:
        plt.title('Persistence Diagram with '+str(MorseComplex.persistence)+' persistence')
    if save == True:
        plt.savefig(filepath, dpi=1200)
    plt.show()