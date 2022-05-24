import timeit

def get_salient_edge_indices(MorseComplex, thresh, vert_dict, edge_dict, face_dict):
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
            