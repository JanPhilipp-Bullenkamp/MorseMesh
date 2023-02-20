from collections import Counter
import numpy as np
from copy import deepcopy

from .cancellation_queue import CancellationQueue
from .load_data.datastructures import Separatrix, MorseCells

def get_closest_extremum(crit_edge, crit_faces_dict, vert_dict, edge_dict, face_dict, salient_edge_pts=None):
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
        if salient_edge_pts != None:
            for closest, dim, distance in sorted(distances, key=lambda item: item[2]):
                if dim == 0:
                    if len(get_indices(crit_edge.paths[closest], edge_dict, face_dict, dim=1).intersection(salient_edge_pts)) < 3:
                        return closest, dim, distance
                elif dim == 2:
                    if len(get_indices(crit_faces_dict[closest].paths[crit_edge.index], edge_dict, face_dict, dim=2).intersection(salient_edge_pts)) < 3:
                        return closest, dim, distance
                    
            return None
        else:    
            closest, dim, distance = sorted(distances, key=lambda item: item[2])[0] 
            return closest, dim, distance
    else: 
        return None
    
def get_indices(path, edge_dict, face_dict, dim):
    indices = set()
    # edge-vert separatrix -> only need to add edge indices
    if dim == 1:
        for i, elt in enumerate(path):
            if i%2 == 0:
                indices.update(edge_dict[elt].indices)
    # face-edge separatrix -> only need to add face indices        
    elif dim == 2:
        for i, elt in enumerate(path):
            if i%2 == 0:
                indices.update(face_dict[elt].indices)
    return indices
    
#def compute_min_sad_persistence(path, min_maximum_val, vert_dict, edge_dict):
def compute_min_sad_persistence(path, vert_dict, edge_dict):
    distances = []
    for i, elt in enumerate(path):
        if i%2 == 0:
            distances.append(edge_dict[elt].fun_val[0]) #min_maximum_val
        elif i%2 == 1:
            distances.append(vert_dict[elt].fun_val) #min_maximum_val
    return sum(distances)/len(distances)

#def compute_max_sad_persistence(path, max_minimum_val, edge_dict, face_dict):
def compute_max_sad_persistence(path, edge_dict, face_dict):
    distances = []
    for i, elt in enumerate(path):
        if i%2 == 0:
            distances.append(face_dict[elt].fun_val[0]) #max_minimum_val
        elif i%2 == 1:
            distances.append(edge_dict[elt].fun_val[0]) #max_minimum_val
    return sum(distances)/len(distances)
            
