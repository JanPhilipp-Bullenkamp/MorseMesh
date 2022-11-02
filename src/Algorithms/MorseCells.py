from collections import Counter
import timeit
from .plot_bdpts import write_overlay_bd

from .weight_metrics import compute_weight_saledge, compute_weight_normals, compute_weight_normalvariance
from .LoadData.Datastructure import Cell
'''
first part: get MorseCells
second part: get connectivity graph
'''

def get_boundary(MorseComplex, vert_dict, edge_dict, face_dict):
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
                        for ind in edge_dict[elt].indices:
                            vert_dict[ind].boundary = True
            if nb == 2:
                for i in range(2):
                    for count, elt in enumerate(edge.paths[mini][i]):
                        # only need to add edge indices, cause the vertices in between are alread considered then
                        if count%2 == 0:
                            bd_points.update(edge_dict[elt].indices)
                            for ind in edge_dict[elt].indices:
                                vert_dict[ind].boundary = True
                        
    # only add faces of the path, as edges should be contained that way already
    '''new: only one of the faces added as bd '''
    for face in MorseComplex.CritFaces.values():
        saddles = Counter(face.connected_saddles)
        for sad, nb in saddles.items():
            if nb==1:
                for count, elt in enumerate(face.paths[sad]):
                    if count%2 == 0: # add all faces
                        ''' old: bd_points.update(face_dict[elt].indices)'''
                        #bd_points.add(next(iter(face_dict[elt].indices)))
                        bd_points.update(face_dict[elt].indices)
                        for ind in face_dict[elt].indices:
                            vert_dict[ind].boundary = True
            if nb==2:
                for i in range(2):
                    for count, elt in enumerate(face.paths[sad][i]):
                        if count%2 == 0: # add all faces
                            ''' old: bd_points.update(face_dict[elt].indices)'''
                            #bd_points.add(next(iter(face_dict[elt].indices)))
                            bd_points.update(face_dict[elt].indices)
                            for ind in face_dict[elt].indices:
                                vert_dict[ind].boundary = True
                        
    return bd_points                

