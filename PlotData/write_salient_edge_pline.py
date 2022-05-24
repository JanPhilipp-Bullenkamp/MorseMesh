import numpy as np
import matplotlib.pyplot as plt
import timeit
from collections import Counter

'''
first part of this file: write salient edge overlay file and improved overlay
second part of this file: plot salient edge persistence histogram
'''
def write_header(file):
    file.write("# +-------------------------------------------------------------------------------+\n")
    file.write("# | PLINE file with polylines                                                     |\n")
    file.write("# +-------------------------------------------------------------------------------+\n")
    file.write("# +------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# | Format: Label No. | Number of Vertices | id1 x1 y1 z1 nx1 ny1 nz1 id2 x2 y2 z2 nx2 ny2 nz2 ... idN xN yN zN nxN nyN nzN\n")
    file.write("# +------------------------------------------------------------------------------------------------------------------------\n")
        
def write_midpoint(file, elt, vert_dict):
    x,y,z = 0,0,0
    for ind in elt.indices:
        x += vert_dict[ind].x
        y += vert_dict[ind].y
        z += vert_dict[ind].z
    x = round(x/len(elt.indices), 8)
    y = round(y/len(elt.indices), 8)
    z = round(z/len(elt.indices), 8)
    file.write(" " + str(-1) + " " + str(x) + " " + str(y) + " " + str(z) + " " + str(1.0) + " " + str(0) + " " + str(0))
    
def write_vertex(file, vert):
    file.write(" " + str(-1) + " " + str(vert.x) + " " + str(vert.y) + " " + str(vert.z) + " " + str(1.0) + " " + str(0) + " " + str(0))

def write_polyline(file, line, line_dim, line_ind, vert_dict, edge_dict, face_dict):
    
    indices = []
    if line_dim == 0:  # so saddle to minimum
        for count, elt in enumerate(line):
            if count%2 == 1: # so vertex (edge-vert-edge-vert-... line)
                indices.append(elt)
    
    if line_dim==1:  # so max to saddle
        for count, elt in enumerate(line):
            if count%2 == 0:  #so maximum (max-sad-max-sad-...)
                indices.append(face_dict[elt])
        
    if len(indices) > 3:
        file.write(str(line_ind) + " " + str(len(indices)))
        for ind in indices:
            if line_dim==0:
                write_vertex(file, vert_dict[elt])

            elif line_dim==1:
                write_midpoint(file, ind, vert_dict) # here ind is a face object
        file.write("\n")

def write_salient_edge_pline(MorseCpx, vert_dict, edge_dict, face_dict, thresh, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + "_maxPers_thresh" + str(thresh) + "_SalientEdge.pline", "w")
    
    write_header(f)
    
    line_ind = 0
    for pers, sepa in MorseCpx.Separatrices:
         if pers > thresh:
                if sepa.dimension == 1:
                    write_polyline(f, sepa.path, 0, line_ind, vert_dict, edge_dict, face_dict)
                    
                elif sepa.dimension == 2:
                    write_polyline(f, sepa.path, 1, line_ind, vert_dict, edge_dict, face_dict)
          
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing salient edge pline file for maximally reduced MC and threshold', thresh, ': ', time_writing_file)
    
    
def write_improved_salient_edge_pline(MorseCpx, min_thresh, max_thresh, vert_dict, edge_dict, face_dict, thresh, target_file, color_paths=[0,0,0]):
    start_timer = timeit.default_timer()
    
    f = open(target_file + "_improved_overlay.ply", "w")
    
    path_vert = set()
    path_edges = set()
    path_faces = set()
    
    MorseCpx.Separatrices.sort(key=lambda x: x[0])
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
    print('Time writing overlay file for MorseComplex with ', MorseCpx.persistence,': ', time_writing_file)