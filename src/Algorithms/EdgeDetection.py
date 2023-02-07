##
# @file EdgeDetection.py
#
# @brief Contains functions for edge detection based on salient edges

def ridge_detection(maxRedComp, thresh_high: float, thresh_low: float, vert_dict: dict, edge_dict: dict, face_dict: dict, min_length: int = 1, max_length: int=None):
    """! @brief Uses double threshold to get strong and weak ridges and adds weak ridges to strong
    ridges if they are adjacent to a strong ridge.
    
    @param maxRedComp A maximally reduced Morse Complex (needed for the Separatrices).
    @param thresh_high The high threshold for ridges that will definitely be added.
    @param thresh_low  The weak threshold for ridges that will be added of they are adjacent to a strong ridge.
    @param vert_dict Dictionary containing all vertices.
    @param edge_dict Dictionary containing all edges.
    @param face_dict Dictionary containing all faces.
    @param min_length Minimum length each separatrix should have: Default 1
    @param max_length Maximum length each separatrix should have: Default None.
    
    @return strong_edge The double thresholded edges stored as a single set of vertex indices.
    """
    strong_ridge, weak_ridge = get_salient_sepa_indices(maxRedComp, thresh_high, thresh_low, 
                                                      edge_dict, face_dict, mode=1,
                                                      min_length=min_length, max_length=max_length)

    if len(weak_ridge) != 0:
        queue = []
        for ind in strong_ridge:
            for nei in vert_dict[ind].neighbors:
                if nei in weak_ridge:
                    queue.append(nei)
                    weak_ridge.remove(nei)

        for elt in queue:
            strong_ridge.add(elt)

        while len(queue) != 0:
            ind = queue.pop(0)
            for nei in vert_dict[ind].neighbors:
                if nei in weak_ridge:
                    queue.append(nei)
                    strong_ridge.add(nei)
                    weak_ridge.remove(nei)
    return strong_ridge

def valley_detection(maxRedComp, thresh_high: float, thresh_low: float, vert_dict: dict, edge_dict: dict, face_dict: dict, min_length: int=1, max_length: int=None):
    """! @brief Uses double threshold to get strong and weak valleys and adds weak valleys to strong
    valleys if they are adjacent to a strong valley.
    
    @param maxRedComp A maximally reduced Morse Complex (needed for the Separatrices).
    @param thresh_high The high threshold for valleys that will definitely be added.
    @param thresh_low  The weak threshold for valleys that will be added of they are adjacent to a strong valley.
    @param vert_dict Dictionary containing all vertices.
    @param edge_dict Dictionary containing all edges.
    @param face_dict Dictionary containing all faces.
    @param min_length Minimum length each separatrix should have: Default 1
    @param max_length Maximum length each separatrix should have: Default None.
    
    @return strong_valley The double thresholded valleys stored as a single set of vertex indices.
    """
    strong_valley, weak_valley = get_salient_sepa_indices(maxRedComp, thresh_high, thresh_low, 
                                                          edge_dict, face_dict, mode=2,
                                                          min_length=min_length, max_length=max_length)

    if len(weak_valley) != 0:
        queue = []
        for ind in strong_valley:
            for nei in vert_dict[ind].neighbors:
                if nei in weak_valley:
                    queue.append(nei)
                    weak_valley.remove(nei)

        for elt in queue:
            strong_valley.add(elt)

        while len(queue) != 0:
            ind = queue.pop(0)
            for nei in vert_dict[ind].neighbors:
                if nei in weak_valley:
                    queue.append(nei)
                    strong_valley.add(nei)
                    weak_valley.remove(nei)
    return strong_valley

def get_salient_sepa_indices(MorseComplex, thresh_high: float, thresh_low: float, edge_dict: dict, 
                             face_dict: dict, mode: int = 1, min_length: int=1, max_length: int=None):
    """! @brief Gets strong and weak edges based on Separatrix persistence.
    
    @details Separatrix persistence similar to Weinkauf and Günther (DOI: 10.1111/j.1467-8659.2009.01528.x)
https://www.researchgate.net/publication/227511709_Separatrix_Persistence_Extraction_of_Salient_Edges_on_Surfaces_Using_Topological_Methods

    @param MorseComplex A Morse Complex (needed for the Separatrices).
    @param thresh_high The high threshold for edges.
    @param thresh_low  The weak threshold for edges.
    @param edge_dict Dictionary containing all edges.
    @param face_dict Dictionary containing all faces.
    @param mode Int giving operation mode: 1 for only ridges, 2 for only valleys or 3 for both.
    @param min_length Minimum length each separatrix should have: Default 1
    @param max_length Maximum length each separatrix should have: Default None.
    
    @return strong_edge, weak edge Two sets of vertex indices containing the vertices of the separatrices that
    had Separatrix persistences above the high/low threshold.
    
    """
    strong_edge = set()
    weak_edge = set()
    if max_length == None:
        max_length = float('inf')
    for pers, sepa in MorseComplex.Separatrices:
        if len(sepa.path) > min_length and len(sepa.path) < max_length:
            # add high persistence edge points
            if mode == 1: # ridge detection
                if pers > thresh_high:
                    add_sepa_to_edge(sepa, strong_edge, edge_dict, face_dict)
                
                # add weak edge points (btw low and high threshold
                elif pers <= thresh_high and pers > thresh_low:
                    add_sepa_to_edge(sepa, weak_edge, edge_dict, face_dict)

            elif mode == 2: # valley detection
                if pers < -thresh_high:
                    add_sepa_to_edge(sepa, strong_edge, edge_dict, face_dict)
                
                # add weak edge points (btw low and high threshold
                elif pers >= -thresh_high and pers < -thresh_low:
                    add_sepa_to_edge(sepa, weak_edge, edge_dict, face_dict)
    return strong_edge, weak_edge

def add_sepa_to_edge(sepa, edge: set, edge_dict: dict, face_dict: dict):
    if sepa.dimension == 1:
        for count, elt in enumerate(sepa.path):
            if count%2 == 1: # so a vertex
                edge.add(elt)
            if count%2 == 0: # so an edge
                edge.update(edge_dict[elt].indices)

    elif sepa.dimension == 2:
        for count, elt in enumerate(sepa.path):
            if count%2 == 0: #so a face
                edge.update(face_dict[elt].indices)
            if count%2 == 1: # so an edge
                edge.update(edge_dict[elt].indices)
            