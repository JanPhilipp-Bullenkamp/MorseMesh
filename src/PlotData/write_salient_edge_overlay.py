import numpy as np
import matplotlib.pyplot as plt
import timeit
from collections import Counter

from .bd_points_compare import write_overlay_bd

'''
first part of this file: write salient edge overlay file and improved overlay
second part of this file: plot salient edge persistence histogram
'''

def write_header(file, nb_points):
    file.write("ply \n")
    file.write("format ascii 1.0 \n")
    file.write("element vertex " + str(nb_points) + "\n")
    file.write("property float x\n")
    file.write("property float y\n")
    file.write("property float z\n")
    file.write("property uchar red\n")
    file.write("property uchar green\n")
    file.write("property uchar blue\n")
    file.write("end_header\n")
    
def write_vertex(file, vert, vert_dict, color=[0,0,0]):
    file.write(str(vert_dict[vert.index].x) + " " + str(vert_dict[vert.index].y) + " " + str(vert_dict[vert.index].z) + " ") 
    file.write(str(color[0]) + " " + str(color[1]) + " " + str(color[2]) + "\n")
        
def write_edge(file, edge, vert_dict, color=[0,0,0]):
    x,y,z = 0,0,0
    for ind in edge.indices:
        x += vert_dict[ind].x
        y += vert_dict[ind].y
        z += vert_dict[ind].z
    x = round(x/len(edge.indices), 8)
    y = round(y/len(edge.indices), 8)
    z = round(z/len(edge.indices), 8)
    file.write(str(x) + " " + str(y) + " " + str(z) + " ") 
    file.write(str(color[0]) + " " + str(color[1]) + " " + str(color[2]) + "\n")
    
def write_face(file, face, vert_dict, color=[0,0,0]):
    x,y,z = 0,0,0
    for ind in face.indices:
        x += vert_dict[ind].x
        y += vert_dict[ind].y
        z += vert_dict[ind].z
    x = round(x/len(face.indices), 8)
    y = round(y/len(face.indices), 8)
    z = round(z/len(face.indices), 8)
    file.write(str(x) + " " + str(y) + " " + str(z) + " ") 
    file.write(str(color[0]) + " " + str(color[1]) + " " + str(color[2]) + "\n")
        

def write_salient_edge_file(MorseCpx, vert_dict, edge_dict, face_dict, 
                            thresh, target_file, color_paths=[0,0,0]):
    start_timer = timeit.default_timer()
    
    f = open(target_file + "_SepThr" + str(thresh) + "_OverlaySalientEdge.ply", "w")
    
    path_vert = set()
    path_edges = set()
    path_faces = set()
    
    for pers, sepa in MorseCpx.Separatrices:
        if pers > thresh:
            if sepa.dimension == 1:
                for i, elt in enumerate(sepa.path):
                    if i%2==0:
                        path_edges.add(elt)
                    elif i%2==1:
                        path_vert.add(elt)

            elif sepa.dimension == 2:
                for i, elt in enumerate(sepa.path):
                    if i%2==0:
                        path_faces.add(elt)
                    elif i%2==1:
                        path_edges.add(elt)
                            
    nb_points = len(path_vert) + len(path_edges) + len(path_faces)
    
    write_header(f, nb_points)
    
    for ind in path_vert:
        write_vertex(f, vert_dict[ind], vert_dict, color=color_paths)
    for ind in path_edges:
        write_edge(f, edge_dict[ind], vert_dict, color=color_paths)
    for ind in path_faces:
        write_face(f, face_dict[ind], vert_dict, color=color_paths)
     
          
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing salient edge overlay file for maximally reduced MC and threshold', thresh, ': ', time_writing_file)
    

