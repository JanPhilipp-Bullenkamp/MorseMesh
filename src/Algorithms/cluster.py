import random

# Input: Mesh, bd_pts
# Output: dictionary of clusters that do not cross boundaries (connected components)

class Component:
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.vertices = {seed} # set()
        self.open = [seed]
        self.neighbors = {}


def cluster_mesh(vert_dict: dict, bd_pts: set, num_seeds: int = 150) -> dict:
    cluster = {}
    
    unoccupied_vertices = [ind for ind in vert_dict.keys() if ind not in bd_pts]

    seeds = random.sample(unoccupied_vertices, num_seeds)
    for seed in seeds:
        cluster[seed] = Component(seed)

    unoccupied_vertices = set(unoccupied_vertices) - set(seeds)

    len_before = 0

    while len(unoccupied_vertices) != len_before:
        len_before = len(unoccupied_vertices)
        for component in cluster.values():
            open_neighbors = [ind for open_vert in component.open for ind in vert_dict[open_vert].neighbors]
            component.open = []
            for ind in open_neighbors:
                if ind in unoccupied_vertices:
                    if ind in bd_pts:
                        component.vertices.add(ind)
                    else:
                        component.vertices.add(ind)
                        component.open.append(ind)
                    unoccupied_vertices.remove(ind)

    return cluster
            