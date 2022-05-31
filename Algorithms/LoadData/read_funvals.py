import numpy as np
from collections import Counter
import timeit

def read_funvals(filename, vertices_dict, edges_dict, faces_dict):
    start_total_time = timeit.default_timer()
    
    vals = []
    with open(filename, "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            else:
                ind = int(line.split()[0])
                feature_vec = [float(x) for x in line.split()[1:]]
                
                # possible change calculation here????
                vertices_dict[ind].fun_val = max(feature_vec)
                vals.append(max(feature_vec))
    
    counts = Counter(vals)
    for key, value in vertices_dict.items():
        if counts[value.fun_val] > 1:
            tmp = value.fun_val
            value.fun_val = value.fun_val + (counts[value.fun_val] - 1) * 0.0000001
            counts[tmp] = counts[tmp] - 1
            
    for edge in edges_dict.values():
        edge.set_fun_val(vertices_dict)
    for face in faces_dict.values():
        face.set_fun_val(vertices_dict)
    
    end_total_time = timeit.default_timer() - start_total_time
    print('Time read new function values:', end_total_time)
    
    return min(vals), max(vals) 