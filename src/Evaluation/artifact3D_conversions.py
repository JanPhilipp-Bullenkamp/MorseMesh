import scipy.io
import numpy as np
from scipy.spatial import KDTree

def artifact3D_to_labels(filename, scarfilename):
    mat = scipy.io.loadmat(filename)
    scarmat = scipy.io.loadmat(scarfilename)
    
    reorientation_trafo = {}
    reorientation_trafo['Flipvector'] = [scarmat['ds'][0][0][1][0][0],scarmat['ds'][0][0][1][0][0],1]
    reorientation_trafo['Trafomatrix'] = scarmat['ds'][0][0][0]
    data = ([scarmat['ds'][0][0][1][0][0],scarmat['ds'][0][0][1][0][0],1]*mat['vertices'].dot(scarmat['ds'][0][0][0])[:,:])
    reorientation_trafo['Translationvector'] = np.sum(data,axis=0)/len(data)
    data = data - np.sum(data,axis=0)/len(data)
    
    pt_list = [pt for pt in data]
        
    tree = KDTree(pt_list, leafsize=1000)

    label_dict = {}
    lab_pt_dict = {}
    visited = set()
    counter = 0
    for label in range(len(scarmat['sdata'])):
        label_dict[label+1] = set()
        for pt in scarmat['sdata'][label][0][2]:
            dist, closest_ind = tree.query(pt,k=1)
            if closest_ind == 0:
                print("Starts at 0")
            if closest_ind == len(pt_list):
                print("Ends with length")
            if closest_ind not in visited:
                if dist > 0.01:
                    counter+=1
                    #print(dist)
                label_dict[label+1].add(closest_ind)
                lab_pt_dict[closest_ind] = label+1
                visited.add(closest_ind)
    print(label+1," labels")
    print(counter,"/",len(pt_list) ," points far away nearest neighbor")
    
    visited_pts = []
    transf = {}
    for i, pt in enumerate(visited):
        transf[i] = pt 
        visited_pts.append(pt_list[pt])
    #visited_pts = [pt_list[i] for i in visited]
    tree_visited = KDTree(visited_pts, leafsize=1000)
    
    not_visited = set(range(len(pt_list))).difference(visited)
    
    print("Process ",len(not_visited), " unvisited points...")
    for ind in not_visited:
        dist, closest_labelled_ind = tree_visited.query(pt_list[ind], k=1)
        label_dict[lab_pt_dict[transf[closest_labelled_ind]]].add(ind)
    return label_dict, reorientation_trafo

def artifact3D_get_trafo(filename, scarfilename):
    mat = scipy.io.loadmat(filename)
    scarmat = scipy.io.loadmat(scarfilename)
    
    reorientation_trafo = {}
    reorientation_trafo['Flipvector'] = [scarmat['ds'][0][0][1][0][0],scarmat['ds'][0][0][1][0][0],1]
    reorientation_trafo['Trafomatrix'] = scarmat['ds'][0][0][0]
    data = ([scarmat['ds'][0][0][1][0][0],scarmat['ds'][0][0][1][0][0],1]*mat['vertices'].dot(scarmat['ds'][0][0][0])[:,:])
    reorientation_trafo['Translationvector'] = np.sum(data,axis=0)/len(data)
    return reorientation_trafo