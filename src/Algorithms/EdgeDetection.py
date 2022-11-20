##
# @file EdgeDetection.py
#
# @brief Contains functions for edge detection based on salient edges

def edge_detection(maxRedComp, thresh_high, thresh_low, vert_dict, edge_dict, face_dict):
    """! @brief Uses double threshold to get strong and weak edges and adds weak edges to strong
    edges if they are adjacent to a strong edge.
    
    @param maxRedComp A maximally reduced Morse Complex (needed for the Separatrices).
    @param thresh_high The high threshold for edges that will definitely be added.
    @param thresh_low  The weak threshold for edges that will be added of they are adjacent to a strong edge.
    @param vert_dict Dictionary containing all vertices.
    @param edge_dict Dictionary containing all edges.
    @param face_dict Dictionary containing all faces.
    
    @return strong_edge The double thresholded edges stored as a single set of vertex indices.
    """
    strong_edge, weak_edge = get_salient_edge_indices(maxRedComp, thresh_high, thresh_low, 
                                                      vert_dict, edge_dict, face_dict)

    if len(weak_edge) != 0:
        queue = []
        for ind in strong_edge:
            for nei in vert_dict[ind].neighbors:
                if nei in weak_edge:
                    queue.append(nei)
                    weak_edge.remove(nei)

        for elt in queue:
            strong_edge.add(elt)

        while len(queue) != 0:
            ind = queue.pop(0)
            for nei in vert_dict[ind].neighbors:
                if nei in weak_edge:
                    queue.append(nei)
                    strong_edge.add(nei)
                    weak_edge.remove(nei)
    return strong_edge

def get_salient_edge_indices(MorseComplex, thresh_high, thresh_low, 
                             vert_dict, edge_dict, face_dict):
    """! @brief Gets strong and weak edges based on Separatrix persistence.
    
    @details Separatrix persistence similar to Weinkauf and Günther (DOI: 10.1111/j.1467-8659.2009.01528.x)
https://www.researchgate.net/publication/227511709_Separatrix_Persistence_Extraction_of_Salient_Edges_on_Surfaces_Using_Topological_Methods

    @param MorseComplex A Morse Complex (needed for the Separatrices).
    @param thresh_high The high threshold for edges.
    @param thresh_low  The weak threshold for edges.
    @param vert_dict Dictionary containing all vertices.
    @param edge_dict Dictionary containing all edges.
    @param face_dict Dictionary containing all faces.
    
    @return strong_edge, weak edge Two sets of vertex indices containing the vertices of the separatrices that
    had Separatrix persistences above the high/low threshold.
    
    """
    strong_edge = set()
    weak_edge = set()
    for pers, sepa in MorseComplex.Separatrices:
        # add high persistence edge points
        if pers > thresh_high:
            if sepa.dimension == 1:
                for count, elt in enumerate(sepa.path):
                    if count%2 == 1: # so a vertex
                        strong_edge.add(elt)
                    if count%2 == 0: # so an edge
                        strong_edge.update(edge_dict[elt].indices)

            elif sepa.dimension == 2:
                for count, elt in enumerate(sepa.path):
                    if count%2 == 0: #so a face
                        strong_edge.update(face_dict[elt].indices)
                    if count%2 == 1: # so an edge
                        strong_edge.update(edge_dict[elt].indices)
        
        # add weak edge points (btw low and high threshold
        elif pers <= thresh_high and pers > thresh_low:
            if sepa.dimension == 1:
                for count, elt in enumerate(sepa.path):
                    if count%2 == 1: # so a vertex
                        weak_edge.add(elt)
                    if count%2 == 0: # so an edge
                        weak_edge.update(edge_dict[elt].indices)

            elif sepa.dimension == 2:
                for count, elt in enumerate(sepa.path):
                    if count%2 == 0: #so a face
                        weak_edge.update(face_dict[elt].indices)
                    if count%2 == 1: # so an edge
                        weak_edge.update(edge_dict[elt].indices)
    return strong_edge, weak_edge
            