import numpy as np

def compute_IoU(labels1, labels2):
    IoU12 = {}
    for label, points in labels1.items():
        if len(points) > 5:
            IoU12[label] = {}
            for compare_label, compare_points in labels2.items():
                if len(compare_points) > 5:
                    intersect = len(points.intersection(compare_points))
                    union = len(points.union(compare_points))
                    IoU12[label][compare_label] = intersect/union
                    
    return IoU12

# also called dice coefficient
def compute_F1_Score(labels1, labels2):
    F1 = {}
    for label, points in labels1.items():
        if len(points) > 5:
            F1[label] = {}
            for compare_label, compare_points in labels2.items():
                if len(compare_points) > 5:
                    intersect_twice = 2*len(points.intersection(compare_points))
                    total_nb = len(points) + len(compare_points)
                    F1[label][compare_label] = intersect_twice/total_nb
                    
    return F1

def get_correct_points(labels1, labels2, IoU):
    # correct means lb1 is max IoU of lb2 and lb2 is max IoU of lb1
    correct_points = set()
    
    lb1s = [lb1 for lb1 in IoU.keys()]
    # get random label from dict for getting lb2s
    lb = next(iter(IoU))
    lb2s = [lb2 for lb2 in IoU[lb].keys()]
    
    data = []
    for lb1 in IoU.keys():
        data.append([val for val in IoU[lb1].values()])
        
    lb2max = np.argmax(data, axis=0)
    lb1max = np.argmax(data, axis=1)
    
    for id2, id1 in enumerate(lb2max):
        for id1p, id2p in enumerate(lb1max):
            if lb1s[id1] == lb1s[id1p] and lb2s[id2] == lb2s[id2p]:
                #print("Correct:",lb1s[id1],lb2s[id2])
                correct_points.update( labels1[lb1s[id1]].intersection(labels2[lb2s[id2]]) )
    
    return correct_points