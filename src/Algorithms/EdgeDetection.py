import timeit

def dual_thresh_edge_detection(max_red_MSComplex, thresh_high, thresh_low, vert_dict, edge_dict, face_dict):
    strong_edge, weak_edge = get_salient_edge_indices_dual_thr(max_red_MSComplex, 
                                                               thresh_high, thresh_low, 
                                                               vert_dict, edge_dict, face_dict)

    queue = []
    for ind in strong_edge:
        for nei in vert_dict[ind].neighbors:
            if nei in weak_edge and nei != ind:
                queue.append(nei)
                weak_edge.remove(nei)

    for elt in queue:
        strong_edge.add(elt)

    while len(queue) != 0:
        ind = queue.pop(0)
        for nei in vert_dict[ind].neighbors:
            if nei in weak_edge and nei != ind:
                queue.append(nei)
                strong_edge.add(nei)
                weak_edge.remove(nei)
    return strong_edge
    
def get_salient_edge_indices(MorseComplex, thresh, 
                             vert_dict, edge_dict, face_dict):
    start_timer = timeit.default_timer()
    
    sal_edge = set()
    for pers, sepa in MorseComplex.Separatrices:
         if pers > thresh:
                if sepa.dimension == 1:
                    for count, elt in enumerate(sepa.path):
                        if count%2 == 1: # so a vertex
                            sal_edge.add(elt)
                        if count%2 == 0: # so an edge
                            sal_edge.update(edge_dict[elt].indices)
                            
                elif sepa.dimension == 2:
                    for count, elt in enumerate(sepa.path):
                        if count%2 == 0: #so a face
                            sal_edge.update(face_dict[elt].indices)
                        if count%2 == 1: # so an edge
                            sal_edge.update(edge_dict[elt].indices)
                            
    time = timeit.default_timer() - start_timer
    print('Time getting salient edge points for ',thresh, 'threshold:', time)                        
    return sal_edge

def get_salient_edge_indices_dual_thr(MorseComplex, 
                                      thresh_high, thresh_low, 
                                      vert_dict, edge_dict, face_dict):
    start_timer = timeit.default_timer()
    
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
                            
    time = timeit.default_timer() - start_timer
    print('Time getting double threshold salient edge points for ',thresh_high,"-",thresh_low, 'threshold:', time)                        
    return strong_edge, weak_edge
            