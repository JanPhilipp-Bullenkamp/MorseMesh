##
# @file read_funvals.py
#
# @brief Contains function for reading new function values from a feature vector file 
# generated by Gigamesh into vertices, and updating edges and faces as well.
#
# @section libraries_read_ply Libraries/Modules
# - numpy standard library
# - collections standard library
#   - need Counter for unique values

#Imports
from collections import Counter
from .anisotropic_diffusion import compute_anisotropic_diffusion

def read_funvals(filename: str, vertices_dict: dict, edges_dict: dict, faces_dict: dict):
    """! @brief Reads a feature vector file and uses the max of each vector as new Morse function values.
    
    @details CURRENTLY JUST SUPPORTS THE MAX OF A FEATURE VECTOR...... might be updated in future to also
    enable min or other metrics.
    
    @param filename The feature vector file to be read for new function values.
    @param vertices_dict The vertices dictionary to be updated with new function values.
    @param edges_dict The edges dictionary to be updated with new function values.
    @param faces_dict The faces dictionary to be updated with new function values.
    
    @return Despite updating the dictionaries, returns the minimum and maximum function value as min, max.
    """
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
    
    min_funval, max_funval = make_vert_funvals_unique(vertices_dict, vals)        
    update_edges_and_faces_funvals(vertices_dict, edges_dict, faces_dict)

    return min_funval, max_funval 

def apply_Perona_Malik_diffusion(vert_dict: dict, edge_dict: dict, face_dict: dict, iterations: int, lamb: float, k: float):
    # compute diffusion (vert dict changed in place)
    compute_anisotropic_diffusion(vert_dict, iterations, lamb, k)
    # make sure vert fun_vals are unique and update edges and faces accordingly
    min_funval, max_fun_val = make_vert_funvals_unique(vert_dict)
    update_edges_and_faces_funvals(vert_dict, edge_dict, face_dict)

    return min_funval, max_fun_val

def update_edges_and_faces_funvals(vert_dict: dict, edge_dict: dict, face_dict: dict):
    for edge in edge_dict.values():
        edge.set_fun_val(vert_dict)
    for face in face_dict.values():
        face.set_fun_val(vert_dict)

def make_vert_funvals_unique(vert_dict: dict, vals: list = None):
    if vals == None:
        vals = [vert.fun_val for vert in vert_dict.values()]
    counts = Counter(vals)
    for vert in vert_dict.values():
        if counts[vert.fun_val] > 1:
            tmp = vert.fun_val
            vert.fun_val = vert.fun_val + (counts[vert.fun_val] - 1) * 0.0000001
            counts[tmp] = counts[tmp] - 1
    return min(vals), max(vals)