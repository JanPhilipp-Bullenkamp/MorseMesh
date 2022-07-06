from collections import Counter
import timeit
from .plot_bdpts import write_overlay_bd

from .weight_metrics import compute_weight_saledge, compute_weight_normals, compute_weight_normalvariance
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
                for count, elt in enumerate(edge.paths[mini]):
                    # only need to add edge indices, cause the vertices in between are alread considered then
                    if count%2 == 0:
                        bd_points.update(edge_dict[elt].indices)
            if nb == 2:
                for i in range(2):
                    for count, elt in enumerate(edge.paths[mini][i]):
                        # only need to add edge indices, cause the vertices in between are alread considered then
                        if count%2 == 0:
                            bd_points.update(edge_dict[elt].indices)
                        
    # only add faces of the path, as edges should be contained that way already
    for face in MorseComplex.CritFaces.values():
        saddles = Counter(face.connected_saddles)
        for sad, nb in saddles.items():
            if nb==1:
                for count, elt in enumerate(face.paths[sad]):
                    if count%2 == 0: # add all faces
                        bd_points.update(face_dict[elt].indices)
            if nb==2:
                for i in range(2):
                    for count, elt in enumerate(face.paths[sad][i]):
                        if count%2 == 0: # add all faces
                            bd_points.update(face_dict[elt].indices)
                        
    return bd_points

def get_neighbors(vert, vert_dict, edge_dict):
    neighbors_ind = set()
    for star_edge in vert.star["E"]:
        neighbors_ind.update(edge_dict[star_edge].indices)
        
    neighbors_ind.remove(vert.index)
    return neighbors_ind
                

def get_MorseCells(MorseComplex, vert_dict, edge_dict, face_dict, fill_neighborhood=True):
    start_time = timeit.default_timer()
    # boundary_points stored in a set. contains all vert that are either boundary themselves
    # or contained in a boundary edge or face
    boundary_points = get_boundary(MorseComplex, edge_dict, face_dict)
    
    visited = set()
    visited_bd = set()
    MorseCells = {}
    # start with label number 1, cause 0 is used for unlabeld points in gigamesh
    cell_counter = 1
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
                        visited_bd.add(ind)
                        visited.add(ind)
                        boundary_points.remove(ind)
                    elif ind not in boundary_points and ind in visited:
                        # if it is in set, all good
                        # if it is not in set: must be visited in another cell already, 
                        # therefore the queue elt popped was a boundary
                        if ind not in MorseCells[cell_counter]["set"]:
                            MorseCells[cell_counter]["boundary"].add(queue_elt.index)
                            visited_bd.add(queue_elt.index)
                
                # add the popped element to the current Morse cell
                MorseCells[cell_counter]["set"].add(queue_elt.index)
                visited.add(queue_elt.index)
                
            cell_counter += 1
            
    
    while len(boundary_points) != 0:
        rem_bd = set()
        for left in boundary_points:
            neighbors = get_neighbors(vert_dict[left], vert_dict, edge_dict)
            labels = []
            for ind in neighbors:
                if ind not in boundary_points:
                    for label, val in MorseCells.items():
                        if ind in val["set"]:
                            labels.append(label)
            if len(labels) > 0:
                counts = Counter(labels)
                max_label = [label for label, nb in sorted(counts.items(), key=lambda item: item[1])][-1]
                MorseCells[max_label]["set"].add(left)
                MorseCells[max_label]["boundary"].add(left)
                visited_bd.add(left)
                rem_bd.add(left)
            
        for elt in rem_bd:
            boundary_points.remove(elt)
            
    #print("Bd pts",len(boundary_points))
    #write_overlay_bd(visited_bd, vert_dict, "test_bd_pts")
    end_time = timeit.default_timer() -start_time
    print("Time get MorseCells for ", MorseComplex.persistence,"persistence: ", end_time)
    
    if fill_neighborhood:
        start_time2 = timeit.default_timer()

        MorseCells = fill_cell_neighbors(MorseCells, vert_dict, edge_dict)

        end_time2 = timeit.default_timer() -start_time2
        print("Time fill neighbors for MorseCells: ", end_time2)
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
    pts = set()
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
                            pts.add(bd_point)
                            pts.add(ind)
                        else:
                            cell["neighbors"][ind_label].add(bd_point)
                            cell["neighbors"][ind_label].add(ind)
                            pts.add(bd_point)
                            pts.add(ind)
                            '''
                            TODO maybe also add the other way around, just in case
                            but should be equal both ways in theory
                            '''
                            
                    else:
                        ct +=1
    #write_overlay_bd(pts, vert_dict, "test_fill_cell_neighbors")
    #print("Nb of not found labels: ", ct)
    return MorseCells
 
def create_SalientEdgeCellConnectivityGraph(MorseCells, salient_points, vert_dict, edge_dict):
    start_time = timeit.default_timer()
    
    ''' MOVED to get_Morse cells, as that is only called once for each persistence, 
        sal edge creation is called multiple times usually. 
        Was very computation heavy i think (badly implemented probably)'''
    #MorseCells = fill_cell_neighbors(MorseCells, vert_dict, edge_dict) 
    
    # create graph with all labels
    ConnGraph = Graph()
    for label in MorseCells.keys():
        cc = ConnComp(label)
        ConnGraph.add_ConnComp(cc)
        
    var = []
    for label, cell in MorseCells.items():
        for neighbor_label, points in cell["neighbors"].items():
            weight = compute_weight_saledge(points, salient_points)
            ConnGraph.add_weightedEdge(label, neighbor_label, weight)
        
    end_time = timeit.default_timer() -start_time
    print("Time get weighted ConnectivityGraph: ", end_time)
    return ConnGraph