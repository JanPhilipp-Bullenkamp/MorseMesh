

# Input: Mesh, bd_pts
# Output: dictionary of clusters that do not cross boundaries (connected components)


def cluster_mesh(vert_dict, bd_pts):
    cluster = {}
    
    clustered = set()
    for ind, vert in vert_dict.items():
        if ind not in bd_pts and ind not in clustered:
            