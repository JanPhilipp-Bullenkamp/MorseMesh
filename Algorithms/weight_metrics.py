import numpy as np

# idea: percentage of salient edge pts on a boundary between two cells
def compute_weight_saledge(points, sal_points):
    edge = 0
    noedge = 0
    for ind in points:
        if ind in sal_points:
            edge += 1
        else:
            noedge += 1
    return edge/(edge+noedge)

# idea: average fun_val on a boundary between two cells
def compute_weight_funvals(points, vert_dict):
    fun_vals = []
    for ind in points:
        fun_vals.append(vert_dict[ind].fun_val)
    return sum(fun_vals)/len(fun_vals)

# idea: compare average normals of two cells and normalize such that 0 means parallel and 1 means antiparallel (0.5 means orthogonal)
def compute_weight_normals(set1, set2, vert_dict):
    nx1, ny1, nz1 = [], [], []
    for ind in set1:
        nx1.append(vert_dict[ind].nx)
        ny1.append(vert_dict[ind].ny)
        nz1.append(vert_dict[ind].nz)
    mean_n1 = np.array([sum(nx1)/len(nx1), sum(ny1)/len(ny1), sum(nz1)/len(nz1)])
    
    nx2, ny2, nz2 = [], [], []
    for ind in set2:
        nx2.append(vert_dict[ind].nx)
        ny2.append(vert_dict[ind].ny)
        nz2.append(vert_dict[ind].nz)
    mean_n2 = np.array([sum(nx2)/len(nx2), sum(ny2)/len(ny2), sum(nz2)/len(nz2)])
    
    cos_angle = np.dot(mean_n1, mean_n2)/(np.linalg.norm(mean_n1)*np.linalg.norm(mean_n2))
    
    # transfers [-1,1] to [0,2] to [0,1] to [0,1] (last conversion cause 0 should be good)
    # test with sqrt
    return np.sqrt(1-(cos_angle+1)/2)

# idea: calculate variance of normals on boundary (high variance means many normal direction shifts, low variance menas mostly flat)
def compute_weight_normalvariance(points, vert_dict):
    nx, ny, nz = [], [], []
    for ind in points:
        nx.append(vert_dict[ind].nx)
        ny.append(vert_dict[ind].ny)
        nz.append(vert_dict[ind].nz)
    metric = np.sqrt(np.var(nx)**2 + np.var(ny)**2 + np.var(nz)**2)
    return metric