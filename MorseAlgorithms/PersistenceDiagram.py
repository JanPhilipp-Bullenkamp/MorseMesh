import numpy as np
import matplotlib.pyplot as plt


def Persistence_Diagram(M, partner, maxval, minval, pointsize = 4, save = False, filepath = None):
    points = {}
    #maxval=0.4
    #minval=-0.25
    for p in range(3):
        points[p] = {}
        points[p]['x'] = []
        points[p]['y'] = []
        points[p]['infinite cycles'] = []
        
        for key in M[p].keys():
            if np.array(partner[key]).size == p + 2:
                if p == 0:
                    points[p]['x'].append(M[p][key])
                else:
                    points[p]['x'].append(max(M[p][key]))
                points[p]['y'].append(max(M[p+1][partner[key]]))
            elif np.array(partner[key]).size == 0:
                if p == 0:
                    points[p]['infinite cycles'].append(M[p][key])
                else:
                    points[p]['infinite cycles'].append(max(M[p][key]))

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
    plt.title('Persistence Diagram')
    if save == True:
        plt.savefig(filepath, dpi=1200)
    plt.show()