def get_MorseCells(MorseComplex, vert_dict, edge_dict, face_dict, fill_neighborhood=True):
    start_time = timeit.default_timer()
    if MorseComplex._flag_MorseCells == True:
        print("Morse cells have been computed for this persistence already, but will be overwritten now")
        MorseComplex.MorseCells = {}
        
    # boundary_points stored in a set. contains all vert that are either boundary themselves
    # or contained in a boundary edge or face
    boundary_points = get_boundary(MorseComplex, vert_dict, edge_dict, face_dict)
    
    # find cells and label without looking at boundary points
    label = 1 # start labelling with label 1, since label 0 is used for unlabeld points in gigamesh
    for vert_ind, vert in vert_dict.items():
        if vert.boundary or vert.label != -1:
            continue
        else:
            MorseComplex.MorseCells[label] = Cell(label)
            
            queue = set()
            queue.add(vert)
            
            while len(queue) != 0:
                # pop one elt from queue
                queue_elt = queue.pop()
                queue_elt.label = label
                
                for ind in queue_elt.neighbors:
                    # only treat non boundary points:
                    if vert_dict[ind].boundary == False:
                        # two cases: 1. unlabelled; 2. already labeled
                        # so if not unlabelled or the same label, sth went wrong
                        if vert_dict[ind].label == -1:
                            queue.add(vert_dict[ind])
                        elif vert_dict[ind].label != label:
                            raise ValueError("Trying to find Morse cells, but seem to have an open cell... (dont know what went wrong)")
                # add popped elt to current Morse cell
                MorseComplex.MorseCells[label].vertices.add(queue_elt.index)
                
            # worked down the whole queue -> continue with next cell
            label +=1
    c=0        
    for vert_ind, vert in vert_dict.items():
        if vert.label == -1:
            c+=1
    print(c, "vert no label")
    print(len(boundary_points),"bd pts")
    
    # cleanup: 
    # mark that we have Morse cells for this complex and
    # need to reset boundary and labels as they are only part of the original mesh class
    MorseComplex._flag_MorseCells = True
    for vertex in vert_dict.values():
        vertex.boundary = False
        vertex.label = -1
        
    
    '''
    visited = set()
    visited_bd = set()
    # start with label number 1, cause 0 is used for unlabeld points in gigamesh
    label = 1
    for vert_ind, vert in vert_dict.items():
        if vert_ind in boundary_points or vert_ind in visited:
            continue
        else:
            MorseComplex.MorseCells[label] = Cell(label)
            
            queue = set()
            queue.add(vert)
            
            while len(queue) != 0:
                # pop one elt from queue
                queue_elt = queue.pop()
                
                # add elts to queue if they are not boundary
                for ind in queue_elt.neighbors:
                    if ind not in boundary_points and ind not in visited:
                        queue.add(vert_dict[ind])
                    elif ind in boundary_points and ind not in visited:
                        MorseComplex.MorseCells[label].vertices.add(ind)
                        MorseComplex.MorseCells[label].boundary.add(ind)
                        visited_bd.add(ind)
                        visited.add(ind)
                        boundary_points.remove(ind)
                    elif ind not in boundary_points and ind in visited:
                        # if it is in set, all good
                        # if it is not in set: must be visited in another cell already, 
                        # therefore the queue elt popped was a boundary
                        if ind not in MorseComplex.MorseCells[label].vertices:
                            MorseComplex.MorseCells[label].boundary.add(queue_elt.index)
                            visited_bd.add(queue_elt.index)
                
                # add the popped element to the current Morse cell
                MorseComplex.MorseCells[label].vertices.add(queue_elt.index)
                visited.add(queue_elt.index)
                
            label += 1
            
    
    while len(boundary_points) != 0:
        rem_bd = set()
        for left in boundary_points:
            labels = []
            for ind in vert_dict[left].neighbors:
                if ind not in boundary_points:
                    for label_v, val in MorseComplex.MorseCells.items():
                        if ind in val.vertices:
                            labels.append(label_v)
            if len(labels) > 0:
                counts = Counter(labels)
                max_label = [label_v for label_v, nb in sorted(counts.items(), key=lambda item: item[1])][-1]
                MorseComplex.MorseCells[max_label].vertices.add(left)
                MorseComplex.MorseCells[max_label].boundary.add(left)
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

        MorseComplex.MorseCells = fill_cell_neighbors(MorseComplex.MorseCells, vert_dict, edge_dict)

        end_time2 = timeit.default_timer() -start_time2
        print("Time fill neighbors for MorseCells: ", end_time2)
    '''
    return MorseComplex.MorseCells


from .ConnectivityGraph import ConnComp, Graph

def find_label(vert, MorseCells):
    for label, cell in MorseCells.items():
        if vert in cell.vertices:
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
        for bd_point in cell.boundary:
            # for all neighbors of bd points, check which label they have and add new labels to neighbors, 
            # also storing the boundary points from both sides (for connectivity calculation later)
            for ind in vert_dict[bd_point].neighbors:
                if ind not in cell.vertices:
                    ind_label = find_label(ind, MorseCells)
                    if ind_label != -1:
                        if ind_label not in cell.neighbors.keys():
                            cell.neighbors[ind_label] = set()
                            cell.neighbors[ind_label].add(bd_point)
                            cell.neighbors[ind_label].add(ind)
                            cell.neighborlist.append(ind_label)
                            pts.add(bd_point)
                            pts.add(ind)
                        else:
                            cell.neighbors[ind_label].add(bd_point)
                            cell.neighbors[ind_label].add(ind)
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
    
    
    # create graph with all labels
    ConnGraph = Graph()
    for cell in MorseCells.values():
        ConnGraph.add_ConnComp(cell)
        
    var = []
    for label, cell in MorseCells.items():
        for neighbor_label, points in cell.neighbors.items():
            weight = compute_weight_saledge(points, salient_points)
            ConnGraph.add_weightedEdge(label, neighbor_label, weight)
        
    end_time = timeit.default_timer() -start_time
    print("Time get weighted ConnectivityGraph: ", end_time)
    return ConnGraph