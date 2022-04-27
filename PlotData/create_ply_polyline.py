import numpy as np
import timeit

def write_header(file, nb_points, properties, nb_triangles=0, nb_polylines=0):
    file.write("ply \n")
    file.write("format ascii 1.0 \n")
    file.write("element vertex " + str(nb_points) + "\n")
    for prop in properties:
        if str(prop) != "property list uchar float feature_vector":
            file.write(str(prop) + "\n")
        
    if nb_triangles != 0:
        file.write("element face " + str(nb_triangles) + "\n")
        file.write("property list uchar int vertex_indices\n")
        
    if nb_polylines != 0:
        file.write("element line " + str(nb_polylines) + "\n")
        file.write("property float x\n")
        file.write("property float y\n")
        file.write("property float z\n")
        file.write("property float nx\n")
        file.write("property float ny\n")
        file.write("property float nz\n")
        file.write("property uint32 labelid\n")
        file.write("property list uchar int vertex_indices\n")
    file.write("end_header\n")
    
def write_vertex(file, vertex, properties, color=[-1,-1,-1]):
    if color == [-1,-1,-1]:
        for i, prop in enumerate(properties):
            if str(prop.name) != "feature_vector":
                file.write(str(vertex[i]) + " ")
        file.write("\n")
    else:
        for i, prop in enumerate(properties):
            if ((str(prop.name) != "red") 
                & (str(prop.name) != "green") 
                & (str(prop.name) != "blue")
                & (str(prop.name) != "feature_vector")):
                file.write(str(vertex[i]) + " ")
            elif str(prop.name) == "red":
                file.write(str(color[0]) + " ")
            elif str(prop.name) == "green":
                file.write(str(color[1]) + " ")
            elif str(prop.name) == "blue":
                file.write(str(color[2]) + " ")
        file.write("\n")
        
# only supports x,y,z,r,g,b properties
def write_midpoint(file, elt, rawdata, color=[0,0,0]):
    x,y,z = 0,0,0
    for ind in elt:
        x += rawdata.elements[0].data[ind][0]
        y += rawdata.elements[0].data[ind][1]
        z += rawdata.elements[0].data[ind][2]
    x = round(x/len(elt), 8)
    y = round(y/len(elt), 8)
    z = round(z/len(elt), 8)
    file.write(str(x) + " " + str(y) + " " + str(z) + " " + str(color[0]) + " " + str(color[1]) + " " + str(color[2]) + "\n")
        
        
def write_face(file, face):
    file.write(str(3) + " " + str(face[0][0]) + " " + str(face[0][1]) + " " + str(face[0][2]) + "\n")

def write_face_tuple(file, face):
    file.write(str(3) + " " + str(face[0]) + " " + str(face[1]) + " " + str(face[2]) + "\n")

def write_polyline(file, line, line_ind):
    
    indices = []
    for elt in line:
        if isinstance(elt, np.int32):
            if elt not in indices:
                indices.append(elt)
                
        else:
            for ind in elt:
                if ind not in indices:
                    indices.append(ind)
                    
    file.write("nan nan nan nan nan nan "+ str(line_ind) + " " + str(len(indices)) + " ")
    for ind in indices:
        file.write(str(ind) + " ")
    file.write("\n")
    
def write_polyline_simplified(file, line, line_ind, modulo_decimator, rawdata, thresh):
    
    indices = []
    count = 0
    for elt in line:
        if isinstance(elt, np.int32):
            if elt not in indices and count%modulo_decimator == 0:
                if rawdata.elements[0].data[elt][3] > thresh or len(indices) < 3:
                    indices.append(elt)
                    count+=1
                else:
                    break
            else:
                count+=1
        else:
            for ind in elt:
                if ind not in indices and count%modulo_decimator == 0:
                    if rawdata.elements[0].data[ind][3] > thresh or len(indices) < 3:
                        indices.append(ind)
                        count+=1
                    else:
                        break
                else:
                    count+=1
                    
    file.write("nan nan nan nan nan nan "+ str(line_ind) + " " + str(len(indices)) + " ")
    for ind in indices:
        file.write(str(ind) + " ")
    file.write("\n")
    

def write_ply_file(C, Paths, rawdata, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + ".ply", "w")
    
    # copy properties from input data
    properties = []
    for prop in rawdata.elements[0].properties:
        properties.append(prop)
    
    # count number of polylines required
    lines_number = 0
    for keys in Paths.keys():
        for key in Paths[keys].keys():
            lines_number += 1
    
    write_header(f, len(rawdata.elements[0].data), properties , len(rawdata.elements[1].data), lines_number)
    
    # write points into file and color critical points red
    for ind, point in enumerate(rawdata.elements[0].data):
        write_vertex(f, point, properties)
    # write triangles into file
    for face in rawdata.elements[1].data:
        write_face(f, face)
    # write polylines
    line_ind=0
    for keys in Paths.keys():
        for line in Paths[keys].values():
            write_polyline(f, line, line_ind)
            line_ind+=1
            
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing own file:', time_writing_file)
    
