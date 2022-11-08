from .PriorityQueue import PriorityQueue
from .ProcessLowerStars import lower_star

import numpy as np
import timeit
from collections import Counter, deque

def construct_labels(lower_star, edges_dict, faces_dict, labels_dict):
    labels = {'edges': {}, 'faces': {}}

    for key in lower_star['edges'].keys():
        labels['edges'][key] = set()
        for i in edges_dict[key].indices:
            labels['edges'][key].add(labels_dict[i])

    for key in lower_star['faces'].keys():
        labels['faces'][key] = set()
        for i in edges_dict[key].indices:
            labels['faces'][key].add(labels_dict[i])

    return labels

def num_unpaired_conforming_faces(face, PQzero, edges_dict, faces_dict, star_labels):
    # checks number of faces in PQzero ( should be equal to number of unpaired faces in lower star, 
    # since all edges from lower star go to PQzero or are paired/ added to C and removed from PQzero)
    number = 0
    for key in PQzero.keys():
        if len(edges_dict[key].indices) == 2:
            if (edges_dict[key].indices).issubset(faces_dict[face].indices):
                number+=1
    return number

def pair(face, PQzero, edges_dict, faces_dict, star_labels):
    for key in PQzero.keys():
        if len(edges_dict[key].indices) ==2:
            if (edges_dict[key].indices).issubset(faces_dict[face].indices):
                return key, PQzero.pop_key(key)

def ConformingGradient(vertices_dict, edges_dict, faces_dict, labels_dict, C, V12, V23):
    start_eff = timeit.default_timer()
    
    for vertex in vertices_dict.values():
        lowerStar = lower_star(vertex, edges_dict, faces_dict)

        if len(lowerStar['edges']) == 0:
            C[0].add(vertex.index)
        else:
            star_labels = construct_labels(lowerStar, edges_dict, faces_dict, labels_dict)
        
            label_set = {labels_dict[vertex.index]}
            
            conformingEdges = {key for key in lower_star['edges'].keys() if star_labels['edges'][key] == label_set}

            if len(conformingEdges) == 0:
                C[0].add(vertex.index)
            else:
                key = conformingEdges.popitem()
                delta_key, delta_value = lowerStar['edges'].pop(key)
                V12[vertex.index] = delta_key

            PQzero = PriorityQueue()
            PQone = PriorityQueue()
            
            for key, value in lowerStar['edges'].items():
                PQzero.insert(tuple((key, value)))
            
            for key, value in lowerStar['faces'].items():
                if (num_unpaired_conforming_faces(key, PQzero, edges_dict, faces_dict, star_labels) == 1 and value > delta_value):
                    PQone.insert(tuple((key, value)))

            while (PQone.notEmpty() or PQzero.notEmpty()):
                while PQone.notEmpty():
                    alpha_key, alpha_value = PQone.pop_front()
                    
                    if num_unpaired_conforming_faces(alpha_key, PQzero, edges_dict, faces_dict) == 0:
                        PQzero.insert(tuple((alpha_key, alpha_value)))

                    else:
                        pair_key, pair_value = pair(alpha_key, PQzero, edges_dict, faces_dict)
                        V23[pair_key] = alpha_key

                        for key, value in lowerStar['faces'].items():
                            if (num_unpaired_conforming_faces(key,PQzero, edges_dict, faces_dict) == 1 and (value > alpha_value or value > pair_value)):
                                PQone.insert(tuple((key, value)))
                
                if PQzero.notEmpty():
                    gamma_key, gamma_value = PQzero.pop_front()
                    
                    if len(gamma_value) == 2:
                        C[1].add(gamma_key)
                    if len(gamma_value) == 3:
                        C[2].add(gamma_key)
                    
                    for key, value in lowerStar['faces'].items():
                        if (num_unpaired_conforming_faces(key,PQzero, edges_dict, faces_dict) == 1 and value > gamma_value):
                            PQone.insert(tuple((key, value)))

    time_eff = timeit.default_timer() -start_eff
    print('Time ProcessLowerStar:', time_eff)