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