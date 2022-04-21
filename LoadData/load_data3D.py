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

def load_data3D(path, position=2, inverted=False):
    start_eff = timeit.default_timer()
    
    read_da = timeit.default_timer()
    rawdata = PlyData.read(path)
    read_data = timeit.default_timer() -read_da
    print('Time read data file:', read_data)
    
    data = {}
    data['vertex'] = {}
    data['star'] = {}
    
    
    i = 0
    if inverted:
        for vert in rawdata.elements[0].data:
            data['vertex'][int(i)] = -1*vert[position]
            data['star'][int(i)] = {}
            i += 1
    else:
        for vert in rawdata.elements[0].data:
            data['vertex'][int(i)] = vert[position]
            data['star'][int(i)] = {}
            i += 1
        
    # make heights unique
    counts = Counter(data['vertex'].values())
    for key, value in data['vertex'].items():
        if counts[value] > 1:
            data['vertex'][key] = value + (counts[value] - 1) * 0.0000001
            counts[value] = counts[value] - 1
            
    # add faces and edges
    for face in rawdata.elements[1].data:
        data['star'][face[0][0]].update({tuple(face[0]) : tuple((get_height(face[0], data['vertex'])))})
        data['star'][face[0][1]].update({tuple(face[0]) : tuple((get_height(face[0], data['vertex'])))})
        data['star'][face[0][2]].update({tuple(face[0]) : tuple((get_height(face[0], data['vertex'])))})
        
        for i in range(3):
            edge = face[0]
            edge = list(edge)
            edge.pop(i)
            if tuple(edge)[::-1] not in data['star'][edge[0]].keys():
                data['star'][edge[0]].update({tuple(edge) : tuple((get_height(list(edge), data['vertex'])))})
                data['star'][edge[1]].update({tuple(edge) : tuple((get_height(list(edge), data['vertex'])))})
            if tuple(edge)[::-1] not in data['star'][edge[1]].keys():
                data['star'][edge[0]].update({tuple(edge) : tuple((get_height(list(edge), data['vertex'])))})
                data['star'][edge[1]].update({tuple(edge) : tuple((get_height(list(edge), data['vertex'])))})
    
    time_eff = timeit.default_timer() - start_eff
    print('Time load data total:', time_eff)
 
    return rawdata, data