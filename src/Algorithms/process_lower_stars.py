##
# @file process_lower_stars.py
#
# @brief Contains the process_lower_stars function described in Robins et al. (DOI: 10.1109/TPAMI.2011.95)
# https://www.researchgate.net/publication/51131057_Theory_and_Algorithms_for_Constructing_Discrete_Morse_Complexes_from_Grayscale_Digital_Images
#
# @section libraries_process_lower_stars Libraries/Modules
# - numpy standard library
# - collections standard library
#   - need Counter and deque
# - PriorityQueue module (local)
#   - PriorityQueue

# imports
from .PriorityQueue import PriorityQueue

import numpy as np
from collections import Counter, deque

def lower_star(vertex, edges_dict, faces_dict):
    """! @brief Extracts the lower star of a vertex.
    @details Contains the vertex and all edges and faces with lower function values than the vertex.
    
    @param vertex The vertex we want to get the lower star of.
    @param edges_dict Dictionary containing all edges.
    @param faces_dict Dictionary containing all faces.
    
    @return lower_star A dictionary containing the keys 'vertex', 'edges' and 'faces' which each
    contain key value pairs of index and edge/face (Simplex class objects). The edges and faces 
    are sorted by function values.
    """
    # x a vertex
    # data star is list of heights and indices of all cells having x as subset
    
    lower_star = {}
    lower_star['vertex'] = {vertex.index : vertex.fun_val}
    lower_star['edges'] = {}
    lower_star['faces'] = {}
    
    for edge_ind in vertex.star["E"]:
        if edges_dict[edge_ind].fun_val[0] == vertex.fun_val:
            lower_star['edges'][edge_ind] = edges_dict[edge_ind]
            
    for face_ind in vertex.star["F"]:
        if faces_dict[face_ind].fun_val[0] == vertex.fun_val:
            lower_star['faces'][face_ind] = faces_dict[face_ind]
    
    # sort edges and cells: biggest/highest at the end
    lower_star['edges'] = {k: v for k, v in sorted(lower_star['edges'].items(), key=lambda item: item[1].fun_val)[::-1]}
    lower_star['faces'] = {k: v for k, v in sorted(lower_star['faces'].items(), key=lambda item: item[1].fun_val)[::-1]}

    return lower_star

def num_unpaired_faces(face, PQzero):
    """! @brief Gives the number of unpaired faces of a face, so the number of edges of a face that are not paired.
    
    @param face The face we want to get the number of unpaired faces of.
    @param PQzero The Priority Queue with 0 unpaired faces.
    
    @return number Returns the number of faces (edges) of a face (triangle) that have not been paired.
    """
    # checks number of faces in PQzero ( should be equal to number of unpaired faces in lower star, 
    # since all edges from lower star go to PQzero or are paired/ added to C and removed from PQzero)
    number = 0
    for simplex, index in PQzero.items():
        if face.has_face(simplex):
            number+=1
    return number

def pair(face, PQzero):
    """! @brief Returns a pair of face and edge.
    
    @param face The face that should be paired (which has exactly one unpaired face).
    @param PQzero The Priority Queue with 0 unpaired faces.
    
    @return index, simplex A tuple of the edge index that is paired with this face and the edge Simplex object.
    """
    for simplex, index in PQzero.items():
        if face.has_face(simplex):
            # need to pop the element from the Priority queue
            PQzero.pop(tuple((simplex,index)))
            return index, simplex

def process_lower_stars(vertices_dict, edges_dict, faces_dict, C, V12, V23):
    """! @brief The function described in Robins et al. 2011, that returns a discrete gradient vector field.
    
    @details Loops over all vertices, calculates their lower stars and pairs up as many edge-vertex (V12) or 
    face-edge (V23) pairs as possible. Simplices that cannot be paired will become critical simplices and 
    are stored in C.
    
    @param vertices_dict The dictionary containing all vertices.
    @param edges_dict The dictionary containing all edges.
    @param faces_dict The dictionary containing all faces.
    @param C The dictionary that will store all critical vertices, edges and faces.
    @param V12 The dictionary that will store pairings between edges and vertices.
    @param V23 The dictionary that will store pairings between faces and edges.
    
    @return Updated C, V12 and V23.
    """
    for vertex in vertices_dict.values():
        lowerStar = lower_star(vertex, edges_dict, faces_dict)
        
        if (len(lowerStar['edges'])+len(lowerStar['faces'])) == 0:
            C[0].add(vertex.index)
            
        else:
            PQzero = PriorityQueue()
            PQone = PriorityQueue()

            delta_Eindex, delta_edge = lowerStar['edges'].popitem()
            V12[vertex.index] = delta_Eindex
            
            for Eindex, edge in lowerStar['edges'].items():
                PQzero.insert(tuple((edge, Eindex)))
            
            for Findex, face in lowerStar['faces'].items():
                if (num_unpaired_faces(face, PQzero) == 1 and face.has_face(delta_edge)):
                    PQone.insert(tuple((face, Findex)))

            while (PQone.notEmpty() or PQzero.notEmpty()):
                while PQone.notEmpty():
                    alpha_simplex, alpha_index = PQone.pop_front()
                    
                    if num_unpaired_faces(alpha_simplex, PQzero) == 0:
                        PQzero.insert(tuple((alpha_simplex, alpha_index)))

                    else:
                        pair_index, pair_simplex = pair(alpha_simplex, PQzero)
                        V23[pair_index] = alpha_index

                        for Findex, face in lowerStar['faces'].items():
                            if (num_unpaired_faces(face, PQzero) == 1 and (face.has_face(alpha_simplex) or face.has_face(pair_simplex))):
                                PQone.insert(tuple((face, Findex)))
                
                if PQzero.notEmpty():
                    gamma_simplex, gamma_index = PQzero.pop_front()
                    
                    if len(gamma_simplex.indices) == 2:
                        C[1].add(gamma_index)
                    if len(gamma_simplex.indices) == 3:
                        C[2].add(gamma_index)
                    
                    for Findex, face in lowerStar['faces'].items():
                        if (num_unpaired_faces(face, PQzero) == 1 and face.has_face(gamma_simplex)):
                            PQone.insert(tuple((face, Findex)))