def _elt_to_ind(elt):
    if isinstance(elt, np.int32):
        return elt
    else:
        return elt[0]
    
def write_ply_file_simplified(C, Paths, rawdata, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + ".ply", "w")
    
    # simplification parameters
    minimum_length = 5
    modulo_decimator = 1
    thresh = 0.15
    
    # copy properties from input data
    properties = []
    for prop in rawdata.elements[0].properties:
        properties.append(prop)
    
    # count number of polylines required
    lines_number = 0
    for keys in Paths.keys():
        for key in Paths[keys].keys():
            if len(Paths[keys][key]) > minimum_length:
                if rawdata.elements[0].data[_elt_to_ind(Paths[keys][key][0])][3] > thresh or rawdata.elements[0].data[_elt_to_ind(Paths[keys][key][-1])][3] > thresh:
                    lines_number += 1
    
    write_header(f, len(rawdata.elements[0].data), properties , len(rawdata.elements[1].data), lines_number)
    
    # write points into file and color critical points red
    for ind, point in enumerate(rawdata.elements[0].data):
        #if ind in C[0].keys():
        #    write_vertex(f, point, properties, color=[255,0,0])
        #else:
        write_vertex(f, point, properties)
    # write triangles into file
    for face in rawdata.elements[1].data:
        write_face(f, face)
    # write polylines
    line_ind=0
    for keys in Paths.keys():
        for line in Paths[keys].values():
            if len(line) > minimum_length:
                if rawdata.elements[0].data[_elt_to_ind(line[0])][3] > thresh or rawdata.elements[0].data[_elt_to_ind(line[-1])][3] > thresh:
                    write_polyline_simplified(f, line, line_ind, modulo_decimator, rawdata, thresh)
                    line_ind+=1
            
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing own file:', time_writing_file) 
    
def write_ply_files_pt_ed_tri(C, Paths, rawdata, target_file):
    start_timer = timeit.default_timer()
    
    fbase = open(target_file + "base" + ".ply", "w")
    fedge = open(target_file + "edge" + ".ply", "w")
    fpoint = open(target_file + "point" + ".ply", "w")
    
    propertiesbase = []
    propertiesedge = []
    propertiespoint = []
    for prop in rawdata.elements[0].properties:
        propertiesbase.append(prop)
        wanted = ["x", "y", "z", "red", "green", "blue"]
        if str(prop.name) in wanted:
            propertiesedge.append(prop)
            propertiespoint.append(prop)
        
    
    lines_added = 0
    lines_number = 0
    for keys in Paths.keys():
        for key in Paths[keys].keys():
            lines_added += len(Paths[keys][key])
            lines_number += 1
    
    write_header(fbase, len(rawdata.elements[0].data), propertiesbase , len(rawdata.elements[1].data))
    # don't know length of vertices and yet (changed later)
    write_header(fedge, -1, propertiesedge)
    write_header(fpoint, len(C[0].keys()) + 2*len(C[1].keys()) + 3*len(C[2].keys()), propertiespoint)
    
    # write points into base and points file
    for ind, point in enumerate(rawdata.elements[0].data):
        write_vertex(fbase, point, propertiesbase)
        
        if ind in C[0].keys():
            write_vertex(fpoint, point, propertiespoint, color=[255,0,0])
            
    # write green and blue edges and triangles as points
    for edge in C[1].keys():
        for i in range(2):
            write_vertex(fpoint, rawdata.elements[0].data[edge[i]], propertiespoint, color=[0,255,0])
            
    for face in C[2].keys():
        for i in range(3):
            write_vertex(fpoint, rawdata.elements[0].data[face[i]], propertiespoint, color=[0,0,255])
            
    # write faces into base file
    for face in rawdata.elements[1].data:
        write_face(fbase, face)
        
    fbase.close()
    fpoint.close()
    
    # write path points edge file
    vertex_counter = 0
    visited = set()
    for face in C[2].keys():
        visited.add(face)
        for end_path in Paths[face].keys():
            visited.add(end_path)
            for elt in Paths[face][end_path]:
                if np.array(elt).shape != (2,) and elt not in visited:
                    write_midpoint(fedge, elt, rawdata, color=[255,0,255])
                    vertex_counter += 1
                    visited.add(elt)
                
    for edge in C[1].keys():
        visited.add(edge)
        for end_path in Paths[edge].keys():
            visited.add(end_path)
            for elt in Paths[edge][end_path]:
                if np.array(elt).shape != (2,) and elt not in visited:
                    write_vertex(fedge, rawdata.elements[0].data[elt], propertiesedge, color=[255,0,255])
                    vertex_counter += 1
                    visited.add(elt)
    
    # close fedge file, reopen it and replace with correct vertex and face number
    fedge.close()
    
    fread = open(target_file + "edge" + ".ply", "r")
    filedata = fread.read()
    fread.close()
    
    filedata = filedata.replace("element vertex -1", "element vertex " + str(vertex_counter))
    
    fwriteedge = open(target_file + "edge" + ".ply", "w")
    fwriteedge.write(filedata)
    fwriteedge.close()
    
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing complex own files:', time_writing_file) 
    
    