"""
    MorseMesh
    Copyright (C) 2023  Jan Philipp Bullenkamp

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from plyfile import PlyData
from collections import Counter

class Parameters:
    def __init__(self, pers, high_thr, low_thr, merge_thr):
        self.pers = pers
        self.high_thr = high_thr
        self.low_thr = low_thr
        self.merge_thr = merge_thr
        
class PlyReadSettings:
    def __init__(self, size_threshold=10, connected_components=True):
        self.size_threshold = size_threshold
        self.connected_components = connected_components
        
""" 
------------------------------------------------------------------------------------------
::::::::::::::LABELS CLASS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
------------------------------------------------------------------------------------------
"""

class Labels:
    def __init__(self, 
                 sorted = False, 
                 enumerated = False, 
                 enumerated_start = 1, 
                 parameters_stored = False,
                 parameters = None):
        # store labels
        self.labels = {}
        
        # store flags
        self.sorted = sorted
        self.enumerated = enumerated
        self.enumerate_start = enumerated_start
        self.parameters_stored = parameters_stored
        
        # parameters
        self.parameters = parameters
        self.plyread = PlyReadSettings()
        
    def enum_labels(self):
        new_dict = {}
        for new_label, old_label in enumerate(self.labels.keys(), start=self.enumerate_start):
            new_dict[new_label] = self.labels.pop(old_label)
        self.labels = new_dict
        
    def sort_labels(self):
        new_dict = {}
        for label_enum, old_label_tuple in enumerate(sorted(self.labels.items(), key=lambda val: len(val[1]), reverse=True), start=self.enumerate_start):
            old_label_key = old_label_tuple[0]
            new_dict[label_enum] = self.labels.pop(old_label_key)
        self.labels = new_dict
        
    def load_from_ply(self, filepath):
        if filepath.split(".")[-1] != "ply":
            raise ValueError("Expected ply file to read labels from")
        self.labels = clean_and_read_labels_from_color_ply(filepath, 
                                                           self.plyread.size_threshold,
                                                           self.plyread.connected_components)
        if self.sorted:
            self.sort_labels()
        elif self.enumerated:
            self.enum_labels()
        
    def load_from_txt(self, filepath):
        if filepath.split(".")[-1] != "txt":
            raise ValueError("Expected txt file to read labels from")
        with open(filepath, "r") as f:
            ind = 0
            for line in f:
                if line[0] == "#":
                    if self.parameters_stored:
                        if ind == 3:
                            pers = float(line.split()[-1])
                        if ind == 4:
                            high_thr = float(line.split()[-1])
                        if ind == 5:
                            low_thr = float(line.split()[-1])
                        if ind == 6:
                            merge_thr = float(line.split()[-1])
                        ind += 1
                    else:
                        continue
                else:
                    ind = int(line.split()[0])
                    label = int(line.split()[1])
                    
                    if label not in self.labels.keys():
                        self.labels[label] = set()
                        self.labels[label].add(ind)
                    else:
                        self.labels[label].add(ind)
            if self.parameters_stored:
                self.parameters = Parameters(pers,high_thr,low_thr,merge_thr)
        if self.sorted:
            self.sort_labels()
        elif self.enumerated:
            self.enum_labels()
            
    def load_from_dict(self, label_dict):
        if type(label_dict) != dict:
            raise ValueError("Expected label dictionary")
        self.labels = label_dict
        if self.sorted:
            self.sort_labels()
        elif self.enumerated:
            self.enum_labels()
            
    def load_from_cells(self, cells):
        for cell in cells.values():
            self.labels[cell.label] = cell.vertices
        if self.sorted:
            self.sort_labels()
        elif self.enumerated:
            self.enum_labels()
            
    def load_parameters(self, pers, high_thr, low_thr, merge_thr):
        self.parameters_stored = True
        self.parameters = Parameters(pers, high_thr, low_thr, merge_thr)
        
    def get_parameters(self):
        return (self.parameters.pers, 
                self.parameters.high_thr, 
                self.parameters.low_thr, 
                self.parameters.merge_thr)
    
    def get_vertex_number(self):
        num = 0
        for indices in self.labels.values():
            num += len(indices)
        return num 
            
    def write_labels_txt(self, filepath):
        # check if filepath is .txt and add if necessary
        if filepath.split(".")[-1] != "txt":
            Warning("Need .txt filepath to write labels! Gonna add .txt")
            filepath += ".txt"
        
        # write file
        with open(filepath, "w") as f:
            # write labels
            if self.parameters_stored:
                write_header(f, params=self.parameters)
            else:
                write_header(f)
            # actually write labels
            for label, indices in self.labels.items():
                for index in indices:
                    f.write(str(index) + " " + str(label) + "\n")
 
                
""" 
------------------------------------------------------------------------------------------
::::::::::::::READ FROM PLY:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
------------------------------------------------------------------------------------------
"""

class Mesh:
    def __init__(self, filename: str):
        self.filename = filename
        
        self.Vertices = {}
        
class Vertex:
    def __init__(self,
                 label: int = None):
        self.label=label
        self.star = set()
        
def neighbor_labels(vert_dict: dict, ind: int) -> list:
    labels = []
    for vert_ind in vert_dict[ind].star:
        if vert_dict[vert_ind].label != vert_dict[ind].label:
            labels.append(vert_dict[vert_ind].label)
    return labels
        
def clean_and_read_labels_from_color_ply(mesh_filename: str, 
                                         threshold: int = 10,
                                         connected_components: bool = False):
    rawdata = PlyData.read(mesh_filename)
    
    data = Mesh(mesh_filename)
    
    labels = {}
    conversion = {}
    
    label_counter = 0
    for ind, pt in enumerate(rawdata['vertex']):
        if tuple((pt['red'], pt['green'], pt['blue'])) not in conversion.keys():
            conversion[ tuple((pt['red'], pt['green'], pt['blue'])) ] = label_counter
            labels[label_counter] = set()
            labels[label_counter].add(ind)
            
            vert = Vertex(label_counter)
            data.Vertices[ind] = vert
            
            label_counter+=1
        else:
            labels[conversion[ tuple((pt['red'], pt['green'], pt['blue'])) ]].add(ind)
            
            vert = Vertex(conversion[tuple((pt['red'], 
                                            pt['green'], 
                                            pt['blue']))])
            data.Vertices[ind] = vert
            
    for face in rawdata['face']:
        indices = set(face[0])
        for elt in indices:
            data.Vertices[elt].star.update(indices)
            
    no_neighbor_list = []
    delkeys = set()
    new_labels = {}
    for label, ptset in labels.items():
        if len(ptset) < threshold:
            no_neighbor_list += ptset
            for pt in ptset:
                data.Vertices[pt].label = None
            delkeys.add(label) 
        elif len(ptset) >= threshold and connected_components: # connected_components is flag
            comp = get_connected_components(label, ptset, data)
            if len(comp.keys()) > 1:
                for key, component in comp.items():
                    if len(component) < threshold:
                        no_neighbor_list += component
                        for pt in component:
                            data.Vertices[pt].label=None
                    else:
                        new_labels[label_counter] = component
                        for pt in component:
                            data.Vertices[pt].label = label_counter
                        label_counter+=1
                delkeys.add(label)

    for key in delkeys:
        labels.pop(key,None)
    labels.update(new_labels)

    it = 0
    while len(no_neighbor_list) != 0:
        pt = no_neighbor_list.pop(0)
        add_point_to_neighborlabel(pt, labels, data, threshold, no_neighbor_list)
        it+=1
        if it%50000==0:
            break                
    return labels

def get_connected_components(label, pts, data):
    comp = {}
    iterated = set()
    l=0
    for pt in pts:
        if pt not in iterated:
            if len(data.Vertices[pt].star.intersection(iterated)) == 0:
                comp[l] = set()
                comp[l].add(pt)
                iterated.add(pt)
                neighbors = set()
                for neig in data.Vertices[pt].star:
                    if data.Vertices[neig].label == label:
                        neighbors.add(neig) 

                while len(neighbors) != 0:
                    point = neighbors.pop()
                    if data.Vertices[point].label == label:
                        comp[l].add(point)
                        iterated.add(point)
                        for nei in data.Vertices[point].star:
                            if data.Vertices[nei].label == label and nei not in iterated:
                                neighbors.add(nei)
                    else:
                        iterated.add(point)
                l+=1
            else:
                for label, pset in comp.items():
                    if len(data.Vertices[pt].star.intersection(pset)) != 0:
                        comp[label].add(pt)
    return comp

def add_point_to_neighborlabel(pt, labels, data, threshold, no_neighbor_list):
    counts = Counter(neighbor_labels(data.Vertices, pt))
    if len(counts) > 0:
        most_common = counts.most_common(1)[0][0]
        if most_common != None and len(labels[most_common]) >= threshold:
            labels[most_common].add(pt)
            data.Vertices[pt].label=most_common
        else:
            data.Vertices[pt].label=None
            no_neighbor_list.append(pt)
    else:
        data.Vertices[pt].label=None
        no_neighbor_list.append(pt)

""" 
------------------------------------------------------------------------------------------
        WRITE .....
------------------------------------------------------------------------------------------
"""

def write_header(file, params = None):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    if params != None:
        file.write("# | Persistence: "+ str(params.pers)+"\n")
        file.write("# | High edge Threshold: "+ str(params.high_thr)+"\n")
        file.write("# | Low edge Threshold: "+ str(params.low_thr)+"\n")
        file.write("# | Merge Threshold: "+ str(params.merge_thr)+"\n")
        file.write("# +-----------------------------------------------------+\n")
            
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")
    