##
# @file read_ply.py
#
# @brief Contains function for reading a ply file into vertices, edges and faces dictionaries.
#
# @section libraries_read_ply Libraries/Modules
# - plyfile library (https://github.com/dranjan/python-plyfile)
#   - Reading ply file
# - numpy standard library
# - collections standard library
#   - need Counter for unique values
# - timeit standard library
#   - timing functions
# - Datastructure module (local)
#   - Access to Vertex, Edge and Face classes.

#Imports
from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty
import numpy as np
from collections import Counter
import timeit

from .Datastructure import Vertex, Edge, Face

def read_ply(filename, quality_index, vertices_dict, edges_dict, faces_dict, inverted=False, load_normals=False):
    """! @brief Reads a ply file and writes the simplicial complex into vertices, edges and faces dictionaries.
    
    @details This function reads the given ply file and fills the given vertices dictionary, edges dictionary 
    and faces dictionary. It uses the values given at the quality index position as Morse function values and makes 
    sure that they are all unique so that we can use it for discrete Morse theory. Also allows to flip the function values
    by multiplying with -1 and thereby switching minima and maxima.
    
    @param filename The ply file to be read.
    @param quality_index The position of the quality you want to read in as the Morse function. Might vary depending on the
           ply file and application.
    @param vertices_dict The vertices dictionary to be filled with vertices.
    @param edges_dict The edges dictionary to be filled with edges.
    @param faces_dict The faces dictionary to be filled with faces.
    @param inverted Optional boolean: whether the Morse function values (quality values) should be multiplied with -1. 
           Doing this flips maxima and minima, default is False
    @param load_normals Optional boolena: whether to load normals into the mesh as well. Default is False.
    
    @return Despite filling the dictionaries, returns the minimum and maximum function value as min, max.
    """
    start_total_time = timeit.default_timer()
    start_time = timeit.default_timer()
    
    rawdata = PlyData.read(filename)
    
    end_time = timeit.default_timer() - start_time
    print('Time read data file:', end_time) 
    
    vals = []
    for vindex, pt in enumerate(rawdata['vertex']):
        vert = Vertex(x=pt[0], y=pt[1], z=pt[2], quality=pt[quality_index], index=vindex)
        if load_normals:
            vert.nx = rawdata['vertex']['nx'][vindex]
            vert.ny = rawdata['vertex']['ny'][vindex]
            vert.nz = rawdata['vertex']['nz'][vindex]
        if inverted:
            vert.fun_val = -1 * vert.quality
        else:
            vert.fun_val = vert.quality
        #vert.fun_val = np.sqrt((vert.x)**2 + (vert.y)**2 + (vert.z)**2)
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
            
            vertices_dict[tmp_ind].neighbors.add(tmp[0])
            vertices_dict[tmp_ind].neighbors.add(tmp[1])
            
            if set(tmp) not in unique_edges:
                edge = Edge(indices=set(tmp), index=eindex)
                edge.set_fun_val(vertices_dict)
                
                edges_dict[eindex] = edge
                for tmp_ed_ind in tmp:
                    vertices_dict[tmp_ed_ind].star["E"].append(eindex)
                
                eindex+=1
                
                unique_edges.add(frozenset(tmp))
                
    end_total_time = timeit.default_timer() - start_total_time
    print('Time read and prepare data:', end_total_time)
    
    return min(vals), max(vals)
    