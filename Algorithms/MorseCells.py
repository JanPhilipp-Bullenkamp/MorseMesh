from collections import Counter
import timeit
'''
first part: get MorseCells
second part: get connectivity graph
'''

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
                        
    # try: add only first face and than only one of the edge points in each edge
    for face in MorseComplex.CritFaces.values():
        saddles = Counter(face.connected_saddles)
        for sad, nb in saddles.items():
            if nb==1:
                count=0
                for elt in face.paths[sad]:
                    if count == 0: #add only first face face
                        bd_points.update(face_dict[elt].indices)
                    elif count%2 == 1: #means edge
                        bd_points.add(next(iter(edge_dict[elt].indices)))
                    count+=1
            if nb==2:
                for i in range(2):
                    count=0
                    for elt in face.paths[sad][i]:
                        if count == 0: # add only first face face
                            bd_points.update(face_dict[elt].indices)
                        elif count%2 == 1: #means edge
                            bd_points.add(next(iter(edge_dict[elt].indices)))
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
            MorseCells[cell_counter] = {}
            MorseCells[cell_counter]["neighbors"] = {}  # only required later
            MorseCells[cell_counter]["boundary"] = set()
            MorseCells[cell_counter]["set"] = set()
            
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
                    elif ind in boundary_points and ind not in visited:
                        MorseCells[cell_counter]["set"].add(ind)
                        MorseCells[cell_counter]["boundary"].add(ind)
                        visited.add(ind)
                    elif ind not in boundary_points and ind in visited:
                        # if it is in set, all good
                        # if it is not in set: must be visited in another cell already, 
                        # therefore the queue elt popped was a boundary
                        if ind not in MorseCells[cell_counter]["set"]:
                            MorseCells[cell_counter]["boundary"].add(queue_elt.index)
                
                # add the popped element to the current Morse cell
                MorseCells[cell_counter]["set"].add(queue_elt.index)
                visited.add(queue_elt.index)
                
            cell_counter += 1
    # also store boundary points /// not necessary anymore?        
    #MorseCells["boundary"] = boundary_points
    
    end_time = timeit.default_timer() -start_time
    print("Time get MorseCells: ", end_time)
    return MorseCells


from .ConnectivityGraph import ConnComp, Graph

def find_label(vert, MorseCells):
    for label, cell in MorseCells.items():
        if vert in cell["set"]:
            return label
    # if not contained in any MorseCell error
    #raise ValueError('Vertex', vert, 'was not found in any MorseCell set! Shouldnt happen')
    #print('Vertex', vert, 'was not found in any MorseCell set! Shouldnt happen')
    return -1
    
def fill_cell_neighbors(MorseCells, vert_dict, edge_dict):
    ct=0
    for label, cell in MorseCells.items():
        # check all boundary points 
        for bd_point in cell["boundary"]:
            neighbors = get_neighbors(vert_dict[bd_point], vert_dict, edge_dict)
            # for all neighbors of bd points, check which label they have and add new labels to neighbors, 
            # also storing the boundary points from both sides (for connectivity calculation later)
            for ind in neighbors:
                if ind not in cell["set"]:
                    ind_label = find_label(ind, MorseCells)
                    if ind_label != -1:
                        if ind_label not in cell["neighbors"].keys():
                            cell["neighbors"][ind_label] = set()
                            cell["neighbors"][ind_label].add(bd_point)
                            cell["neighbors"][ind_label].add(ind)
                        else:
                            cell["neighbors"][ind_label].add(bd_point)
                            cell["neighbors"][ind_label].add(ind)
                            '''
                            TODO maybe also add the other way around, just in case
                            but should be equal both ways in theory
                            '''
                            
                    else:
                        ct +=1
    print("Nb of not found labels: ", ct)
    return MorseCells

def compute_weight(points, vert_dict):
    fun_vals = []
    for ind in points:
        fun_vals.append(vert_dict[ind].fun_val)
    return sum(fun_vals)/len(fun_vals)
    
def create_CellConnectivityGraph(MorseCells, vert_dict, edge_dict):
    start_time = timeit.default_timer()
    
    MorseCells = fill_cell_neighbors(MorseCells, vert_dict, edge_dict)
    
    # create graph with all labels
    ConnGraph = Graph()
    for label in MorseCells.keys():
        cc = ConnComp(label)
        ConnGraph.add_ConnComp(cc)
        
    for label, cell in MorseCells.items():
        for neighbor_label, points in cell["neighbors"].items():
            weight = compute_weight(points, vert_dict)
            ConnGraph.add_weightedEdge(label, neighbor_label, weight)
        
    end_time = timeit.default_timer() -start_time
    print("Time get weighted ConnectivityGraph: ", end_time)
    return ConnGraph