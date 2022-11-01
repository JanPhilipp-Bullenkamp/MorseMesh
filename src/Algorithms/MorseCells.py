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
        for minimal_sepa in edge.paths:
            for count, elt in enumerate(minimal_sepa.path):
                # only need to add edge indices, cause the vertices in between are alread considered then
                if count%2 == 0:
                    #bd_points.update(edge_dict[elt].indices)
                    for vert in edge_dict[elt].indices:
                        bd_points.add(vert)
                        vert_dict[vert].boundary = True
                        
    # only add faces of the path, as edges should be contained that way already
    '''new: only one of the faces vertices added as bd'''
    for face in MorseComplex.CritFaces.values():
        for maximal_sepa in face.paths:
            for count, elt in enumerate(maximal_sepa.path):
                if count%2 == 0: # add all faces
                    ''' old: bd_points.update(face_dict[elt].indices)'''
                    #bd_points.add(face_dict[elt].get_max_fun_val_index())
                    #vert_dict[face_dict[elt].get_max_fun_val_index()].boundary = True
                    bd_points.update(face_dict[elt].indices)
                    for index in face_dict[elt].indices:
                        vert_dict[index].boundary = True
    return bd_points                

def get_MorseCells(MorseComplex, vert_dict, edge_dict, face_dict):
    start_time = timeit.default_timer()
    if MorseComplex._flag_MorseCells == True:
        print("Morse cells have been computed for this persistence already, but will be overwritten now")
        MorseComplex.MorseCells = {}
    
    # boundary_points stored in a set. contains all vert that are either boundary themselves
    # or contained in a boundary edge or face
    boundary_points = get_boundary(MorseComplex, vert_dict, edge_dict, face_dict)
    write_overlay_bd(boundary_points, vert_dict, "../../Data/bd_pts_finer_morsecomplex_"+str(MorseComplex.persistence))
    
    # start with label number 1, cause 0 is used for unlabeld points in gigamesh
    label = 1
    for vert_ind, vert in vert_dict.items():
        # .boundary is bool, .label is -1 by default and all labels than start at 1
        # dont want boundary or already labelled component as start
        if vert.boundary or vert.label != -1:
        #if vert_ind in boundary_points or vert_ind in visited:
            continue
        else:
            MorseComplex.MorseCells[label] = Cell(label)
            
            queue = set()
            queue.add(vert)
            
            while len(queue) != 0:
                # pop one elt from queue
                queue_elt = queue.pop()
                queue_elt.label = label
                queue_elt.boundary = False
                
                # add elts to queue if they are not boundary
                for ind in queue_elt.neighbors:
                    # Four cases:
                    # 1. no boundary and not labelled yet
                    # 2. already labelled (differently)
                    # 3. already labelled (same label)- nothing to do
                    # 4. boundary and not labelled yet
                    
                    # Case 1: just add to queue
                    if vert_dict[ind].boundary == False and vert_dict[ind].label == -1:
                        queue.add(vert_dict[ind])
                        
                    # Case 2: connect the two cells
                    elif vert_dict[ind].label != -1 and vert_dict[ind].label != label:
                        MorseComplex.add_neighboring_cell_labels(label, queue_elt.index, vert_dict[ind].label, ind)
                        
                    # Case 3: nothing to do, so skipped
                        
                    # Case 4: label boundary as current label and check surrounding of boundary vert
                    # for other labels (and add the cell connections accordingly)
                    elif vert_dict[ind].boundary and vert_dict[ind].label == -1:
                        vert_dict[ind].label = label
                        vert_dict[ind].boundary = False
                        MorseComplex.MorseCells[label].vertices.add(ind)
                        
                        # check surounding for other labels and connect
                        neighb_labels = vert_dict[ind].has_neighbor_label(vert_dict)
                        if len(neighb_labels) > 0:
                            for nei_vert_ind, nei_label in neighb_labels:
                                MorseComplex.add_neighboring_cell_labels(label, ind, nei_label, nei_vert_ind)
                           
                # add the popped element to the current Morse cell
                MorseComplex.MorseCells[label].vertices.add(queue_elt.index)
                
            label += 1
            
    
    boundary_points = MorseComplex.find_active_boundaries(boundary_points, vert_dict)
            
    for i in range(3):
        #boundary_points = MorseComplex.find_active_boundaries(boundary_points, vert_dict)
        for unlabelled_ind in boundary_points:
            if vert_dict[unlabelled_ind].label != -1:
                raise ValueError('Should not be possible to have a labelled vertex in the unlabelled bd_pts...')
            # check neighborhood 1-ring
            neighb_labels = vert_dict[unlabelled_ind].has_neighbor_label(vert_dict)

            if len(neighb_labels) > 0:
                # just take the first label (shouldnt matter to much)
                ind, label = neighb_labels[0]

                MorseComplex.MorseCells[label].vertices.add(unlabelled_ind)
                vert_dict[unlabelled_ind].boundary = False

                # need to check wether there are other labels as well and add to cell connection if necessary
                if len(neighb_labels) > 1:
                    for nei_vert_ind, nei_label in neighb_labels:
                        if nei_label != -1 and nei_label != label:
                            MorseComplex.add_neighboring_cell_labels(label, unlabelled_ind, nei_label, nei_vert_ind)

        boundary_points = MorseComplex.find_active_boundaries(boundary_points, vert_dict)
    
    if len(boundary_points) > 0:
        print("Have ",len(boundary_points), " unlabelled boundary points left!")
           
    '''
    while len(boundary_points) != 0:
        rem_bd = set()
        for left in boundary_points:
            labels = []
            for ind in vert_dict[left].neighbors:
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
    '''      
    #print("Bd pts",len(boundary_points))
    #write_overlay_bd(visited_bd, vert_dict, "test_bd_pts_raw")
    
    MorseComplex._flag_MorseCells = True
    
    
    # need to reset boundary and labels as they are only part of the original mesh class
    for vertex in vert_dict.values():
        vertex.boundary = False
        vertex.label = -1
    
    end_time = timeit.default_timer() -start_time
    print("Time get MorseCells for ", MorseComplex.persistence,"persistence: ", end_time)
    return MorseComplex.MorseCells


from .ConnectivityGraph import Graph
 
def create_SalientEdgeCellConnectivityGraph(MorseCells, salient_points, vert_dict, edge_dict):
    start_time = timeit.default_timer()
    
    # create graph with all labels
    ConnGraph = Graph()
    for cell in MorseCells.values():
        ConnGraph.add_ConnComp(cell)
        
    var = []
    for label, cell in MorseCells.items():
        for neighbor_label, points_here in cell.neighbors.items():
            # need points on both sides of the bopundary
            points_there = MorseCells[neighbor_label].neighbors[label]
            weight = compute_weight_saledge(points_here.union(points_there), salient_points)
            ConnGraph.add_weightedEdge(label, neighbor_label, weight)
        
    end_time = timeit.default_timer() -start_time
    print("Time get weighted ConnectivityGraph: ", end_time)
    return ConnGraph