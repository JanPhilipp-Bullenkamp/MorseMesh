from plyfile import PlyData

def read_labels_from_color_ply(filename):
    rawdata = PlyData.read(filename)
    
    labels = {}
    conversion = {}
    
    label = 0
    for ind, pt in enumerate(rawdata['vertex']):
        if tuple((pt['red'], pt['green'], pt['blue'])) not in conversion.keys():
            conversion[ tuple((pt['red'], pt['green'], pt['blue'])) ] = label
            labels[label] = set()
            labels[label].add(ind)
            
            label+=1
        else:
            labels[conversion[ tuple((pt['red'], pt['green'], pt['blue'])) ]].add(ind)
            
    return labels, len(rawdata['vertex'])
         