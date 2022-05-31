def compute_weight_saledge(points, sal_points):
    edge = 0
    noedge = 0
    for ind in points:
        if ind in sal_points:
            edge += 1
        else:
            noedge += 1
    return edge/(edge+noedge)

def compute_weight(points, vert_dict):
    fun_vals = []
    for ind in points:
        fun_vals.append(vert_dict[ind].fun_val)
    return sum(fun_vals)/len(fun_vals)
