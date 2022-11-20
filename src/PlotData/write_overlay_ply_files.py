import numpy as np
from collections import Counter

'''
Contains:
write_SalientEdge_overlay_ply_file
write_MSComplex_overlay_ply_file
write_Cell_labels_overlay_ply_file
'''

color_list = [[255,0,0],  #red
              [0,255,0], #lime
              [0,0,255], # blue
              [255,255,0], # yellow
              [0,255,255], #cyan
              [255,0,255], #magenta
              [192,192,192], #silver
              [128,0,0], #maroon
              [128,128,0], #olive
              [0,128,0], # green
              [128,0,128], #purple
              [0,128,128], #teal
              [0,0,128] #navy
             ]

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

def write_Cell_labels_overlay_ply_file(MorseCells, vert_dict, target_file):
    with open(target_file + "_OverlayCells.ply", "w") as f:
        nb_points = 0
        for cell in MorseCells.values():
            nb_points += len(cell.vertices)

        write_header(f, nb_points)

        for label, cells in MorseCells.items():
            cell_color = color_list[label%len(color_list)]
            for ind in cells.vertices:
                write_vertex(f, vert_dict[ind], vert_dict, color=cell_color)

def write_MSComplex_overlay_ply_file(MorseCpx, vert_dict, edge_dict, face_dict, target_file, color_paths=[0,0,0]):
    with open(target_file + "_" + str(MorseCpx.persistence) + "P_OverlayMorseComplex.ply", "w") as f:
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
           
    
def write_SalientEdge_overlay_ply_file(MorseCpx, vert_dict, edge_dict, face_dict, 
                                       thresh_high, thresh_low, 
                                       target_file, color_high=[0,0,0], color_low=[255,255,255]):
    with open(target_file+"_"+str(thresh_low)+"Tlow_"+str(thresh_high)+"Thigh_OverlaySalientEdge.ply", "w") as f:
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