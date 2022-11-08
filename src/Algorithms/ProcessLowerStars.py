from .PriorityQueue import PriorityQueue

import numpy as np
import timeit
from collections import Counter, deque

def lower_star(vertex, edges_dict, faces_dict):
    # x a vertex
    # data star is list of heights and indices of all cells having x as subset
    
    lower_star = {}
    lower_star['vertex'] = {vertex.index : vertex.fun_val}
    lower_star['edges'] = {}
    lower_star['faces'] = {}
    
    for edge_ind in vertex.star["E"]:
        if edges_dict[edge_ind].fun_val[0] == vertex.fun_val:
            lower_star['edges'][edge_ind] = edges_dict[edge_ind] #.fun_val
            
    for face_ind in vertex.star["F"]:
        if faces_dict[face_ind].fun_val[0] == vertex.fun_val:
            lower_star['faces'][face_ind] = faces_dict[face_ind] #.fun_val
    
    # sort edges and cells: biggest/highest at the end
    lower_star['edges'] = {k: v for k, v in sorted(lower_star['edges'].items(), key=lambda item: item[1].fun_val)[::-1]}
    lower_star['faces'] = {k: v for k, v in sorted(lower_star['faces'].items(), key=lambda item: item[1].fun_val)[::-1]}

    return lower_star

def num_unpaired_faces(face, PQzero):
    # checks number of faces in PQzero ( should be equal to number of unpaired faces in lower star, 
    # since all edges from lower star go to PQzero or are paired/ added to C and removed from PQzero)
    number = 0
    for simplex, index in PQzero.items():
        if face.has_face(simplex):
            number+=1
    return number

def pair(face, PQzero):
    for simplex, index in PQzero.items():
        if face.has_face(simplex):
            return index, simplex

def ProcessLowerStars(vertices_dict, edges_dict, faces_dict, C, V12, V23):
    start_eff = timeit.default_timer()
    
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

    time_eff = timeit.default_timer() -start_eff
    print('Time ProcessLowerStar:', time_eff)