from .PriorityQueue import PriorityQueue

import numpy as np
import timeit
from collections import Counter, deque

def lower_star(x_key, x_value, data_star, N):
    # x a vertex
    # data star is list of heights and indices of all cells having x as subset
    
    lower_star = {}
    lower_star['vertex'] = {x_key : x_value}
    lower_star['edges'] = {}
    lower_star['faces'] = {}
    
    for key, value in data_star.items():
        if max(value) == x_value:
            if len(value) == 2:
                lower_star['edges'].update({key : value})
            if len(value) == N:
                lower_star['faces'].update({key : value})

    # sort edges and cells: biggest/highest at the end
    lower_star['edges'] = {k: v for k, v in sorted(lower_star['edges'].items(), key=lambda item: item[1])[::-1]}
    lower_star['faces'] = {k: v for k, v in sorted(lower_star['faces'].items(), key=lambda item: item[1])[::-1]}

    return lower_star

def num_unpaired_faces(face, PQzero):
    # checks number of faces in PQzero ( should be equal to number of unpaired faces in lower star, 
    # since all edges from lower star go to PQzero or are paired/ added to C and removed from PQzero)
    number = 0
    for key in PQzero.keys():
        if (set(key).issubset(face) and len(key) == 2):
            number +=1
    return number

def pair(face, PQzero):
    for key in PQzero.keys():
        if (set(key).issubset(face) and len(key) == 2):
            return key, PQzero.pop_key(key)


def ProcessLowerStar(data, N):
    start_eff = timeit.default_timer()
    C = {}
    C[0] = {}
    C[1] = {}
    C[2] = {}
    V = {}
    

    for vertex_key, vertex_value in data['vertex'].items():
        lowerStar = lower_star(vertex_key, vertex_value, data['star'][vertex_key], N)
        
        if (len(lowerStar['edges'])+len(lowerStar['faces'])) == 0:
            C[0].update({vertex_key : vertex_value})
            
        else:
            PQzero = PriorityQueue()
            PQone = PriorityQueue()

            delta_key, delta_value = lowerStar['edges'].popitem()
            V[vertex_key] = tuple((delta_key , delta_value))
            
            for key, value in lowerStar['edges'].items():
                PQzero.insert(tuple((key, value)))
            
            for key, value in lowerStar['faces'].items():
                if (num_unpaired_faces(key, PQzero) == 1 and value > delta_value):
                    PQone.insert(tuple((key, value)))

            while (PQone.notEmpty() or PQzero.notEmpty()):
                while PQone.notEmpty():
                    alpha_key, alpha_value = PQone.pop_front()
                    
                    if num_unpaired_faces(alpha_key, PQzero) == 0:
                        PQzero.insert(tuple((alpha_key, alpha_value)))

                    else:
                        pair_key, pair_value = pair(alpha_key, PQzero)
                        V[pair_key] = tuple((alpha_key , alpha_value))

                        for key, value in lowerStar['faces'].items():
                            if (num_unpaired_faces(key,PQzero) == 1 and (value > alpha_value or value > pair_value)):
                                PQone.insert(tuple((key, value)))
                
                if PQzero.notEmpty():
                    gamma_key, gamma_value = PQzero.pop_front()

                    if len(gamma_key) == 2:
                        C[1].update({gamma_key : gamma_value})
                    if len(gamma_key) == N:
                        C[2].update({gamma_key : gamma_value})
                    
                    for key, value in lowerStar['faces'].items():
                        if (num_unpaired_faces(key,PQzero) == 1 and value > gamma_value):
                            PQone.insert(tuple((key, value)))

    time_eff = timeit.default_timer() -start_eff
    print('Time ProcessLowerStar:', time_eff)    
    
    return C, V


def ProcessLowerStarCoface(data, N):
    start_eff = timeit.default_timer()
    C = {}
    C[0] = {}
    C[1] = {}
    C[2] = {}
    V = {}
    

    for vertex_key, vertex_value in data['vertex'].items():
        lowerStar = lower_star(vertex_key, vertex_value, data['star'][vertex_key], N)
        
        if (len(lowerStar['edges'])+len(lowerStar['faces'])) == 0:
            C[0].update({vertex_key : vertex_value})
            
        else:
            PQzero = PriorityQueue()
            PQone = PriorityQueue()

            delta_key, delta_value = lowerStar['edges'].popitem()
            V[vertex_key] = tuple((delta_key , delta_value))
            
            for key, value in lowerStar['edges'].items():
                PQzero.insert(tuple((key, value)))
            
            for key, value in lowerStar['faces'].items():
                if (num_unpaired_faces(key, PQzero) == 1 and set(delta_key).issubset(key)):
                    PQone.insert(tuple((key, value)))

            while (PQone.notEmpty() or PQzero.notEmpty()):
                while PQone.notEmpty():
                    alpha_key, alpha_value = PQone.pop_front()
                    
                    if num_unpaired_faces(alpha_key, PQzero) == 0:
                        PQzero.insert(tuple((alpha_key, alpha_value)))

                    else:
                        pair_key, pair_value = pair(alpha_key, PQzero)
                        V[pair_key] = tuple((alpha_key , alpha_value))

                        for key, value in lowerStar['faces'].items():
                            if (num_unpaired_faces(key,PQzero) == 1 and (set(alpha_key).issubset(key) or set(pair_key).issubset(key))):
                                PQone.insert(tuple((key, value)))
                
                if PQzero.notEmpty():
                    gamma_key, gamma_value = PQzero.pop_front()

                    if len(gamma_key) == 2:
                        C[1].update({gamma_key : gamma_value})
                    if len(gamma_key) == N:
                        C[2].update({gamma_key : gamma_value})
                    
                    for key, value in lowerStar['faces'].items():
                        if (num_unpaired_faces(key,PQzero) == 1 and set(gamma_key).issubset(key)):
                            PQone.insert(tuple((key, value)))

    time_eff = timeit.default_timer() -start_eff
    print('Time ProcessLowerStar eff:', time_eff)    
    
    return C, V

