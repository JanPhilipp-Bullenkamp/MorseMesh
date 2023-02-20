##
# @file extract_morse_complex.py
#
# @brief Contains the extract_morse_complex function described in Robins et al. (DOI: 10.1109/TPAMI.2011.95)
# https://www.researchgate.net/publication/51131057_Theory_and_Algorithms_for_Constructing_Discrete_Morse_Complexes_from_Grayscale_Digital_Images
#
# @section libraries_extract_morse_complex Libraries/Modules
# - numpy standard library
# - Datastructure module (local)
#   - need CritVertex, CritEdge, CritFace, MorseComplex structures
# - Tree module (local)
#   - need Tree for path finding to get adjacency between critical cells in the MS complex

import numpy as np
from .tree import Tree, Node

from .load_data.datastructures import CritVertex, CritEdge, CritFace, MorseComplex

def potential_cells(p, cell, vert_dict, edge_dict):
    """! @brief Gives the faces(vert/edges) of a cell needed for finding a path from critical cell to critical cell.
    
    @param p Dimension of the cell we are looking at (1 if edge, 2 for face).
    @ param cell The cell we want to get potential faces of.
    @param vert_dict Dictionary containing all vertices.
    @param edges_dict Dictionary containing all edges.
    
    @return pot_alphas Returns a set of possible next cells.
    """
    pot_alphas = set()
    if p == 1:
        for ind in cell.indices:
            pot_alphas.add(ind)
    else:
        for ind in cell.indices:
            for edge_ind in vert_dict[ind].star["E"]:
                if edge_dict[edge_ind].indices.issubset(cell.indices):
                    pot_alphas.add(edge_ind)
                    
    return pot_alphas

def extract_morse_complex(vert_dict, edge_dict, face_dict, V12, V23, C):
    """! @brief The function described in Robins et al. 2011, that returns a Morse Complex.
    
    @details Loops over all critical edges and faces and follows the paths indicated by the gradient field 
    that start at each critical cell. This gives the adjacencies of the cells and their paths between each 
    other, giving us the Morse Complex as well as the Separatrices and thereby represents the surface in 
    a reduced skelton.
    
    @param vert_dict The dictionary containing all vertices.
    @param edge_dict The dictionary containing all edges.
    @param face_dict The dictionary containing all faces.
    @param C The dictionary containing all critical vertices, edges and faces.
    @param V12 The dictionary containing all pairings between edges and vertices.
    @param V23 The dictionary containing all pairings between faces and edges.
    
    @return initial_complex The initial (unreduced) Morse complex.
    """
    initial_complex = MorseComplex()
    
    for C_index in C[0]:
        initial_complex.add_vertex(vert_dict[C_index])
    for p in (1,2):
        for C_index in C[p]:
            if p == 1:
                crit_cell = CritEdge(edge_dict[C_index])
            else:
                crit_cell = CritFace(face_dict[C_index])

            paths_tree = Tree(C_index) ## contains Qbfs list for breadth first search
            pot_alphas = potential_cells(p, crit_cell, vert_dict, edge_dict)

            for alpha in pot_alphas:
                if (alpha in V12.keys() and p==1) or (alpha in V23.keys() and p==2):
                    child_node = Node(alpha,"root")
                    paths_tree.Qbfs.append(tuple((alpha, child_node)))
                    paths_tree.addNode(child_node)
                elif alpha in C[p-1]:
                    child_node = Node(alpha, "root", end_flag=True)
                    # add to facelists:
                    # p=1: connect min and saddle, min should already exist in complex
                    # p=2: connect max and saddle, saddle should already exist in complex
                    if p == 1:
                        initial_complex.CritVertices[alpha].connected_saddles.append(C_index)
                        crit_cell.connected_minima.append(alpha)
                    else:
                        initial_complex.CritEdges[alpha].connected_maxima.append(C_index)
                        crit_cell.connected_saddles.append(alpha)
                        
                    # add to Paths
                    paths_tree.addNode(child_node)
                    paths_tree.addEnd(child_node)

            while len(paths_tree.Qbfs) != 0:
                alpha, parent_node = paths_tree.Qbfs.pop(-1)
                if p == 1:
                    beta = V12[alpha]
                else:
                    beta = V23[alpha]
                    
                child_node = Node(beta, parent_node)
                parent_node.addNode(child_node)
                if p == 1:
                    pot_deltas = potential_cells(p, edge_dict[beta], vert_dict, edge_dict)
                else:
                    pot_deltas = potential_cells(p, face_dict[beta], vert_dict, edge_dict)
                    
                pot_deltas.discard(alpha)

                for delta in pot_deltas:
                    if delta in C[p-1]:
                        next_child_node = Node(delta, child_node, end_flag=True)
                        # add to facelists:
                        # p=1: connect min and saddle, min should already exist in complex
                        # p=2: connect max and saddle, saddle should already exist in complex
                        if p == 1:
                            initial_complex.CritVertices[delta].connected_saddles.append(C_index)
                            crit_cell.connected_minima.append(delta)
                        else:
                            initial_complex.CritEdges[delta].connected_maxima.append(C_index)
                            crit_cell.connected_saddles.append(delta)
                            
                        # add to Paths
                        child_node.addNode(next_child_node)
                        paths_tree.addEnd(next_child_node)

                    elif (delta in V12.keys() and p==1) or (delta in V23.keys() and p==2):
                        next_child_node = Node(delta, child_node)
                        paths_tree.Qbfs.append(tuple((delta, next_child_node)))

            # find paths from end nodes to start C_index
            for itnode in paths_tree.pathends:
                path = []
                while itnode.parent != "root":
                    path.append(itnode.data)
                    itnode = itnode.parent
                # still need to add the node with parent "root" and the root node itself, so:
                path.append(itnode.data)
                path.append(C_index)
                face = path[0]
                if face not in crit_cell.paths.keys():
                    crit_cell.paths[face] = path[::-1]
                else:
                    crit_cell.paths[face] = [crit_cell.paths[face], path[::-1]]
                
            if p == 1:
                initial_complex.CritEdges[C_index] = crit_cell
            else:
                initial_complex.CritFaces[C_index] = crit_cell 
    return initial_complex