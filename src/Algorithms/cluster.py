import random

# Input: Mesh, bd_pts
# Output: dictionary of clusters that do not cross boundaries (connected components)

class Component:
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.vertices = {seed} # set()
        self.open = [seed]
        self.boundary = set()
        self.neighbors = {}

    def get_open_neighbors(self, vert_dict: dict) -> list:
        open_neighbors = []
        for open_vert in self.open:
            for ind in vert_dict[open_vert].neighbors:
                if ind not in self.vertices:
                    open_neighbors.append(ind)
        return open_neighbors


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
            open_neighbors = component.get_open_neighbors(vert_dict)
            component.open = []
            for ind in open_neighbors:
                if ind in unoccupied_vertices:
                    if ind in bd_pts:
                        component.vertices.add(ind)
                    else:
                        component.vertices.add(ind)
                        component.open.append(ind)
                    unoccupied_vertices.remove(ind)

        # can be the case, if there are enclosures of the boundary where no seed spawned inside
        if len(unoccupied_vertices) == len_before and len(unoccupied_vertices - bd_pts) != 0:
            new_seed = (unoccupied_vertices - bd_pts).pop()
            cluster[new_seed] = Component(new_seed)
            unoccupied_vertices.remove(new_seed)

    if len(unoccupied_vertices - bd_pts) != 0:
        raise AssertionError("Only boundary points should be left in the unclustered points!")

    # treat boundary points if necessary (should be only bd points with only bd_points as neighbors)
    while len(unoccupied_vertices) != 0:
        remaining_pt = unoccupied_vertices.pop()
        for comp in cluster.values():
            if vert_dict[remaining_pt].neighbors.intersection(comp.vertices):
                comp.vertices.add(remaining_pt)
                break

    # fill boundary points
    get_boundary_points(cluster, vert_dict)

    # fill neighborhoods
    fill_neighborhood(cluster, vert_dict)
    
    return cluster 

def get_boundary_points(cluster: dict, vert_dict: dict):
    for comp in cluster.values():
        for ind in comp.vertices:
            if len(vert_dict[ind].neighbors - comp.vertices) != 0:
                comp.boundary.add(ind)

def fill_neighborhood(cluster: dict, vert_dict: dict):
    for seed, comp in cluster.items():
        for bd in comp.boundary:
            other_side_bd = vert_dict[bd].neighbors - comp.vertices
            for nei_seed, nei_comp in cluster.items():
                if len(nei_comp.boundary.intersection(other_side_bd)) != 0:
                    if nei_seed not in comp.neighbors.keys():
                        comp.neighbors[nei_seed] = set()
                    if seed not in nei_comp.neighbors.keys():
                        nei_comp.neighbors[seed] = set()

                    comp.neighbors[nei_seed].update(nei_comp.boundary.intersection(other_side_bd))
                    nei_comp.neighbors[seed].update(nei_comp.boundary.intersection(other_side_bd))