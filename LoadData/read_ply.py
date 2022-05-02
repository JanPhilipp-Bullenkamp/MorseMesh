from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty
import numpy as np
from collections import Counter
import timeit

from .Datastructure import Vertex, Edge, Face

def read_ply(filename, quality_index, vertices_dict, edges_dict, faces_dict):
    start_time = timeit.default_timer()
    
    rawdata = PlyData.read(filename)
    
    end_time = timeit.default_timer() - start_time
    print('Time read data file:', end_time) 
    
    vals = []
    for vindex, pt in enumerate(rawdata['vertex']):
        vert = Vertex(x=pt[0], y=pt[1], z=pt[2], quality=pt[quality_index], index=vindex)
        vert.fun_val = vert.quality
        vals.append(vert.fun_val)
        vertices_dict[vindex] = vert
        
    counts = Counter(vals)
    for key, value in vertices_dict.items():
        if counts[value.fun_val] > 1:
            tmp = value.fun_val
            value.fun_val = value.fun_val + (counts[value.fun_val] - 1) * 0.0000001
            counts[tmp] = counts[tmp] - 1
            
    
    eindex = 0
    unique_edges = set()
    for findex, rawface in enumerate(rawdata['face']):
        face = Face(indices=set(rawface[0]), index=findex)
        face.set_fun_val(vertices_dict)
        
        faces_dict[findex] = face
        
        for i in range(3):
            tmp = list(rawface[0])
            tmp_ind = tmp.pop(i)
            vertices_dict[tmp_ind].star["F"].append(findex)
            
            if set(tmp) not in unique_edges:
                edge = Edge(indices=set(tmp), index=eindex)
                edge.set_fun_val(vertices_dict)
                
                edges_dict[eindex] = edge
                for tmp_ed_ind in tmp:
                    vertices_dict[tmp_ed_ind].star["E"].append(eindex)
                
                eindex+=1
                
                unique_edges.add(frozenset(tmp))
         
            


