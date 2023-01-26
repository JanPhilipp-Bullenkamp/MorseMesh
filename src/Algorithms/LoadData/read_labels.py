from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty
import timeit
from collections import Counter

def read_label_txt(filename):
    start_total_time = timeit.default_timer()

    labels = {}
    
    with open(filename, "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            else:
                s = line.split()
                ind = int(s[0])
                label = int(s[1])
                labels[ind] = label
                
    end_total_time = timeit.default_timer() - start_total_time
    print('Time read labels in txt file:', end_total_time)

    c = Counter(labels.values())
    critLabels = c.most_common()[:0:-1]
    
    return labels, set(a for (a, b) in critLabels)