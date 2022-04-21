from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty
import numpy as np
import timeit
from collections import Counter, deque

#### Load data

def get_height(cell, vertex_list):
    # gives height array of cell. 
    # if vertex is ordered, than the height will be ordered as well
    height = []
    for ind in cell:
        height.append(vertex_list[ind])
    return tuple(sorted(height,reverse=True))

def load_data_forBettiComparison(path, position=2):
    start_eff = timeit.default_timer()
    
    read_da = timeit.default_timer()
    rawdata = PlyData.read(path)
    read_data = timeit.default_timer() -read_da
    print('Time read data file:', read_data)
    
    data = {}
    data[0] = {}
    data[1] = {}
    data[2] = {}
    
    Facelist = {}
    
    #vert_fi = timeit.default_timer()
    i = 0
    for vert in rawdata.elements[0].data:
        data[0][int(i)] = vert[position]
        i += 1
    
    # make heights unique
    counts = Counter(data[0].values())
    for key, value in data[0].items():
        if counts[value] > 1:
            data[0][key] = value + (counts[value] - 1) * 0.0000001
            counts[value] = counts[value] - 1
            
    # add faces and edges
    for face in rawdata.elements[1].data:
        data[2][tuple(face[0])] = tuple((get_height(face[0], data[0])))
        Facelist[tuple(face[0])] = list()
        
        for i in range(3):
            edge = face[0]
            edge = list(edge)
            edge.pop(i)
            if tuple(edge)[::-1] not in data[1].keys():
                data[1][tuple(edge)] = tuple((get_height(list(edge), data[0])))
                Facelist[tuple(edge)] = list()
                Facelist[tuple(edge)].append(tuple((tuple(edge)[0], data[0][tuple(edge)[0]]))) 
                Facelist[tuple(edge)].append(tuple((tuple(edge)[1], data[0][tuple(edge)[1]])))
                
                Facelist[tuple(face[0])].append(tuple((tuple(edge), tuple((get_height(list(edge), data[0]))))))
                
            elif tuple(edge)[::-1] in data[1].keys():
                Facelist[tuple(face[0])].append(tuple((tuple(edge)[::-1], tuple((get_height(list(edge), data[0]))))))
        
    time_eff = timeit.default_timer() - start_eff
    print('Time load data total:', time_eff)
 
    return data, Facelist