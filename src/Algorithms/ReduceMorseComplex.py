from collections import Counter
import numpy as np
import timeit
from copy import deepcopy

from .CancellationQueue import CancellationQueue
from .LoadData.Datastructure import Separatrix

def get_closest_extremum(crit_edge, vert_dict, face_dict):
    distances = []
    
    # first add distances to all maxima
    face_counter = Counter(crit_edge.connected_maxima)
    for face_ind, nb in face_counter.items():
        # cannot cancel loops, so only if there is a single path we can add the extremum
        if nb==1:
            # check for valuebale edge-min connections:
            min_dist = []
            for elt in crit_edge.connected_minima:
                min_dist.append(vert_dict[elt].fun_val)
            # take absolute value btw the two highest vertices of edge and face respectively
            distances.append(tuple((face_ind, 2, abs(face_dict[face_ind].fun_val[0]-crit_edge.fun_val[0])))) 
                               
    # now add distances to all minima
    vert_counter = Counter(crit_edge.connected_minima)
    for vert_ind, nb in vert_counter.items():
        # cannot cancel loops, so only if there is a single path we can add the extremum
        if nb==1:
            #check for valuable max-edge connections:
            max_dist = []
            for elt in crit_edge.connected_maxima:
                max_dist.append(face_dict[elt].fun_val[0])
                
            # take absolute value btw the highest vertex of edge and the value of the vertex
            distances.append(tuple((vert_ind, 0, abs(crit_edge.fun_val[0]-vert_dict[vert_ind].fun_val)))) 
            
    if sorted(distances, key=lambda item: item[2]):
        closest, dim, distance = sorted(distances, key=lambda item: item[2])[0] 
        return closest, dim, distance
    else: 
        return None
            
# saddle and minimum given as CritEdge and CritVertex objects
def cancel_one_critical_pair_min(saddle, minimum, MorseComplex, vert_dict, edge_dict, face_dict):
    """
    Cancels a saddle and minimum pair of the MorseComplex
        saddle: a CritEdge object
        minimum: a CritVertex object
        MorseComplex: a MorseComplex object, that will be changed accordingly
    """
    # remove saddle from connected faces
    MorseComplex.remove_edge_from_face_connections_and_delete_sepas(saddle.index)
    
    # remove separatrices with destination saddle
    for conn_max in saddle.connected_maxima:
        MorseComplex.remove_separatrix_from_face_to_edge(conn_max, saddle.index)
        
    # find new saddles and minimmum (can only be one minimum, 
    # since saddle can only connect to one vert twice or two vert once
    # and one vert already is the minimum to be cancelled
    new_saddles = set()
    for conn_sad in minimum.connected_saddles:
        if conn_sad != saddle.index:
            new_saddles.add(conn_sad)
    new_minimum = None
    for conn_min in saddle.connected_minima:
        if conn_min != minimum.index:
            new_minimum = conn_min
            
    # sanity check (should have found the new minimum)
    if new_minimum == None:
        raise ValueError('Did not find the new minimum to connect to! Shouldnt happen.')
            
    # find separatrix to be cancelled
    cancel_separatrix = None
    for sepa in saddle.paths:
        if sepa.destination == minimum.index:
            cancel_separatrix = sepa
    
    # add separatrix to MorseComplex with separatrix persistence
    # store reverse path with removed crit cells (otherwise duplicated)
    if cancel_separatrix != None:
        inverted_cropped_path = cancel_separatrix.path[1:-1][::-1]
        MorseComplex.add_separatrix_and_calculate_persistence(cancel_separatrix, vert_dict, edge_dict, face_dict)
    else:
        raise ValueError('Did not find the separatrix to be cancelled! Shouldnt happen.')
    
    # path to be added: inverted path from old_min to old_sad + path from old_sad to new min
    path_old_sad_new_min = MorseComplex.get_single_path_from_edge_to_vert(saddle.index, new_minimum)
    path_to_be_added = inverted_cropped_path + path_old_sad_new_min
    
    # reconnect from new sads to new min and add to connections
    MorseComplex.extend_new_sads_to_new_min(minimum.index, new_saddles, new_minimum, path_to_be_added)
    
    # remove old sad and old min from connections of new sads and new mins
    MorseComplex.remove_edge_from_vert_connections(saddle.index)
    MorseComplex.remove_vert_from_edge_connections(minimum.index)
    
    # now pop old saddle and old min from complex, as they have been cancelled and reconnected:
    MorseComplex.pop_edge(saddle.index)
    MorseComplex.pop_vert(minimum.index)
    
    return MorseComplex


