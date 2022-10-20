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
            # take absolute value btw the two highest vertices of edge and face respectively
            distances.append(tuple((face_ind, 2, abs(face_dict[face_ind].fun_val[0]-crit_edge.fun_val[0])))) 
        elif nb > 2:
            raise ValueError("Mesh has irregularities! Please clean it before. CritFace", face_ind, " has ", nb, " connections to CritEdge ", crit_edge.index, " so there are edges in the mesh that connect 3 triangles together.")
                               
    # now add distances to all minima
    vert_counter = Counter(crit_edge.connected_minima)
    for vert_ind, nb in vert_counter.items():
        # cannot cancel loops, so only if there is a single path we can add the extremum
        if nb==1:
            # take absolute value btw the highest vertex of edge and the value of the vertex
            distances.append(tuple((vert_ind, 0, abs(crit_edge.fun_val[0]-vert_dict[vert_ind].fun_val))))
        elif nb > 2:
            raise ValueError("Dont know what could cause this, but CritVert", vert_ind, " has ", nb, " connections to CritEdge ", crit_edge.index, " which should combinatorally not be possible...")
            
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

def cancel_one_critical_pair_min_old(saddle, minimum, MorseComplex, vert_dict, edge_dict, face_dict):
    """
    Cancels a saddle and minimum pair of the MorseComplex
        saddle: a CritEdge object
        minimum: a CritVertex object
        MorseComplex: a MorseComplex object, that will be changed accordingly
    """
    #list of the maximal function values connected to saddle that is about to be cancelled
    #we require the minimum of this list for separatrix persistence later
    #maximal_values_list = []
    # cut paths between old saddle and its connected maxima, as we cancel the saddle
    # saddle can be twice in the connection list, but paths would be stored under one key only,
    # therefore pop key and both will be removed (need None argument for second iteration)
    for conn_max in saddle.connected_maxima:
        #maximal_values_list.append(MorseComplex.CritFaces[conn_max].fun_val[0])
        MorseComplex.CritFaces[conn_max].connected_saddles.remove(saddle.index)
        for sep in MorseComplex.CritFaces[conn_max].paths:
            if sep.destination == saddle.index:
                MorseComplex.CritFaces[conn_max].paths.remove(sep)
        #MorseComplex.CritFaces[conn_max].paths.pop(saddle.index, None)
        
    # find new saddles and minima:
    new_saddles = []
    for conn_sad in minimum.connected_saddles:
        if conn_sad != saddle.index:
            new_saddles.append(conn_sad)
    new_minima = []
    for conn_min in saddle.connected_minima:
        if conn_min != minimum.index:
            new_minima.append(conn_min)
            
    # save original path for separatrix persistence for later:
    for sepa in saddle.paths:
        if sepa.destination == minimum.index:
            original_path = sepa.path
            minimal_line_persistence = sepa.calculate_separatrix_persistence(vert_dict, edge_dict, face_dict)
    
    minimal_line = Separatrix(saddle.index, minimum.index, 1, original_path, minimal_line_persistence)
    MorseComplex.Separatrices.append(tuple((minimal_line_persistence, minimal_line)))
    
    # save the inverted path between sadle and minimum:
    # reverse path and remove first and last elt (min and saddle otherwise duplicated)
    inverted_cropped_path = original_path[1:-1][::-1]
    
    new_saddles_counts = Counter(new_saddles)
    new_minima_counts = Counter(new_minima)
    for new_sad, nb_sad in new_saddles_counts.items():
        # save paths from new saddle to minimum 
        # (want to pop the minimum from the new saddle paths afterwards)
        #new_saddle_paths = MorseComplex.CritEdges[new_sad].paths[minimum.index]
        c = 0
        new_saddles_paths = []
       
        for sep in MorseComplex.CritEdges[new_sad].paths:
            if sep.destination == minimum.index:
                new_saddles_paths.append(sep.path)
                MorseComplex.CritEdges[new_sad].connected_minima.remove(minimum.index)
                c+=1
                
        for sep in MorseComplex.CritEdges[new_sad].paths:
            if sep.destination == minimum.index:
                MorseComplex.CritEdges[new_sad].paths.remove(sep)
        if c != nb_sad:
            raise ValueError("didnt find as many separatrices as nb_saddles connected, so sth went wrong... nb_sad was ",nb_sad, " and found ", c, "sepas")
                
        # now loop over new minima to connect new paths and remove saddle from new min connections
        for new_min, nb_min in new_minima_counts.items():
            # nb_min should be one, as the saddle can only connect to two minima, or one minimum twice 
            # and one is the one we want to cancel to, so it should be one path two 2 minima
            if nb_min == 1:
                # new saddle had one connection to old min:
                # then: add new min to new saddle connection and take the single path:
                # new_sad-old_min + old_min-old_sad(reversed) + old_sad-new_min 
                for old_sep in saddle.paths:
                    if old_sep.destination == new_min:
                        new_min_path = old_sep.path

                if nb_sad == 1:
                    MorseComplex.CritEdges[new_sad].connected_minima.append(new_min)
                    MorseComplex.CritVertices[new_min].connected_saddles.append(new_sad)

                    new_sep = Separatrix(new_sad, new_min, 1, new_saddles_paths[0] + inverted_cropped_path + new_min_path)
                    MorseComplex.CritEdges[new_sad].paths.append(new_sep)

                    #if new_min not in MorseComplex.CritEdges[new_sad].paths.keys():
                    #   MorseComplex.CritEdges[new_sad].paths[new_min] = new_saddle_paths + inverted_cropped_path + saddle.paths[new_min]
                    #else:
                    #    MorseComplex.CritEdges[new_sad].paths[new_min] = [MorseComplex.CritEdges[new_sad].paths[new_min], new_saddle_paths + inverted_cropped_path + saddle.paths[new_min]]


                # new saddle had 2 connections to old min, therefore also 2 conn to new min
                elif nb_sad == 2:
                    # add to connection twice
                    for k in range(nb_sad):
                        MorseComplex.CritEdges[new_sad].connected_minima.append(new_min)
                        MorseComplex.CritVertices[new_min].connected_saddles.append(new_sad)
                        # add both paths to the paths to new_min (only differ in the first part from new_sad to old_min)
                        new_sep = Separatrix(new_sad, new_min, 1, new_saddles_paths[k] + inverted_cropped_path + new_min_path)
                        MorseComplex.CritEdges[new_sad].paths.append(new_sep)

            else:
                print("Saddle should only be able to connect to two minima or one minimum twice!")
                raise RuntimeError
            
        # remove all instances of minimum from new saddles connections and paths
        #for i in range(nb_sad):
            #MorseComplex.CritEdges[new_sad].connected_minima.remove(minimum.index)
            #MorseComplex.CritEdges[new_sad].paths.pop(minimum.index, None)
            
        
    
    # needs to be put out oif the new saddles loop, otherwise repeated for each sadddle
    for new_min, nb_min in new_minima_counts.items():
        for j in range(nb_min):
            MorseComplex.CritVertices[new_min].connected_saddles.remove(saddle.index)
                
    # now pop old saddle and old min from complex, as they have been cancelled and reconnected:
    MorseComplex.CritEdges.pop(saddle.index)
    MorseComplex.CritVertices.pop(minimum.index)
    
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


