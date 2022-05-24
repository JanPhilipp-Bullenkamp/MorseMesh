def compute_weight_saledge(points, sal_points):
    edge = 0
    noedge = 0
    for ind in points:
        if ind in sal_points:
            edge += 1
        else:
            noedge += 1
    return edge/(edge+noedge)

class ConnComp():
    def __init__(self, label):
        self.label = label
        self.neighbors = []
        
    def add_neighbor(self, neighbor):
        if neighbor.label not in self.neighbors:
            self.neighbors.append(neighbor.label)
            neighbor.neighbors.append(self.label)

class Graph():
    def __init__(self):
        self.conncomps = {}
        
    def add_ConnComp(self, conncomp):
        self.conncomps[conncomp.label] = {}
        for neighb in conncomp.neighbors:
            self.conncomps[conncomp.label][neighb] = 0

    def add_Edge(self, label1, label2):
        if label1 in self.conncomps.keys() and label2 in self.conncomps.keys():
            if label2 not in self.conncomps[label1].keys():
                self.conncomps[label1][label2] = 0
            if label1 not in self.conncomps[label2].keys():
                self.conncomps[label2][label1] = 0
                
    def add_weightedEdge(self, label1, label2, weight):
        if label1 in self.conncomps.keys() and label2 in self.conncomps.keys():
            if label2 not in self.conncomps[label1].keys():
                self.conncomps[label1][label2] = weight
            if label1 not in self.conncomps[label2].keys():
                self.conncomps[label2][label1] = weight
                
    def remove_small_components(self, Mesh, persistence, size_thresh):
        rem_comp = set()
        for key, val in self.conncomps.items():
            lowest_weight_label = [neighb for neighb, v in sorted(val.items(), key=lambda item: abs(item[1]))][0]
            if len(Mesh.MorseCells[persistence][key]["set"]) < size_thresh:
                for nei in self.conncomps[key].keys():
                    self.conncomps[nei].pop(key)
                    rem_comp.add(key)
                Mesh.MorseCells[persistence][lowest_weight_label]["set"].update(Mesh.MorseCells[persistence][key]["set"])
                Mesh.MorseCells[persistence][lowest_weight_label]["boundary"].update(Mesh.MorseCells[persistence][key]["boundary"])
                Mesh.MorseCells[persistence].pop(key)
        for comp in rem_comp:
            self.conncomps.pop(comp)
        return Mesh
    
    def remove_weak_edges(self, Mesh, persistence, absolute_threshold):
        rem_comp = set()
        for key, val in self.conncomps.items():
            if len(val.keys()) != 0:
                neighb, weight = [tuple((neighb, weight)) for neighb, weight in sorted(val.items(), key=lambda item: abs(item[1]))][0]
                if abs(weight) < absolute_threshold:
                    for nei in self.conncomps[key].keys():
                        self.conncomps[nei].pop(key)
                        rem_comp.add(key)
                    Mesh.MorseCells[persistence][neighb]["set"].update(Mesh.MorseCells[persistence][key]["set"])
                    Mesh.MorseCells[persistence][neighb]["boundary"].update(Mesh.MorseCells[persistence][key]["boundary"])
                    Mesh.MorseCells[persistence].pop(key)
        for comp in rem_comp:
            self.conncomps.pop(comp)
        return Mesh
    
    def merge_and_update(self, label1, label2, MorseCell, saledge_points):
        # want to remove label2, 
        # update weights of the new combined label1
        # update the MorseCell dict accordingly
        #print("Merge", label1, "and", label2, "with weight", self.conncomps[label1][label2], "should be equal to",self.conncomps[label2][label1])
        MorseCell[label1]["set"].update(MorseCell[label2]["set"])
        MorseCell[label1]["boundary"].update(MorseCell[label2]["boundary"])
        MorseCell[label1]["neighbors"].pop(label2)
        MorseCell[label2]["neighbors"].pop(label1)
        # go over old neighbors of label2 and either combine with label1 or add new neighbor
        for neighb, elts in MorseCell[label2]["neighbors"].items():
            if neighb in MorseCell[label1]["neighbors"].keys():
                MorseCell[label1]["neighbors"][neighb].update(elts)
                MorseCell[neighb]["neighbors"][label1].update(elts)
                # need to recompute weights
                self.conncomps[label1][neighb] = compute_weight_saledge(MorseCell[label1]["neighbors"][neighb], saledge_points) 
                self.conncomps[neighb][label1] = compute_weight_saledge(MorseCell[label1]["neighbors"][neighb], saledge_points) 
            else:
                MorseCell[label1]["neighbors"][neighb] = elts
                MorseCell[neighb]["neighbors"][label1] = elts
                self.conncomps[label1][neighb] = self.conncomps[label2][neighb] #copy weight from label2
                self.conncomps[neighb][label1] = self.conncomps[label2][neighb] #copy weight from label2
                
            # delete label 2 from all neighbors
            MorseCell[neighb]["neighbors"].pop(label2)
            self.conncomps[neighb].pop(label2)
            
        # now remove label2 objects
        MorseCell.pop(label2)
        self.conncomps[label1].pop(label2)
        self.conncomps.pop(label2)
        return MorseCell
            
    
    def simplify_cells(self, MorseCell, thresh, saledge_points):
        
        merge_list = []
        for label in self.conncomps.keys():
            # weight is % of edge points (btw 0 and 1)
            if sorted(self.conncomps[label].items(), key=lambda item: item[1]):
                lowest_nei, lowest_weight = [tuple((neighb, weight)) for neighb, weight in sorted(self.conncomps[label].items(), key=lambda item: item[1])][0]

                if lowest_weight < thresh:
                    merge_list.append(tuple((label, lowest_nei)) )
                
        visited = set()
        for lb1, lb2 in merge_list:
            if lb1 not in visited and lb2 not in visited:
                MorseCell = self.merge_and_update(lb1, lb2, MorseCell, saledge_points)
                visited.add(lb1)
                visited.add(lb2)
            
        return MorseCell
            
                
        
        