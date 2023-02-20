from collections import Counter
from ..plot_data.plot_points_for_debugging import write_overlay_points

from .load_data.datastructures import Cell, MorseCells

def get_boundary(MorseComplex, vert_dict, edge_dict, face_dict):
    bd_points = set()
    
    for vert_ind in MorseComplex.CritVertices.keys():
        bd_points.add(vert_ind)
        vert_dict[vert_ind].boundary = True
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
                        bd_points.add(face_dict[elt].get_max_fun_val_index())
                        vert_dict[face_dict[elt].get_max_fun_val_index()].boundary = True
                    elif count%2 == 1: # add all edges
                        bd_points.add(edge_dict[elt].get_max_fun_val_index())
                        vert_dict[edge_dict[elt].get_max_fun_val_index()].boundary = True
            if nb==2:
                for i in range(2):
                    for count, elt in enumerate(face.paths[sad][i]):
                        if count%2 == 0: # add all faces
                            bd_points.add(face_dict[elt].get_max_fun_val_index())
                            vert_dict[face_dict[elt].get_max_fun_val_index()].boundary = True
                        elif count%2 == 1: # add all edges
                            bd_points.add(edge_dict[elt].get_max_fun_val_index())
                            vert_dict[edge_dict[elt].get_max_fun_val_index()].boundary = True
                        
    return bd_points                

def get_morse_cells(MorseComplex, vert_dict, edge_dict, face_dict, fill_neighborhood=True):
    if MorseComplex._flag_MorseCells == True:
        print("Morse cells have been computed for this persistence already, but will be overwritten now")
        MorseComplex.MorseCells = MorseCells()
        
    # boundary_points stored in a set. contains all vert that are either boundary themselves
    # or contained in a boundary edge or face
    boundary_points = get_boundary(MorseComplex, vert_dict, edge_dict, face_dict)
    #print("BD points: ", len(boundary_points))
    #write_overlay_points(boundary_points, vert_dict, "../../Data/test_objects/boundary_overlay001")
    
    # find cells and label without looking at boundary points
    label = 1 # start labelling with label 1, since label 0 is used for unlabeld points in gigamesh
    for vert in vert_dict.values():
        if vert.boundary or vert.label != -1:
            continue
        else:
            MorseComplex.MorseCells.add_cell(Cell(label))
            
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
                MorseComplex.MorseCells.add_vertex_to_label(label, queue_elt.index)
                
            # worked down the whole queue -> continue with next cell
            label +=1
    
    
    second_it = set()
    # now treat boundary points:
    for bd_ind in boundary_points:
        if vert_dict[bd_ind].label != -1:
            print("ind ", bd_ind, " has label ", vert_dict[bd_ind].label)
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
            MorseComplex.MorseCells.add_vertex_to_label(neighb_ind[0][1], bd_ind)
        else:
            counts = Counter([t[1] for t in neighb_ind])
            most_common_label = counts.most_common(1)[0][0]
            
            vert_dict[bd_ind].label = most_common_label
            MorseComplex.MorseCells.add_vertex_to_label(most_common_label, bd_ind)
            #MorseComplex.MorseCells[most_common_label].vertices.add(bd_ind)
            MorseComplex.MorseCells.add_boundary_to_label(most_common_label, bd_ind)
            #MorseComplex.MorseCells[most_common_label].boundary.add(bd_ind)
            
            for elt_ind, elt_label in neighb_ind:
                if elt_label != most_common_label:
                    MorseComplex.MorseCells.add_neighboring_cell_labels(most_common_label, bd_ind, elt_label, elt_ind)
    
    count_no_label_after_2it = 0
    third_it = set()
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
            third_it.add(bd_ind)
            count_no_label_after_2it += 1
            continue
        elif len(neighb_labels) == 1:
            vert_dict[bd_ind].boundary = False
            vert_dict[bd_ind].label = neighb_ind[0][1]
            MorseComplex.MorseCells.add_vertex_to_label(neighb_ind[0][1], bd_ind)
            #MorseComplex.MorseCells[neighb_ind[0][1]].vertices.add(bd_ind)
        else:
            counts = Counter([t[1] for t in neighb_ind])
            most_common_label = counts.most_common(1)[0][0]
            
            vert_dict[bd_ind].label = most_common_label
            MorseComplex.MorseCells.add_vertex_to_label(most_common_label, bd_ind)
            #MorseComplex.MorseCells[most_common_label].vertices.add(bd_ind)
            MorseComplex.MorseCells.add_boundary_to_label(most_common_label, bd_ind)
            #MorseComplex.MorseCells[most_common_label].boundary.add(bd_ind)
            
            for elt_ind, elt_label in neighb_ind:
                if elt_label != most_common_label:
                    MorseComplex.MorseCells.add_neighboring_cell_labels(most_common_label, bd_ind, elt_label, elt_ind)
                    
    count_no_label_after_3it = 0
    # now treat boundary points in second iteration that had no labelled neighbors before:
    for bd_ind in third_it:
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
            count_no_label_after_3it += 1
            continue
        elif len(neighb_labels) == 1:
            vert_dict[bd_ind].boundary = False
            vert_dict[bd_ind].label = neighb_ind[0][1]
            MorseComplex.MorseCells.add_vertex_to_label(neighb_ind[0][1], bd_ind)
            #MorseComplex.MorseCells[neighb_ind[0][1]].vertices.add(bd_ind)
        else:
            counts = Counter([t[1] for t in neighb_ind])
            most_common_label = counts.most_common(1)[0][0]
            
            vert_dict[bd_ind].label = most_common_label
            MorseComplex.MorseCells.add_vertex_to_label(most_common_label, bd_ind)
            #MorseComplex.MorseCells[most_common_label].vertices.add(bd_ind)
            MorseComplex.MorseCells.add_boundary_to_label(most_common_label, bd_ind)
            #MorseComplex.MorseCells[most_common_label].boundary.add(bd_ind)
            
            for elt_ind, elt_label in neighb_ind:
                if elt_label != most_common_label:
                    MorseComplex.MorseCells.add_neighboring_cell_labels(most_common_label, bd_ind, elt_label, elt_ind)
    
    if count_no_label_after_3it > 0:
        print("Have ", count_no_label_after_3it, " boundary points that could not be labelled in 3 iterations...")
    
    # cleanup: 
    # mark that we have Morse cells for this complex and
    # need to reset boundary and labels as they are only part of the original mesh class
    MorseComplex._flag_MorseCells = True
    for vertex in vert_dict.values():
        vertex.boundary = False
        vertex.label = -1
    return MorseComplex.MorseCells
