from collections import Counter
import timeit

def get_boundary(MorseComplex, edge_dict, face_dict):
    bd_points = set()
    
    for vert_ind in MorseComplex.CritVertices.keys():
        bd_points.add(vert_ind)
    for edge in MorseComplex.CritEdges.values():
        minima = Counter(edge.connected_minima)
        for mini, nb in minima.items():
            if nb == 1:
                count = 0
                for elt in edge.paths[mini]:
                    # only need to add edge indices, cause the vertices in between are alread considered then
                    if count%2 == 0:
                        bd_points.update(edge_dict[elt].indices)
                    count+=1
            if nb == 2:
                for i in range(2):
                    count = 0
                    for elt in edge.paths[mini][i]:
                        # only need to add edge indices, cause the vertices in between are alread considered then
                        if count%2 == 0:
                            bd_points.update(edge_dict[elt].indices)
                        count+=1
                        
    for face in MorseComplex.CritFaces.values():
        saddles = Counter(face.connected_saddles)
        for sad, nb in saddles.items():
            if nb==1:
                count=0
                for elt in face.paths[sad]:
                    if count%2 == 0: #means face
                        bd_points.update(face_dict[elt].indices)
                    elif count%2 == 1: #means edge
                        bd_points.update(edge_dict[elt].indices)
                    count+=1
                        
    return bd_points

def get_neighbors(vert, vert_dict, edge_dict):
    neighbors_ind = set()
    for star_edge in vert.star["E"]:
        neighbors_ind.update(edge_dict[star_edge].indices)
        
    neighbors_ind.remove(vert.index)
    return neighbors_ind
                

def get_MorseCells(MorseComplex, vert_dict, edge_dict, face_dict):
    start_time = timeit.default_timer()
    # boundary_points stored in a set. contains all vert that are either boundary themselves
    # or contained in a boundary edge or face
    boundary_points = get_boundary(MorseComplex, edge_dict, face_dict)
    
    visited = set()
    MorseCells = {}
    cell_counter = 0
    for vert_ind, vert in vert_dict.items():
        if vert_ind in boundary_points or vert_ind in visited:
            continue
        else:
            MorseCells[cell_counter] = set()
            
            queue = set()
            queue.add(vert)
            
            while len(queue) != 0:
                # pop one elt from queue and find the neighbors
                queue_elt = queue.pop()
                neighbors_indices = get_neighbors(queue_elt, vert_dict, edge_dict)
                
                # add elts to queue if they are not boundary
                for ind in neighbors_indices:
                    if ind not in boundary_points and ind not in visited:
                        queue.add(vert_dict[ind])
                
                # add the popped element to the current Morse cell
                MorseCells[cell_counter].add(queue_elt.index)
                visited.add(queue_elt.index)
                
            cell_counter += 1
    # also store boundary points        
    MorseCells["boundary"] = boundary_points
    
    end_time = timeit.default_timer() -start_time
    print("Time get MorseCells: ", end_time)
    return MorseCells
    
    