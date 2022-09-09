from .weight_metrics import compute_weight_saledge, compute_weight_normals

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
                
    def remove_small_components(self, MorseCell, size_thresh):
        rem_comp = set()
        for key, val in self.conncomps.items():
            if [neighb for neighb, v in sorted(val.items(), key=lambda item: abs(item[1]))]:
                lowest_weight_label = [neighb for neighb, v in sorted(val.items(), key=lambda item: abs(item[1]))][0]
                if len(MorseCell[key]["set"]) < size_thresh:
                    for nei in self.conncomps[key].keys():
                        self.conncomps[nei].pop(key)
                        rem_comp.add(key)
                    MorseCell[lowest_weight_label]["set"].update(MorseCell[key]["set"])
                    MorseCell[lowest_weight_label]["boundary"].update(MorseCell[key]["boundary"])
                    MorseCell.pop(key)
        for comp in rem_comp:
            self.conncomps.pop(comp)
        return MorseCell
    
    def remove_small_enclosures(self, MorseCell, relative_size_thresh=0.5):
        rem_comp = set()
        for enclosed in self.conncomps.keys():
            if len(self.conncomps[enclosed].keys()) == 1:
                surrounding = next(iter(self.conncomps[enclosed]))
                
                if len(MorseCell[enclosed]["set"])/len(MorseCell[surrounding]["set"]) < relative_size_thresh:
                    self.conncomps[surrounding].pop(enclosed)
                    rem_comp.add(enclosed)
                    MorseCell[surrounding]["set"].update(MorseCell[enclosed]["set"])
                    MorseCell.pop(enclosed)
        for comp in rem_comp:
            self.conncomps.pop(comp)
        return MorseCell
        
    
    def remove_weak_edges(self, MorseCell, absolute_threshold):
        rem_comp = set()
        for key, val in self.conncomps.items():
            if len(val.keys()) != 0:
                neighb, weight = [tuple((neighb, weight)) for neighb, weight in sorted(val.items(), key=lambda item: abs(item[1]))][0]
                if abs(weight) < absolute_threshold:
                    for nei in self.conncomps[key].keys():
                        self.conncomps[nei].pop(key)
                        rem_comp.add(key)
                    MorseCell[neighb]["set"].update(MorseCell[key]["set"])
                    MorseCell[neighb]["boundary"].update(MorseCell[key]["boundary"])
                    MorseCell.pop(key)
        for comp in rem_comp:
            self.conncomps.pop(comp)
        return MorseCell
    
    def merge_and_update(self, label1, label2, MorseCell, saledge_points, vert_dict):
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
                weight_saledge = compute_weight_saledge(MorseCell[label1]["neighbors"][neighb], saledge_points)
                ''' Normals weight commented out, needs further work'''
                #weight_normals = compute_weight_normals(MorseCell[label1]["set"], MorseCell[neighb]["set"], vert_dict)
                #self.conncomps[label1][neighb] = (weight_saledge+weight_normals)/2
                #self.conncomps[neighb][label1] = (weight_saledge+weight_normals)/2
                self.conncomps[label1][neighb] = weight_saledge
                self.conncomps[neighb][label1] = weight_saledge
                
                '''TODO
                compute weights new every time due to changed mean normal
                   TODO'''
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
            
    
    def simplify_cells(self, MorseCell, thresh, saledge_points, vert_dict):
        
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
                MorseCell = self.merge_and_update(lb1, lb2, MorseCell, saledge_points, vert_dict)
                visited.add(lb1)
                visited.add(lb2)
            
        return MorseCell
            
                
        
        