def cancel_one_critical_pair_max_old(saddle, maximum, MorseComplex, vert_dict, edge_dict, face_dict):
    """
    Cancels a saddle and maximum pair of the MorseComplex
        saddle: a CritEdge object
        maximum: a CritFace object
        MorseComplex: a MorseComplex object, that will be changed accordingly
    """
    #list of the minimal function values connected to saddle that is about to be cancelled
    #we require the maximum of this list for separatrix persistence later
    #minimal_values_list = []
    # cut paths between old saddle and its connected minima, as we cancel the saddle
    # saddle can be twice in the connection list
    for conn_min in saddle.connected_minima:
        #minimal_values_list.append(MorseComplex.CritVertices[conn_min].fun_val)
        MorseComplex.CritVertices[conn_min].connected_saddles.remove(saddle.index)
        
    # find new saddles and maxima:
    new_saddles = []
    for conn_sad in maximum.connected_saddles:
        if conn_sad != saddle.index:
            new_saddles.append(conn_sad)
    new_maxima = []
    for conn_max in saddle.connected_maxima:
        if conn_max != maximum.index:
            new_maxima.append(conn_max)
            
    # save original path for separatrix persistence for later:
    for sepa in maximum.paths:
        if sepa.destination == saddle.index:
            original_path = sepa.path
            maximal_line_persistence = sepa.calculate_separatrix_persistence(vert_dict, edge_dict, face_dict)
    #maximal_line_persistence = compute_max_sad_persistence(original_path, edge_dict, face_dict)
    
    maximal_line = Separatrix(maximum.index, saddle.index, 2, original_path, maximal_line_persistence)
    MorseComplex.Separatrices.append(tuple((maximal_line_persistence, maximal_line)))
    
    # save the inverted path between sadle and maximum:
    # reverse path and remove first and last elt (max and saddle otherwise duplicated)
    inverted_cropped_path = original_path[1:-1][::-1]
    
    new_saddles_counts = Counter(new_saddles)
    new_maxima_counts = Counter(new_maxima)
    for new_max, nb_max in new_maxima_counts.items():
        # save paths from new maximum to saddle 
        # (want to pop the saddle from the new max paths afterwards)
        for sepa in MorseComplex.CritFaces[new_max].paths:
            if sepa.destination == saddle.index:
                new_max_paths = sepa.path
                MorseComplex.CritFaces[new_max].paths.remove(sepa)
        #new_max_paths = MorseComplex.CritFaces[new_max].paths[saddle.index]
        if nb_max != 1:
            raise ValueError("nb max should be 1, but was: ",nb_max)
        # remove all instances of saddle from new max connections and paths
        for i in range(nb_max):
            MorseComplex.CritFaces[new_max].connected_saddles.remove(saddle.index)
            '''done in previous loop'''
            #MorseComplex.CritFaces[new_max].paths.pop(saddle.index, None)
            
        # now loop over new saddles to connect new paths and remove maximum from new saddle connections
        for new_sad, nb_sad in new_saddles_counts.items():
            # need cases:
            # 1. one path new_max-old_sad and one path old_max-new_sad
            # 2. two paths new_max-old_sad and one path old_max-new_sad
            # 3. one path new_max-old_sad and two paths old_max-new_sad
            # 4. two paths new_max-old_sad and two paths old_max-new_sad
            if nb_sad == 1 and nb_max == 1:
                MorseComplex.CritFaces[new_max].connected_saddles.append(new_sad)
                MorseComplex.CritEdges[new_sad].connected_maxima.append(new_max)
                for last_sep_part in maximum.paths:
                    if last_sep_part.destination == new_sad:
                        last_path = last_sep_part.path
                new_sep = Separatrix(new_max, new_sad, 2, new_max_paths + inverted_cropped_path + last_path)
                MorseComplex.CritFaces[new_max].paths.append(new_sep)
                #if new_sad not in MorseComplex.CritFaces[new_max].paths.keys():
                #    MorseComplex.CritFaces[new_max].paths[new_sad] = new_max_paths + inverted_cropped_path + maximum.paths[new_sad]
                #else:
                #    MorseComplex.CritFaces[new_max].paths[new_sad] = [MorseComplex.CritFaces[new_max].paths[new_sad], new_max_paths + inverted_cropped_path + maximum.paths[new_sad]]
                
            elif nb_sad == 1 and nb_max == 2:
                raise ValueError("nb max shouldt be able to be 2...")
                for p in range(2):
                    MorseComplex.CritFaces[new_max].connected_saddles.append(new_sad)
                    MorseComplex.CritEdges[new_sad].connected_maxima.append(new_max)
                # add two paths: first part from new_max to saddle is different
                MorseComplex.CritFaces[new_max].paths[new_sad] = [new_max_paths[0] + inverted_cropped_path + maximum.paths[new_sad], new_max_paths[1] + inverted_cropped_path + maximum.paths[new_sad]]
                
            elif nb_sad == 2 and nb_max == 1:
                p=0
                for last_sep_part in maximum.paths:
                    if last_sep_part.destination == new_sad:
                        MorseComplex.CritFaces[new_max].connected_saddles.append(new_sad)
                        MorseComplex.CritEdges[new_sad].connected_maxima.append(new_max)
                        last_path = last_sep_part.path
                        new_sep = Separatrix(new_max, new_sad, 2, new_max_paths + inverted_cropped_path + last_path)
                        MorseComplex.CritFaces[new_max].paths.append(new_sep)
                        p+=1
                if p!=2:
                    raise ValueError("Should have found two sepas, but found: ", p)
                
                #for p in range(2):
                #    MorseComplex.CritFaces[new_max].connected_saddles.append(new_sad)
                #    MorseComplex.CritEdges[new_sad].connected_maxima.append(new_max)
                # add two paths: last part from max to new_sad is different
                #MorseComplex.CritFaces[new_max].paths[new_sad] = [new_max_paths + inverted_cropped_path + maximum.paths[new_sad][0], new_max_paths + inverted_cropped_path + maximum.paths[new_sad][1]]
                
            elif nb_sad == 2 and nb_max == 2:
                raise ValueError("nb max shouldt be able to be 2...")
                '''
                ! We reduce this case!
                instead of the 4 possibilities, we only take two (should topologically be equal, due to mod 2 or so ? 
                Problem for all 4 would be the paths, as we store them such that we expect max 2 paths between two critical simplices
                '''
                for p in range(2):
                    MorseComplex.CritFaces[new_max].connected_saddles.append(new_sad)
                    MorseComplex.CritEdges[new_sad].connected_maxima.append(new_max)
                # add two paths: last part from max to new_sad and first part from new_max to sad are different,
                # we take one of each to reduce the cases from 4 to 2
                MorseComplex.CritFaces[new_max].paths[new_sad] = [new_max_paths[0] + inverted_cropped_path + maximum.paths[new_sad][0], new_max_paths[1] + inverted_cropped_path + maximum.paths[new_sad][1]]
                
            else:
                print("More than 2 paths between new_max and saddle or max and new_saddle, shouldnt be possible!")
                #raise RuntimeError
                
    # needs to be put out of new_max loop, otherwise repeated to often
    for new_sad, nb_sad in new_saddles_counts.items():
        for j in range(nb_sad):
            MorseComplex.CritEdges[new_sad].connected_maxima.remove(maximum.index)
                
    # now pop old saddle and old min from complex, as they have been cancelled and reconnected:
    MorseComplex.CritEdges.pop(saddle.index)
    MorseComplex.CritFaces.pop(maximum.index)
    
    return MorseComplex
            
