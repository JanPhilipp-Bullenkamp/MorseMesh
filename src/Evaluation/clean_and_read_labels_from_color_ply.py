from plyfile import PlyData
from collections import Counter

def write_header(file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")

class Mesh:
    def __init__(self, filename):
        self.filename = filename
        
        self.Vertices = {}
        
class Vertex:
    def __init__(self, x=None, y=None, z=None,
                label=None):
        self.x = x
        self.y = y
        self.z = z
        self.label=label
        self.star = set()
        
def neighbor_labels(vert_dict, ind):
    labels = []
    for vert_ind in vert_dict[ind].star:
        if vert_dict[vert_ind].label != vert_dict[ind].label:
            labels.append(vert_dict[vert_ind].label)
    return labels
        
def clean_and_read_labels_from_color_ply(mesh_filename, label_filename=None, threshold=10):
    rawdata = PlyData.read(mesh_filename)
    
    data = Mesh(mesh_filename)
    
    labels = {}
    conversion = {}
    
    label = 0
    for ind, pt in enumerate(rawdata['vertex']):
        if tuple((pt['red'], pt['green'], pt['blue'])) not in conversion.keys():
            conversion[ tuple((pt['red'], pt['green'], pt['blue'])) ] = label
            labels[label] = set()
            labels[label].add(ind)
            
            vert = Vertex(pt['x'], pt['y'], pt['z'], label)
            data.Vertices[ind] = vert
            
            label+=1
        else:
            labels[conversion[ tuple((pt['red'], pt['green'], pt['blue'])) ]].add(ind)
            
            vert = Vertex(pt['x'], pt['y'], pt['z'], conversion[ tuple((pt['red'], pt['green'], pt['blue'])) ])
            data.Vertices[ind] = vert
            
    for face in rawdata['face']:
        indices = set(face[0])
        for elt in indices:
            data.Vertices[elt].star.update(indices)
            
    new_it = []
    delkeys = set()
    for label, ptset in labels.items():
        if len(ptset) < threshold:
            for pt in ptset:
                counts = Counter(neighbor_labels(data.Vertices, pt))
                if len(counts) > 0:
                    most_common = counts.most_common(1)[0][0]
                    if most_common != None and len(labels[most_common]) >= threshold:
                        labels[most_common].add(pt)
                        data.Vertices[pt].label=most_common
                    else:
                        data.Vertices[pt].label=None
                        new_it.append(pt)
                else:
                    data.Vertices[pt].label=None
                    new_it.append(pt)
            
            delkeys.add(label) 
    for key in delkeys:
        del labels[key]
                    
    it = 0
    while len(new_it) != 0:
        pt = new_it.pop(0)
        counts = Counter(neighbor_labels(data.Vertices, pt))
        if len(counts) > 0:
            most_common = counts.most_common(1)[0][0]
            if len(labels[most_common]) >= threshold and most_common != None:
                labels[most_common].add(pt)
                data.Vertices[pt].label=most_common
            else:
                new_it.append(pt)
        else:
            new_it.append(pt)
        it+=1
        if it%50000==0:
            break
              
    if label_filename != None:    
        with open(label_filename +".txt", "w") as f:
            write_header(f)

            for count, indices in enumerate(sorted(labels.values(), key=lambda kv: len(kv), reverse=True)):
                label = count+1 # start with label 1
                for index in indices:
                    f.write(str(index) + " " + str(label) + "\n")
                
    return labels