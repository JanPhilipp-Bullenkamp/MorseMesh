from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty
import timeit

def read_labels_from_color_ply(filename):
    start_total_time = timeit.default_timer()
    
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
            
                
    end_total_time = timeit.default_timer() - start_total_time
    print('Time read labels in ply file data:', end_total_time)
    
    return labels, len(rawdata['vertex'])
         