def write_dual_thresh_salient_edge_file(MorseCpx, vert_dict, edge_dict, face_dict, 
                                        thresh_high, thresh_low, 
                                        target_file, color_high=[0,0,0], color_low=[255,255,255]):
    start_timer = timeit.default_timer()
    
    f = open(target_file+"_dualthresh"+str(thresh_low)+"-"+str(thresh_high)+"_OverlaySalientEdge.ply", "w")
    
    path_vert_high = set()
    path_edges_high = set()
    path_faces_high = set()
    path_vert_low = set()
    path_edges_low = set()
    path_faces_low = set()
    
    for pers, sepa in MorseCpx.Separatrices:
        if pers > thresh_high:
            if sepa.dimension == 1:
                for i, elt in enumerate(sepa.path):
                    if i%2==0:
                        path_edges_high.add(elt)
                    elif i%2==1:
                        path_vert_high.add(elt)

            elif sepa.dimension == 2:
                for i, elt in enumerate(sepa.path):
                    if i%2==0:
                        path_faces_high.add(elt)
                    elif i%2==1:
                        path_edges_high.add(elt)
        
        # add low edges
        elif pers <= thresh_high and pers > thresh_low:
            if sepa.dimension == 1:
                for i, elt in enumerate(sepa.path):
                    if i%2==0:
                        path_edges_low.add(elt)
                    elif i%2==1:
                        path_vert_low.add(elt)

            elif sepa.dimension == 2:
                for i, elt in enumerate(sepa.path):
                    if i%2==0:
                        path_faces_low.add(elt)
                    elif i%2==1:
                        path_edges_low.add(elt)

                            
    nb_points = len(path_vert_high) + len(path_edges_high) + len(path_faces_high) + len(path_vert_low) + len(path_edges_low) + len(path_faces_low)
    
    write_header(f, nb_points)
    
    for ind in path_vert_high:
        write_vertex(f, vert_dict[ind], vert_dict, color=color_high)
    for ind in path_edges_high:
        write_edge(f, edge_dict[ind], vert_dict, color=color_high)
    for ind in path_faces_high:
        write_face(f, face_dict[ind], vert_dict, color=color_high)
                                                                                                           
    
    for ind in path_vert_low:
        write_vertex(f, vert_dict[ind], vert_dict, color=color_low)
    for ind in path_edges_low:
        write_edge(f, edge_dict[ind], vert_dict, color=color_low)
    for ind in path_faces_low:
        write_face(f, face_dict[ind], vert_dict, color=color_low)
          
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing dual thresh salient edge overlay file for maximally reduced MC and threshold', thresh_low, thresh_high, ': ', time_writing_file)
    
def write_improved_salient_edge_file(MorseCpx, min_thresh, max_thresh, vert_dict, edge_dict, face_dict, 
                                     thresh, target_file, color_paths=[0,0,0]):
    start_timer = timeit.default_timer()
    
    f = open(target_file + "_maxPers_thresh" + str(thresh) + "_ImprovedOverlaySalientEdge.ply", "w")
    
    path_vert = set()
    path_edges = set()
    path_faces = set()
    
    for pers, sepa in MorseCpx.Separatrices:
         if pers > thresh:
                if sepa.dimension == 1:
                    if abs(vert_dict[sepa.path[-1]].fun_val) > min_thresh: 
                        for i, elt in enumerate(sepa.path):
                            if i%2==0:
                                path_edges.add(elt)
                            elif i%2==1:
                                path_vert.add(elt)
                    
                elif sepa.dimension == 2:
                    if abs(face_dict[sepa.path[0]].fun_val[0]) > max_thresh:
                        for i, elt in enumerate(sepa.path):
                            if i%2==0:
                                path_faces.add(elt)
                            elif i%2==1:
                                path_edges.add(elt)
            
    nb_points = len(path_vert) + len(path_edges) + len(path_faces)
    
    write_header(f, nb_points)
    
    for ind in path_vert:
        write_vertex(f, vert_dict[ind], vert_dict, color=color_paths)
    for ind in path_edges:
        write_edge(f, edge_dict[ind], vert_dict, color=color_paths)
    for ind in path_faces:
        write_face(f, face_dict[ind], vert_dict, color=color_paths)
     
          
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing improved salient edge overlay file for maximally reduced MC and threshold', thresh, ': ', time_writing_file)
    
def plot_salient_edge_histogramm(Cplx, nb_bins = 15, log=False, save = False, filepath = None):
    persistences = []
    for pers, sepa in Cplx.Separatrices:
        persistences.append(pers)
        
    plt.hist(persistences, bins=nb_bins, log=log)
    plt.xlabel("Separatrix Persistence")
    plt.ylabel("Counts")
    plt.title("Separatrix Persistence Histogram")
    if save == True:
        plt.savefig(filepath, dpi=600)
    plt.show()
    