# saddle and minimum given as CritEdge and CritVertex objects
def cancel_one_critical_pair_min(saddle, minimum, MorseComplex, vert_dict, edge_dict, face_dict):
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
        if saddle.index in MorseComplex.CritFaces[conn_max].paths.keys():
            if saddle.connected_maxima.count(conn_max) == 2:
                for i in range(2):
                    max_cancel_line_persistence = compute_max_sad_persistence(MorseComplex.CritFaces[conn_max].paths[saddle.index][i], edge_dict, face_dict)
                    max_cancel_line = Separatrix(conn_max, saddle.index, 2, MorseComplex.CritFaces[conn_max].paths[saddle.index][i], max_cancel_line_persistence)
                    MorseComplex.Separatrices.append(tuple((max_cancel_line_persistence, max_cancel_line)))
            else:
                max_cancel_line_persistence = compute_max_sad_persistence(MorseComplex.CritFaces[conn_max].paths[saddle.index], edge_dict, face_dict)
                max_cancel_line = Separatrix(conn_max, saddle.index, 2, MorseComplex.CritFaces[conn_max].paths[saddle.index], max_cancel_line_persistence)
                MorseComplex.Separatrices.append(tuple((max_cancel_line_persistence, max_cancel_line)))
        MorseComplex.CritFaces[conn_max].paths.pop(saddle.index, None)
        
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
    original_path = saddle.paths[minimum.index]
    minimal_line_persistence = compute_min_sad_persistence(original_path, vert_dict, edge_dict)
    
    minimal_line = Separatrix(saddle.index, minimum.index, 1, original_path, minimal_line_persistence)
    MorseComplex.Separatrices.append(tuple((minimal_line_persistence, minimal_line)))
    
    # save the inverted path between sadle and minimum:
    # reverse path and remove first and last elt (min and saddle otherwise duplicated)
    inverted_cropped_path = saddle.paths[minimum.index][1:-1][::-1]
    
    new_saddles_counts = Counter(new_saddles)
    new_minima_counts = Counter(new_minima)
    for new_sad, nb_sad in new_saddles_counts.items():
        # save paths from new saddle to minimum 
        # (want to pop the minimum from the new saddle paths afterwards)
        new_saddle_paths = MorseComplex.CritEdges[new_sad].paths[minimum.index]
        
        # remove all instances of minimum from new saddles connections and paths
        for i in range(nb_sad):
            MorseComplex.CritEdges[new_sad].connected_minima.remove(minimum.index)
            MorseComplex.CritEdges[new_sad].paths.pop(minimum.index, None)
            
        # now loop over new minima to connect new paths and remove saddle from new min connections
        for new_min, nb_min in new_minima_counts.items():
            # nb_min should be one, as the saddle can only connect to two minima, or one minimum twice 
            # and one is the one we want to cancel to, so it should be one path two 2 minima
            if nb_min == 1:
                # new saddle had one connection to old min:
                # then: add new min to new saddle connection and take the single path:
                # new_sad-old_min + old_min-old_sad(reversed) + old_sad-new_min 
                if nb_sad == 1:
                    MorseComplex.CritEdges[new_sad].connected_minima.append(new_min)
                    MorseComplex.CritVertices[new_min].connected_saddles.append(new_sad)
                    if new_min not in MorseComplex.CritEdges[new_sad].paths.keys():
                        MorseComplex.CritEdges[new_sad].paths[new_min] = new_saddle_paths + inverted_cropped_path + saddle.paths[new_min]
                    else:
                        MorseComplex.CritEdges[new_sad].paths[new_min] = [MorseComplex.CritEdges[new_sad].paths[new_min], new_saddle_paths + inverted_cropped_path + saddle.paths[new_min]]
                    
                
                # new saddle had 2 connections to old min, therefore also 2 conn to new min
                elif nb_sad == 2:
                    # add to connection twice
                    for k in range(nb_sad):
                        MorseComplex.CritEdges[new_sad].connected_minima.append(new_min)
                        MorseComplex.CritVertices[new_min].connected_saddles.append(new_sad)
                    # add both paths to the paths to new_min (only differ in the first part from new_sad to old_min)
                    MorseComplex.CritEdges[new_sad].paths[new_min] = [new_saddle_paths[0] + inverted_cropped_path + saddle.paths[new_min], new_saddle_paths[1] + inverted_cropped_path + saddle.paths[new_min]]
                    
            else:
                print("Saddle should only be able to connect to two minima or one minimum twice!")
                raise RuntimeError
    
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
    #list of the minimal function values connected to saddle that is about to be cancelled
    #we require the maximum of this list for separatrix persistence later
    #minimal_values_list = []
    # cut paths between old saddle and its connected minima, as we cancel the saddle
    # saddle can be twice in the connection list
    for conn_min in saddle.connected_minima:
        #minimal_values_list.append(MorseComplex.CritVertices[conn_min].fun_val)
        if conn_min in saddle.paths.keys():
            if saddle.connected_minima.count(conn_min) == 2:
                for i in range(2):
                    min_cancel_line_persistence = compute_min_sad_persistence(saddle.paths[conn_min][i], vert_dict, edge_dict)
                    min_cancel_line = Separatrix(saddle.index, conn_min, 1, saddle.paths[conn_min][i], min_cancel_line_persistence)
                    MorseComplex.Separatrices.append(tuple((min_cancel_line_persistence, min_cancel_line)))
            else:
                min_cancel_line_persistence = compute_min_sad_persistence(saddle.paths[conn_min], vert_dict, edge_dict)
                min_cancel_line = Separatrix(saddle.index, conn_min, 1, saddle.paths[conn_min], min_cancel_line_persistence)
                MorseComplex.Separatrices.append(tuple((min_cancel_line_persistence, min_cancel_line)))
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
    original_path = maximum.paths[saddle.index]
    maximal_line_persistence = compute_max_sad_persistence(original_path, edge_dict, face_dict)
    
    maximal_line = Separatrix(maximum.index, saddle.index, 2, original_path, maximal_line_persistence)
    MorseComplex.Separatrices.append(tuple((maximal_line_persistence, maximal_line)))
    
    # save the inverted path between sadle and maximum:
    # reverse path and remove first and last elt (max and saddle otherwise duplicated)
    inverted_cropped_path = maximum.paths[saddle.index][1:-1][::-1]
    
    new_saddles_counts = Counter(new_saddles)
    new_maxima_counts = Counter(new_maxima)
    for new_max, nb_max in new_maxima_counts.items():
        # save paths from new maximum to saddle 
        # (want to pop the saddle from the new max paths afterwards)
        new_max_paths = MorseComplex.CritFaces[new_max].paths[saddle.index]
        
        # remove all instances of saddle from new max connections and paths
        for i in range(nb_max):
            MorseComplex.CritFaces[new_max].connected_saddles.remove(saddle.index)
            MorseComplex.CritFaces[new_max].paths.pop(saddle.index, None)
            
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
                if new_sad not in MorseComplex.CritFaces[new_max].paths.keys():
                    MorseComplex.CritFaces[new_max].paths[new_sad] = new_max_paths + inverted_cropped_path + maximum.paths[new_sad]
                else:
                    MorseComplex.CritFaces[new_max].paths[new_sad] = [MorseComplex.CritFaces[new_max].paths[new_sad], new_max_paths + inverted_cropped_path + maximum.paths[new_sad]]
                
            elif nb_sad == 1 and nb_max == 2:
                for p in range(2):
                    MorseComplex.CritFaces[new_max].connected_saddles.append(new_sad)
                    MorseComplex.CritEdges[new_sad].connected_maxima.append(new_max)
                # add two paths: first part from new_max to saddle is different
                MorseComplex.CritFaces[new_max].paths[new_sad] = [new_max_paths[0] + inverted_cropped_path + maximum.paths[new_sad], new_max_paths[1] + inverted_cropped_path + maximum.paths[new_sad]]
                
            elif nb_sad == 2 and nb_max == 1:
                for p in range(2):
                    MorseComplex.CritFaces[new_max].connected_saddles.append(new_sad)
                    MorseComplex.CritEdges[new_sad].connected_maxima.append(new_max)
                # add two paths: last part from max to new_sad is different
                MorseComplex.CritFaces[new_max].paths[new_sad] = [new_max_paths + inverted_cropped_path + maximum.paths[new_sad][0], new_max_paths + inverted_cropped_path + maximum.paths[new_sad][1]]
                
            elif nb_sad == 2 and nb_max == 2:
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
                raise RuntimeError
                
    # needs to be put out of new_max loop, otherwise repeated to often
    for new_sad, nb_sad in new_saddles_counts.items():
        for j in range(nb_sad):
            MorseComplex.CritEdges[new_sad].connected_maxima.remove(maximum.index)
                
    # now pop old saddle and old min from complex, as they have been cancelled and reconnected:
    MorseComplex.CritEdges.pop(saddle.index)
    MorseComplex.CritFaces.pop(maximum.index)
    
    return MorseComplex
            