def cancel_one_critical_pair_max(saddle, maximum, MorseComplex, vert_dict, edge_dict, face_dict):
    """
    Cancels a saddle and maximum pair of the MorseComplex
        saddle: a CritEdge object
        maximum: a CritFace object
        MorseComplex: a MorseComplex object, that will be changed accordingly
    """
    # remove saddle from connected vertices 
    # (dont have to remove sepa from sad to vert, as this sad will be cancelled anyways)
    MorseComplex.remove_edge_from_vert_connections(saddle.index)
        
    # find new saddles and maxima:
    # store separatrices to new saddles and set of indices for new maxmima
    new_saddles_sepa_set = set()
    for sepa in maximum.paths:
        if sepa.destination != saddle.index:
            new_saddles_sepa_set.add(sepa)
    new_maxima = set()
    for conn_max in saddle.connected_maxima:
        if conn_max != maximum.index:
            new_maxima.add(conn_max)
            
    # find separatrix to be cancelled
    cancel_separatrix = None
    for sepa in maximum.paths:
        if sepa.destination == saddle.index:
            cancel_separatrix = sepa
    
    # add separatrix to MorseComplex with separatrix persistence
    # store reverse path with removed crit cells (otherwise duplicated)
    if cancel_separatrix != None:
        inverted_cropped_path = cancel_separatrix.path[1:-1][::-1]
        MorseComplex.add_separatrix_and_calculate_persistence(cancel_separatrix, vert_dict, edge_dict, face_dict)
    else:
        raise ValueError('Did not find the separatrix to be cancelled! Shouldnt happen.')
            
    # reconnect from new maxs to new sads and add to connections
    MorseComplex.extend_new_maxs_to_new_sads(saddle.index, new_maxima, new_saddles_sepa_set, inverted_cropped_path)
            
    # remove old max and old sad from connections of new maxs and new sads
    MorseComplex.remove_face_from_edge_connections(maximum.index)
    MorseComplex.remove_edge_from_face_connections_and_delete_sepas(saddle.index)    
    
    # now pop old saddle and old min from complex, as they have been cancelled and reconnected:
    MorseComplex.pop_edge(saddle.index)
    MorseComplex.pop_face(maximum.index)
    
    return MorseComplex
            
def CancelCriticalPairs(MorseComplex, threshold, vert_dict, edge_dict, face_dict):
    start_eff = timeit.default_timer()

    CancelPairs = CancellationQueue()
    redMorseComplex = deepcopy(MorseComplex) 
    redMorseComplex.persistence = threshold
    # fill queue
    for crit_edge in redMorseComplex.CritEdges.values():
        closest_extremum = get_closest_extremum(crit_edge, redMorseComplex.CritVertices, redMorseComplex.CritFaces)
        if closest_extremum != None:
            index, dim, dist = closest_extremum
            if dist < threshold:
                CancelPairs.insert(tuple((dist, id(crit_edge), crit_edge)))
    
    # work down queue
    while CancelPairs.notEmpty():
        prio, obj_id, saddle = CancelPairs.pop_front()
        check = get_closest_extremum(saddle, redMorseComplex.CritVertices, redMorseComplex.CritFaces)
        if check != None:
            closest, dim, dist = check
            if dist <= CancelPairs.check_distance():
                if dim == 0:
                    redMorseComplex = cancel_one_critical_pair_min(saddle, redMorseComplex.CritVertices[closest], redMorseComplex, vert_dict, edge_dict, face_dict)
                elif dim == 2:
                    redMorseComplex = cancel_one_critical_pair_max(saddle, redMorseComplex.CritFaces[closest], redMorseComplex, vert_dict, edge_dict, face_dict)
            else:
                CancelPairs.insert(tuple((dist, obj_id, saddle)))
    
    time_eff = timeit.default_timer() - start_eff
    print('Time cancel critical points with ', threshold, " persistence: ", time_eff)
    return redMorseComplex
    