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