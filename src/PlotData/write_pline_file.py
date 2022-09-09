import numpy as np
import timeit
from collections import Counter

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
            elif count%2 == 1:  #so saddle
                indices.append(edge_dict[elt])
        
    if len(indices) > 3:
        file.write(str(line_ind) + " " + str(len(indices)))
        for ind in indices:
            if line_dim==0:
                write_vertex(file, vert_dict[elt])

            elif line_dim==1:
                write_midpoint(file, ind, vert_dict) # here ind is an edge or face object
        file.write("\n")
    
def write_polyline_thresholded(file, line, line_dim, line_ind, thresh, vert_dict, edge_dict, face_dict):
    
    indices = []
    if line_dim == 0:  # so saddle to minimum
        for count, elt in enumerate(line):
            if count%2 == 1: # so vertex (edge-vert-edge-vert-... line)
                if vert_dict[elt].fun_val > thresh:
                    indices.append(elt)
                else:
                    break
    
    if line_dim==1:  # so max to saddle
        for count, elt in enumerate(line):
            if count%2 == 0:  #so maximum (max-sad-max-sad-...)
                if face_dict[elt].fun_val[0] > thresh:
                    indices.append(face_dict[elt])
                else:
                    break
            elif count%2 == 1:  #so saddle
                if edge_dict[elt].fun_val[0] > thresh:
                    indices.append(edge_dict[elt])
                else:
                    break
    if len(indices) > 3:                
        file.write(str(line_ind) + " " + str(len(indices)))
        for ind in indices:
            if line_dim==0:
                write_vertex(file, vert_dict[elt])

            elif line_dim==1:
                write_midpoint(file, ind, vert_dict) # here ind is an edge or face object
        file.write("\n")
    

def write_pline_file(MorseComplex, vert_dict, edge_dict, face_dict, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + "_pers" + str(MorseComplex.persistence) + "_MorseComplex.pline", "w")
      
    write_header(f)
    
    # write polylines
    line_ind=0
    # write max to saddle first
    for critface in MorseComplex.CritFaces.values():
        counts = Counter(critface.connected_saddles)
        for sad, nb in counts.items():
            if nb == 1:
                line = critface.paths[sad]
                write_polyline(f, line, 1, line_ind, vert_dict, edge_dict, face_dict)
                line_ind+=1
            elif nb == 2:
                for i in range(2):
                    line = critface.paths[sad][i]
                    write_polyline(f, line, 1, line_ind, vert_dict, edge_dict, face_dict)
                    line_ind+=1
                
    # now write sad to min
    for critedge in MorseComplex.CritEdges.values():
        counts = Counter(critedge.connected_minima)
        for minimum, nb in counts.items():
            if nb == 1:
                line = critedge.paths[minimum]
                write_polyline(f, line, 0, line_ind, vert_dict, edge_dict, face_dict)
                line_ind+=1
            elif nb == 2:
                for i in range(2):
                    line = critedge.paths[minimum][i]
                    write_polyline(f, line, 0, line_ind, vert_dict, edge_dict, face_dict)
                    line_ind+=1
                
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing MorseComplex pline file for persistence ', MorseComplex.persistence, ':', time_writing_file)
    
def write_pline_file_thresholded(MorseComplex, minimum_length, thresh, vert_dict, edge_dict, face_dict, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + "_pers" + str(MorseComplex.persistence) + "_thresh" + str(thresh) + "_ThreshMorseComplex.pline", "w")
    
    write_header(f)
    
    # write polylines
    line_ind=0
    # write max to saddle first
    for critface in MorseComplex.CritFaces.values():
        counts = Counter(critface.connected_saddles)
        for sad, nb in counts.items():
            if nb == 1:
                line = critface.paths[sad]
                if len(line) > minimum_length:
                    write_polyline_thresholded(f, line, 1, line_ind, thresh, vert_dict, edge_dict, face_dict)
                    line_ind+=1
            elif nb == 2:
                for i in range(2):
                    line = critface.paths[sad][i]
                    if len(line) > minimum_length:
                        write_polyline_thresholded(f, line, 1, line_ind, thresh, vert_dict, edge_dict, face_dict)
                        line_ind+=1
                
    # now write sad to min
    for critedge in MorseComplex.CritEdges.values():
        counts = Counter(critedge.connected_minima)
        for minimum, nb in counts.items():
            if nb == 1:
                line = critedge.paths[minimum]
                if len(line) > minimum_length:
                    write_polyline_thresholded(f, line, 0, line_ind, thresh, vert_dict, edge_dict, face_dict)
                    line_ind+=1
            elif nb == 2:
                for i in range(2):
                    line = critedge.paths[minimum][i]
                    if len(line) > minimum_length:
                        write_polyline_thresholded(f, line, 0, line_ind, thresh, vert_dict, edge_dict, face_dict)
                        line_ind+=1
            
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing MorseComplex pline file for persistence', MorseComplex.persistence, 'and threshold', thresh, ':', time_writing_file)