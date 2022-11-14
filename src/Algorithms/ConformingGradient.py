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
        for i in faces_dict[key].indices:
            labels['faces'][key].add(labels_dict[i])

    return labels

def num_unpaired_conforming_faces(Findex, face, PQzero, star_labels):
    # checks number of faces in PQzero ( should be equal to number of unpaired faces in lower star, 
    # since all edges from lower star go to PQzero or are paired/ added to C and removed from PQzero)
    number = 0
    for simplex, index in PQzero.items():
        if face.has_face(simplex) and star_labels['faces'][Findex] == star_labels['edges'][index]:
            number+=1
    return number

def conforming_pair(Findex, face, PQzero, star_labels):
    for simplex, index in PQzero.items():
        if face.has_face(simplex) and star_labels['faces'][Findex] == star_labels['edges'][index]:
            # need to pop the element from the Priority queue
            PQzero.pop(tuple((simplex,index)))
            return index, simplex

def ConformingGradient(vertices_dict, edges_dict, faces_dict, labels_dict, C, V12, V23):
    start_eff = timeit.default_timer()
    
    for vertex in vertices_dict.values():
        lowerStar = lower_star(vertex, edges_dict, faces_dict)

        if len(lowerStar['edges']) == 0:
            C[0].add(vertex.index)
        else:
            star_labels = construct_labels(lowerStar, edges_dict, faces_dict, labels_dict)
        
            label_set = {labels_dict[vertex.index]}
            
            conformingEdges = [Eindex for Eindex in lowerStar['edges'].keys() if star_labels['edges'][Eindex] == label_set]

            if len(conformingEdges) == 0:
                C[0].add(vertex.index)
            else:
                delta_Eindex = conformingEdges.pop()
                delta_edge = lowerStar['edges'].pop(delta_Eindex)
                V12[vertex.index] = delta_Eindex

            PQzero = PriorityQueue()
            PQone = PriorityQueue()
            VisitedFaces = []
            
            for Eindex, edge in lowerStar['edges'].items():
                PQzero.insert(tuple((edge, Eindex)))
            
            for Findex, face in lowerStar['faces'].items():
                if (num_unpaired_conforming_faces(Findex, face, PQzero, star_labels) == 1 and face.has_face(delta_edge)):
                    PQone.insert(tuple((face, Findex)))
                    VisitedFaces.append(Findex)

            while (PQone.notEmpty() or PQzero.notEmpty()):
                while PQone.notEmpty():
                    alpha_simplex, alpha_index = PQone.pop_front()
                    
                    if num_unpaired_conforming_faces(alpha_index, alpha_simplex, PQzero, star_labels) == 0:
                        PQzero.insert(tuple((alpha_simplex, alpha_index)))

                    else:
                        pair_index, pair_simplex = conforming_pair(alpha_index, alpha_simplex, PQzero, star_labels)
                        V23[pair_index] = alpha_index

                        for Findex, face in lowerStar['faces'].items():
                            if (num_unpaired_conforming_faces(alpha_index, alpha_simplex, PQzero, star_labels) == 1 and (face.has_face(alpha_simplex) or face.has_face(pair_simplex))):
                                PQone.insert(tuple((face, Findex)))
                                VisitedFaces.append(Findex)
                
                if PQzero.notEmpty():
                    gamma_simplex, gamma_index = PQzero.pop_front()
                    
                    if len(gamma_simplex.indices) == 2:
                        C[1].add(gamma_index)
                    if len(gamma_simplex.indices) == 3:
                        C[2].add(gamma_index)
                    
                    for Findex, face in lowerStar['faces'].items():
                        if (num_unpaired_conforming_faces(alpha_index, alpha_simplex, PQzero, star_labels) == 1 and face.has_face(gamma_simplex)):
                            PQone.insert(tuple((face, Findex)))

            for Findex, face in lowerStar['faces'].items(): #all leftover faces are critical
                if not (Findex in VisitedFaces):
                    C[2].add(Findex)

    time_eff = timeit.default_timer() -start_eff
    print('Time ProcessLowerStar:', time_eff)