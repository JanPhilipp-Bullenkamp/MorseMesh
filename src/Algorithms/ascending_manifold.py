

def ascending_manifold(vert_dict: dict,
                       edge_dict: dict,
                       V12: dict,
                       C: dict
                       ):
    # label crit vertices first
    for label, vert_ind in enumerate(C[0]):
        vert_dict[vert_ind].ascend_label = label
    
    for v_ind, e_ind in V12.items():
        if vert_dict[v_ind].ascend_label == None:
            other_v = (edge_dict[e_ind].indices - {v_ind}).pop()

            q = []
            q.append(other_v)

            for ind in q:
                do=sth

