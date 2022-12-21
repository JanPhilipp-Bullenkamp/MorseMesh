from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty
import timeit
from collections import Counter

def read_label_txt(filename):
    start_total_time = timeit.default_timer()
    
    critLabel = 0 #zero is not used as a label by the clean_gt function
    labels = {}
    
    with open(filename, "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            else:
                s = line.split()
                if len(s) == 1:
                    critLabel = int(line.split()[0])
                else:
                    ind = int(line.split()[0])
                    label = int(line.split()[1])
                    labels[ind] = label
                
    end_total_time = timeit.default_timer() - start_total_time
    print('Time read labels in txt file:', end_total_time)
    
    return labels, critLabel