def cancel_critical_pairs(MorseComplex, threshold, vert_dict, edge_dict, face_dict, salient_edge_pts=None):
    redMorseComplex = deepcopy(MorseComplex) 
    redMorseComplex.persistence = threshold
    
    # reset Morse cells, Segmentation and Betti numbers if necessary
    if redMorseComplex._flag_MorseCells:
        redMorseComplex.MorseCells = MorseCells()
        redMorseComplex._flag_MorseCells = False
        redMorseComplex.Segmentations = {}
    if redMorseComplex._flag_BettiNumbers:
        redMorseComplex.BettiNumbers = None
        redMorseComplex.partners = None
        redMorseComplex._flag_BettiNumbers = False
    
    
    CancelPairs = CancellationQueue()
    
    # fill queue
    for crit_edge in redMorseComplex.CritEdges.values():
        closest_extremum = get_closest_extremum(crit_edge, redMorseComplex.CritFaces, vert_dict, edge_dict, face_dict, salient_edge_pts=salient_edge_pts)
        if closest_extremum != None:
            index, dim, dist = closest_extremum
            if dist < threshold:
                CancelPairs.insert(tuple((dist, id(crit_edge), crit_edge)))
    
    # work down queue
    while CancelPairs.notEmpty():
        prio, obj_id, saddle = CancelPairs.pop_front()
        check = get_closest_extremum(saddle, redMorseComplex.CritFaces, vert_dict, edge_dict, face_dict, salient_edge_pts=salient_edge_pts)
        if check != None:
            closest, dim, dist = check
            if dist <= CancelPairs.check_distance():
                if dim == 0:
                    redMorseComplex = cancel_one_critical_pair_min(saddle, redMorseComplex.CritVertices[closest], redMorseComplex, vert_dict, edge_dict, face_dict)
                elif dim == 2:
                    redMorseComplex = cancel_one_critical_pair_max(saddle, redMorseComplex.CritFaces[closest], redMorseComplex, vert_dict, edge_dict, face_dict)
            else:
                CancelPairs.insert(tuple((dist, obj_id, saddle)))
    return redMorseComplex
    