def CancelCriticalPairs(MorseComplex, threshold, vert_dict, edge_dict, face_dict):
    start_eff = timeit.default_timer()

    redMorseComplex = deepcopy(MorseComplex) 
    redMorseComplex.persistence = threshold
    
    # reset Morse cells and Betti numbers if necessary
    if redMorseComplex._flag_MorseCells:
        redMorseComplex.MorseCells = {}
        redMorseComplex._flag_MorseCells = False
    if redMorseComplex._flag_BettiNumbers:
        redMorseComplex.BettiNumbers = None
        redMorseComplex._flag_BettiNumbers = False
        
    
    CancelPairs = CancellationQueue()
    
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
                start2 = timeit.default_timer()
                if dim == 0:
                    redMorseComplex = cancel_one_critical_pair_min_old(saddle, redMorseComplex.CritVertices[closest], redMorseComplex, vert_dict, edge_dict, face_dict)
                elif dim == 2:
                    redMorseComplex = cancel_one_critical_pair_max_old(saddle, redMorseComplex.CritFaces[closest], redMorseComplex, vert_dict, edge_dict, face_dict)
                time2= timeit.default_timer() - start2
                if time2 > 1:
                    print("Cancel saddle ",saddle, " with ", closest, " took: ", time2)
            else:
                CancelPairs.insert(tuple((dist, obj_id, saddle)))
    
    time_eff = timeit.default_timer() - start_eff
    print('Time cancel critical points with ', threshold, " persistence: ", time_eff)
    return redMorseComplex
    