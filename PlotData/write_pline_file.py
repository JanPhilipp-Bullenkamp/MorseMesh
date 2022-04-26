import numpy as np
import timeit

def write_header(file):
    file.write("# +-------------------------------------------------------------------------------+\n")
    file.write("# | PLINE file with polylines                                                     |\n")
    file.write("# +-------------------------------------------------------------------------------+\n")
    file.write("# +------------------------------------------------------------------------------------------------------------------------\n")
    file.write("# | Format: Label No. | Number of Vertices | id1 x1 y1 z1 nx1 ny1 nz1 id2 x2 y2 z2 nx2 ny2 nz2 ... idN xN yN zN nxN nyN nzN\n")
    file.write("# +------------------------------------------------------------------------------------------------------------------------\n")
        
def write_midpoint(file, elt, rawdata):
    x,y,z = 0,0,0
    for ind in elt:
        x += rawdata.elements[0].data[ind][0]
        y += rawdata.elements[0].data[ind][1]
        z += rawdata.elements[0].data[ind][2]
    x = round(x/len(elt), 8)
    y = round(y/len(elt), 8)
    z = round(z/len(elt), 8)
    file.write(" " + str(-1) + " " + str(x) + " " + str(y) + " " + str(z) + " " + str(1.0) + " " + str(0) + " " + str(0))
    
def write_vertex(file, elt, rawdata):
    x = rawdata.elements[0].data[elt][0]
    y = rawdata.elements[0].data[elt][1]
    z = rawdata.elements[0].data[elt][2]
    file.write(" " + str(-1) + " " + str(x) + " " + str(y) + " " + str(z) + " " + str(1.0) + " " + str(0) + " " + str(0))
        
def write_polyline(file, line, line_ind, rawdata):
    
    indices = []
    for elt in line:
        if isinstance(elt, np.int32):
            if elt not in indices:
                indices.append(elt)
                
        elif np.array(elt).shape == (3,):
            if elt not in indices:
                indices.append(elt)
                    
    file.write(str(line_ind) + " " + str(len(indices)))
    for ind in indices:
        if isinstance(ind, np.int32):
            write_vertex(file, ind, rawdata)
                
        elif np.array(ind).shape == (3,):
            write_midpoint(file, ind, rawdata)
    file.write("\n")
    
def _elt_to_ind(elt):
    if isinstance(elt, np.int32):
        return elt
    else:
        return elt[0]
    
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
        elif np.array(elt).shape == (3,):
            if elt not in indices and count%modulo_decimator == 0:
                if rawdata.elements[0].data[_elt_to_ind(elt)][3] > thresh or len(indices) < 3:
                    indices.append(elt)
                    count+=1
                else:
                    break
            else:
                count+=1
                    
    file.write(str(line_ind) + " " + str(len(indices)))
    for ind in indices:
        if isinstance(ind, np.int32):
            write_vertex(file, ind, rawdata)
                
        elif np.array(ind).shape == (3,):
            write_midpoint(file, ind, rawdata)
    file.write("\n")
    

def write_pline_file(C, Paths, rawdata, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + ".pline", "w")
      
    write_header(f)
    
    # write polylines
    line_ind=0
    for keys in Paths.keys():
        for line in Paths[keys].values():
            write_polyline(f, line, line_ind, rawdata)
            line_ind+=1
            
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing pline file:', time_writing_file)
    
def write_pline_file_simplified(C, Paths, rawdata, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + ".pline", "w")
    
    # simplification parameters
    minimum_length = 5
    modulo_decimator = 3
    thresh = 0.15
    
    write_header(f)
    
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
    print('Time writing simplified pline file:', time_writing_file) 