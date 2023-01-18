import random
from .CancellationQueue import CancellationQueue

# Input: Mesh, bd_pts
# Output: dictionary of clusters that do not cross boundaries (connected components)

class Component:
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.vertices = {seed} # set()
        self.open = [seed]
        self.boundary = set()
        self.neighbors = {}
        self.neighbors_weights = {}

    def get_open_neighbors(self, vert_dict: dict) -> list:
        open_neighbors = []
        for open_vert in self.open:
            for ind in vert_dict[open_vert].neighbors:
                if ind not in self.vertices:
                    open_neighbors.append(ind)
        return open_neighbors

def merge_cluster(cluster: dict, bd_points: set, threshold: float):
    # 1. calculate weights between cells
    compute_all_weights(cluster, bd_points)
    still_changing = True
    minimum_labels = 3
    # pop from queue until no more elements are below the merge threshold or we reach the minimum number of labels
    while len(cluster) > minimum_labels and still_changing: #and queue.length() != 0:
        # 2. create and fill Cancellation Queue
        queue = CancellationQueue()
        before = len(cluster)
        for label, comp in cluster.items():
            for neighbor, weight in comp.neighbors_weights.items():
                if weight < threshold:
                    queue.insert(tuple((weight,label, neighbor)))

        while queue.length() != 0:
            weight, label1, label2 = queue.pop_front()
            
            # need to make sure the popped tuple is still available for merging and their weight is also the same.
            if label1 in cluster.keys() and label2 in cluster.keys():
                if label2 in cluster[label1].neighbors.keys():
                    if weight == cluster[label1].neighbors_weights[label2]:
                        # can merge cells
                        updated_weights = merge_cells(cluster, bd_points, label1, label2)
        after = len(cluster)
        if before == after:
            still_changing = False

    cluster = sort_enumerate_dict(cluster)
    return cluster

def sort_enumerate_dict(cluster: dict) -> dict:
    sorted_enum = {}
    for count, comp in enumerate(sorted(cluster.values(), key=lambda kv: len(kv.vertices), reverse=True)):
        sorted_enum[count] = comp
    return sorted_enum

def compute_weight_between_two_cells(components: dict, bd_points: set, label1: int, label2: int):
    points1 = components[label1].neighbors[label2]
    points2 = components[label2].neighbors[label1]
    
    weight = compute_weight(points1.union(points2), bd_points)
    
    components[label1].neighbors_weights[label2] = weight
    components[label2].neighbors_weights[label1] = weight
    return weight
            
def merge_cells(components: dict, bd_points: set, label1: int, label2: int, pop_label2: bool = True) -> list:
    updated_weights = []
    
    # do 1. and 2.:
    components[label1].vertices.update(components[label2].vertices)
    components[label1].boundary.update(components[label2].boundary)
    # remove boundary between the two
    components[label1].boundary = components[label1].boundary - (components[label1].neighbors[label2].union(components[label2].neighbors[label1]))
    
    # iterate over neighbors of label2:
    for neighbor, indices in components[label2].neighbors.items():
        if neighbor == label1:
            continue
        # common neighbor -> adjust boundaries and recomupte weights
        elif neighbor in components[label1].neighbors.keys():
            # extend boundaries on both sides
            components[label1].neighbors[neighbor].update(indices)
            components[neighbor].neighbors[label1].update(components[neighbor].neighbors[label2])
            
            # remove label 2 from neighbor
            components[neighbor].neighbors.pop(label2)
            components[neighbor].neighbors_weights.pop(label2)
            
            # recompute weight:
            new_weight = compute_weight_between_two_cells(components, bd_points, label1, neighbor)
            
            # fill updated_weights list for cancellation queue later
            updated_weights.append(tuple((new_weight, label1, neighbor)))
            
        elif neighbor not in components[label1].neighbors.keys():
            # add new neighbor to label 1 and copy weight from label 2
            components[label1].neighbors[neighbor] = indices
            components[label1].neighbors_weights[neighbor] = components[label2].neighbors_weights[neighbor]
            
            # add label 1 as new neighbor to neighbor and copy weight
            components[neighbor].neighbors[label1] = components[neighbor].neighbors[label2]
            components[neighbor].neighbors_weights[label1] = components[neighbor].neighbors_weights[label2]
            
            # remove label 2 from neighbor:
            components[neighbor].neighbors.pop(label2)
            components[neighbor].neighbors_weights.pop(label2)
            
        else:
            raise AssertionError("Shouldnt happen. One of the above cases always should be fulfilled.")
    
    # remove label 2 from label 1:
    components[label1].neighbors.pop(label2)
    components[label1].neighbors_weights.pop(label2)
    
    # remove label 2 cell completely (optional due to dictionary size change) need to remove after looping sometimes
    if pop_label2:
        components.pop(label2)
    
    return updated_weights
    
def compute_all_weights(cluster: dict, bd_pts: set):
    for seed, comp in cluster.items():
        for nei_seed, nei_points in comp.neighbors.items():
            points_from_nei = cluster[nei_seed].neighbors[seed]
            weight = compute_weight(points_from_nei.union(nei_points), bd_pts)
            comp.neighbors_weights[nei_seed] = weight
            cluster[nei_seed].neighbors_weights[seed] = weight
            
def compute_weight(cluster_boundary: set, edge_pts: set):
    return len(cluster_boundary.intersection(edge_pts))/len(cluster_boundary.union(edge_pts))

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
                        comp.neighbors_weights[nei_seed] = 0
                    if seed not in nei_comp.neighbors.keys():
                        nei_comp.neighbors[seed] = set()
                        nei_comp.neighbors_weights[seed] = 0

                    comp.neighbors[nei_seed].update(nei_comp.boundary.intersection(other_side_bd))
                    nei_comp.neighbors[seed].update(nei_comp.boundary.intersection(other_side_bd))