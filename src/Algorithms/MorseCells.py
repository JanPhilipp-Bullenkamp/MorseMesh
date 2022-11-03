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
            
    second_it = set()
    # now treat boundary points:
    for bd_ind in boundary_points:
        if vert_dict[bd_ind].label != -1:
            raise ValueError('Should not be possible to have a labelled vertex in the unlabelled bd_pts...')
        # check surrounding for other labels
        # neighb_labels is set of neighboring labels
        # neighb_ind is list of [elt, label] tuples of the neighboring labels
        neighb_labels, neighb_ind = vert_dict[bd_ind].has_neighbor_label(vert_dict)
        # Cases:
        # 1. no labelled neighbors -> surrounded by other bd pts -> add for second iteration and continue for now
        # 2. one neighbor label -> this point can be added to that label and marked as no bd
        # 3. more than one label -> add as neighbors and boundary of the cells
        if len(neighb_labels) == 0:
            second_it.add(bd_ind)
            continue
        elif len(neighb_labels) == 1:
            vert_dict[bd_ind].boundary = False
            vert_dict[bd_ind].label = neighb_ind[0][1]
            MorseComplex.MorseCells[neighb_ind[0][1]].vertices.add(bd_ind)
        else:
            counts = Counter([t[1] for t in neighb_ind])
            most_common_label = counts.most_common(1)[0][0]
            
            vert_dict[bd_ind].label = most_common_label
            MorseComplex.MorseCells[most_common_label].vertices.add(bd_ind)
            MorseComplex.MorseCells[most_common_label].boundary.add(bd_ind)
            
            for elt_ind, elt_label in neighb_ind:
                if elt_label != most_common_label:
                    MorseComplex.add_neighboring_cell_labels(most_common_label, bd_ind, elt_label, elt_ind)
    
    count_no_label_after_2it = 0
    # now treat boundary points in second iteration that had no labelled neighbors before:
    for bd_ind in second_it:
        if vert_dict[bd_ind].label != -1:
            raise ValueError('Should not be possible to have a labelled vertex in the unlabelled bd_pts...')
        # check surrounding for other labels
        # neighb_labels is set of neighboring labels
        # neighb_ind is list of [elt, label] tuples of the neighboring labels
        neighb_labels, neighb_ind = vert_dict[bd_ind].has_neighbor_label(vert_dict)
        # Cases:
        # 1. no labelled neighbors -> surrounded by other bd pts -> continue for now
        # 2. one neighbor label -> this point can be added to that label and marked as no bd
        # 3. more than one label -> add as neighbors and boundary of the cells
        if len(neighb_labels) == 0:
            count_no_label_after_2it += 1
            continue
        elif len(neighb_labels) == 1:
            vert_dict[bd_ind].boundary = False
            vert_dict[bd_ind].label = neighb_ind[0][1]
            MorseComplex.MorseCells[neighb_ind[0][1]].vertices.add(bd_ind)
        else:
            counts = Counter([t[1] for t in neighb_ind])
            most_common_label = counts.most_common(1)[0][0]
            
            vert_dict[bd_ind].label = most_common_label
            MorseComplex.MorseCells[most_common_label].vertices.add(bd_ind)
            MorseComplex.MorseCells[most_common_label].boundary.add(bd_ind)
            
            for elt_ind, elt_label in neighb_ind:
                if elt_label != most_common_label:
                    MorseComplex.add_neighboring_cell_labels(most_common_label, bd_ind, elt_label, elt_ind)
    
    if count_no_label_after_2it > 0:
        print("Have ", count_no_label_after_2it, " boundary points that could not be labelled in 2 iterations...")
    
    '''
    c=0        
    for vert_ind, vert in vert_dict.items():
        if vert.label == -1:
            c+=1
    print(c, "vert no label")
    print(len(boundary_points),"bd pts")
    '''
    
    # cleanup: 
    # mark that we have Morse cells for this complex and
    # need to reset boundary and labels as they are only part of the original mesh class
    MorseComplex._flag_MorseCells = True
    for vertex in vert_dict.values():
        vertex.boundary = False
        vertex.label = -1
        
    end_time = timeit.default_timer() -start_time
    print("Time get MorseCells for ", MorseComplex.persistence,"persistence: ", end_time)
    
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