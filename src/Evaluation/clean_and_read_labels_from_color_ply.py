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

def write_header(file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")

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
                                         label_filename: str = None, 
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
    
    """
    for label, pts in labels.items():
        comp = get_connected_components(label, pts, data)
        if len(comp.keys()) > 1:
                print("Label", label, " has more than one CC")
                lengths = [len(pts) for pts in comp.values()]
                print("Has", len(comp.keys()), " different components with lengths")
                print(lengths)
    """
              
    if label_filename != None:    
        with open(label_filename +".txt", "w") as f:
            write_header(f)

            for count, indices in enumerate(sorted(labels.values(), 
                                                   key=lambda kv: len(kv), 
                                                   reverse=True)):
                label = count+1 # start with label 1
                for index in indices:
                    f.write(str(index) + " " + str(label) + "\n")
                
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