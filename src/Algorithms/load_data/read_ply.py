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
# - Datastructure module (local)
#   - Access to Vertex, Edge and Face classes.

#Imports
from plyfile import PlyData
from collections import Counter

from .datastructures import Vertex, Simplex

def read_ply(filename, quality_index, vertices_dict, edges_dict, faces_dict, inverted=False):
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
    
    @return Despite filling the dictionaries, returns the minimum and maximum function value as min, max.
    """
    rawdata = PlyData.read(filename)
    
    vals = []
    for vindex, pt in enumerate(rawdata['vertex']):
        vert = Vertex(x=pt[0], y=pt[1], z=pt[2], quality=pt[quality_index], index=vindex)
        if inverted:
            vert.fun_val = -1 * vert.quality
        else:
            vert.fun_val = vert.quality
        vals.append(vert.fun_val)
        vertices_dict[vindex] = vert
        
    counts = Counter(vals)
    for vert in vertices_dict.values():
        if counts[vert.fun_val] > 1:
            tmp = vert.fun_val
            vert.fun_val = vert.fun_val + (counts[vert.fun_val] - 1) * 0.0000001
            counts[tmp] = counts[tmp] - 1
            
    
    eindex = 0
    unique_edges = set()
    for findex, rawface in enumerate(rawdata['face']):
        face = Simplex(indices=set(rawface[0]), index=findex)
        face.set_fun_val(vertices_dict)
        
        faces_dict[findex] = face
        
        for i in range(3):
            tmp = list(rawface[0])
            tmp_ind = tmp.pop(i)
            vertices_dict[tmp_ind].star["F"].append(findex)
            
            vertices_dict[tmp_ind].neighbors.add(tmp[0])
            vertices_dict[tmp_ind].neighbors.add(tmp[1])
            
            if set(tmp) not in unique_edges:
                edge = Simplex(indices=set(tmp), index=eindex)
                edge.set_fun_val(vertices_dict)
                
                edges_dict[eindex] = edge
                for tmp_ed_ind in tmp:
                    vertices_dict[tmp_ed_ind].star["E"].append(eindex)
                
                eindex+=1
                
                unique_edges.add(frozenset(tmp))
    return min(vals), max(vals)
    