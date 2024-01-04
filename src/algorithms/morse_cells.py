"""
    MorseMesh
    Copyright (C) 2023  Jan Philipp Bullenkamp

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from collections import Counter

from .datastructures import Cell, MorseCells

def get_boundary(MorseComplex, vert_dict, edge_dict, face_dict):
    bd_points = set()
    
    for vert_ind in MorseComplex.CritVertices.keys():
        bd_points.add(vert_ind)
        vert_dict[vert_ind].boundary = True
        
    def edge_path_to_bd_points(path):
        for count, elt in enumerate(path):
            # only need to add edge indices, cause the vertices in 
            # between are alread considered then
            if count%2 == 0:
                bd_points.update(edge_dict[elt].indices)
                for ind in edge_dict[elt].indices:
                    vert_dict[ind].boundary = True
        
    for edge in MorseComplex.CritEdges.values():
        minima = Counter(edge.connected_minima)
        for mini, nb in minima.items():
            if nb == 1:
                edge_path_to_bd_points(edge.paths[mini])
            if nb == 2:
                for i in range(2):
                    edge_path_to_bd_points(edge.paths[mini][i])
                        
    def face_path_to_bd_points(path):
        for count, elt in enumerate(path):
            if count%2 == 0: # add all faces
                bd_points.add(face_dict[elt].get_max_fun_val_index())
                vert_dict[face_dict[elt].get_max_fun_val_index()].boundary = True
            elif count%2 == 1: # add all edges
                bd_points.add(edge_dict[elt].get_max_fun_val_index())
                vert_dict[edge_dict[elt].get_max_fun_val_index()].boundary = True
                
    # only add faces of the path, as edges should be contained that way already
    '''new: only one of the faces added as bd '''
    for face in MorseComplex.CritFaces.values():
        saddles = Counter(face.connected_saddles)
        for sad, nb in saddles.items():
            if nb==1:
                face_path_to_bd_points(face.paths[sad])
            if nb==2:
                for i in range(2):
                    face_path_to_bd_points(face.paths[sad][i])
                        
    return bd_points            

def find_closest_label(start_index, vert_dict):
    labels = []
    unlabelled = set()
    visited = set()
    unlabelled.add(start_index)
    prev_length = -1
    while (len(visited) != prev_length and len(labels) == 0):
        prev_length = len(visited)
        index = unlabelled.pop()
        visited.add(index)
        for ind in vert_dict[index].neighbors:
            if ind in unlabelled or ind in visited:
                continue
            if vert_dict[ind].label == -1:
                unlabelled.add(ind)
            else:
                labels.append(vert_dict[ind].label)
                visited.add(ind)
    if len(labels) == 0:
        raise ValueError("Have a patch of unlabelled points not connected to any label!")
    
    label_occurences = Counter(labels)
    return label_occurences.most_common(1)[0][0]
         

def get_morse_cells(MorseComplex, vert_dict, edge_dict, face_dict):
    if MorseComplex._flag_MorseCells == True:
        print("Morse cells have been computed for this persistence "
              "already, but will be overwritten now.")
        MorseComplex.MorseCells = MorseCells()
        
    # boundary_points stored in a set. contains all vert that are either 
    # boundary themselves or contained in a boundary edge or face
    boundary_points = get_boundary(MorseComplex, vert_dict, edge_dict, face_dict)
    
    # find cells and label without looking at boundary points
    label = 1 # start labelling with label 1
    for vert in vert_dict.values():
        if vert.boundary or vert.label != -1:
            continue
        
        MorseComplex.MorseCells.add_cell(Cell(label))
        queue = set()
        queue.add(vert)
        
        while len(queue) != 0:
            # pop one elt from queue
            queue_elt = queue.pop()
            queue_elt.label = label
            
            for ind in queue_elt.neighbors:
                # only treat non boundary points:
                if vert_dict[ind].boundary:
                    continue
                # two cases: 1. unlabelled; 2. already labeled
                # so if not unlabelled or the same label, sth went wrong
                if vert_dict[ind].label == -1:
                    queue.add(vert_dict[ind])
                elif vert_dict[ind].label != label:
                    raise ValueError("Trying to find Morse cells, but seem to "
                                        "have an open cell... "
                                        "(dont know what went wrong)")
            # add popped elt to current Morse cell
            MorseComplex.MorseCells.add_vertex_to_label(label, queue_elt.index)
        # worked down the whole queue -> continue with next cell
        label +=1
            
    for bd_ind in boundary_points:
        if vert_dict[bd_ind].label != -1:
            print("ind ", bd_ind, " has label ", vert_dict[bd_ind].label)
            raise ValueError("Should not be possible to have a labelled "
                             "vertex in the unlabelled bd_pts...")
        label = find_closest_label(bd_ind, vert_dict)
        vert_dict[bd_ind].label = label
        MorseComplex.MorseCells.add_vertex_to_label(label, bd_ind)
        
    for bd_ind in boundary_points:
        # check surrounding for other labels
        # neighb_labels is set of neighboring labels
        # neighb_ind is list of [elt, label] tuples of the neighboring labels
        own_label = vert_dict[bd_ind].label
        neighb_labels, neighb_ind = vert_dict[bd_ind].has_neighbor_label(vert_dict)
        if len(neighb_labels) > 0:
            for elt, nei_label in neighb_ind:
                MorseComplex.MorseCells.add_neighboring_cell_labels(own_label, bd_ind,
                                                                    nei_label, elt)
    
    # cleanup: 
    # mark that we have Morse cells for this complex and
    # need to reset boundary and labels as they are only part of the original mesh class
    MorseComplex._flag_MorseCells = True
    for vertex in vert_dict.values():
        vertex.boundary = False
        vertex.label = -1
    return MorseComplex.MorseCells
