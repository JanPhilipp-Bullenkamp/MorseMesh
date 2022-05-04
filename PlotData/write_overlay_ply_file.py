import numpy as np
import timeit
from collections import Counter

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
        

def write_overlay_ply_file(MorseCpx, vert_dict, edge_dict, face_dict, target_file, color_paths=[0,0,0]):
    start_timer = timeit.default_timer()
    
    f = open(target_file + "_overlay.ply", "w")
    
    path_vert = set()
    path_edges = set()
    path_faces = set()
    for maximum in MorseCpx.CritFaces.keys():
        saddles = Counter(MorseCpx.CritFaces[maximum].connected_saddles)
        for sad, nb in saddles.items():
            if nb == 1:
                # remove first and last elt, as they are in Crit already
                path = MorseCpx.CritFaces[maximum].paths[sad][1:-1]
                # first is face, second edge, so now we start with an edge
                count = 0
                for elt in path:
                    if count%2 == 0:
                        path_edges.add(elt)
                    elif count%2 ==1:
                        path_faces.add(elt)
                    count+=1
                
            elif nb == 2:
                for i in range(2):
                    # remove first and last elt, as they are in Crit already
                    path = MorseCpx.CritFaces[maximum].paths[sad][i][1:-1]
                    # first is face, second edge, so now we start with an edge
                    count = 0
                    for elt in path:
                        if count%2 == 0:
                            path_edges.add(elt)
                        elif count%2 ==1:
                            path_faces.add(elt)
                        count+=1
                        
    for saddle in MorseCpx.CritEdges.keys():
        minima = Counter(MorseCpx.CritEdges[saddle].connected_minima)
        for mini, nb in minima.items():
            if nb == 1:
                # remove first and last elt, as they are in Crit already
                path = MorseCpx.CritEdges[saddle].paths[mini][1:-1]
                # first is face, second edge, so now we start with an edge
                count = 0
                for elt in path:
                    if count%2 == 0:
                        path_vert.add(elt)
                    elif count%2 ==1:
                        path_edges.add(elt)
                    count+=1
                
            elif nb == 2:
                for i in range(2):
                    # remove first and last elt, as they are in Crit already
                    path = MorseCpx.CritEdges[saddle].paths[mini][i][1:-1]
                    # first is face, second edge, so now we start with an edge
                    count = 0
                    for elt in path:
                        if count%2 == 0:
                            path_vert.add(elt)
                        elif count%2 ==1:
                            path_edges.add(elt)
                        count+=1
    
    nb_points = len(MorseCpx.CritVertices) + len(MorseCpx.CritEdges) + len(MorseCpx.CritFaces) + len(path_vert) + len(path_edges) + len(path_faces)
    
    write_header(f, nb_points)
    
    for vert in MorseCpx.CritVertices.values():
        write_vertex(f, vert, vert_dict, color=[255,0,0])
    for ed in MorseCpx.CritEdges.values():
        write_edge(f, ed, vert_dict, color=[0,255,0])
    for fa in MorseCpx.CritFaces.values():
        write_face(f, fa, vert_dict, color=[0,0,255])
        
    for ind in path_vert:
        write_vertex(f, vert_dict[ind], vert_dict, color=color_paths)
    for ind in path_edges:
        write_edge(f, edge_dict[ind], vert_dict, color=color_paths)
    for ind in path_faces:
        write_face(f, face_dict[ind], vert_dict, color=color_paths)
     
        
                        
            
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing overlay file:', time_writing_file)
    