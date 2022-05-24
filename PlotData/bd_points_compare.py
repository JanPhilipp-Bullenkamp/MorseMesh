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
    file.write(str(vert_dict[vert].x) + " " + str(vert_dict[vert].y) + " " + str(vert_dict[vert].z) + " ") 
    file.write(str(color[0]) + " " + str(color[1]) + " " + str(color[2]) + "\n")
        
def write_overlay_bd(bd_points, vert_dict, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file +"_OverlayBD.ply", "w")
    
    nb_points = len(bd_points)
    write_header(f, nb_points)
    
    for vert in bd_points:
        write_vertex(f, vert, vert_dict, color=[255,0,0])
        
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing overlay file for bd: ', time_writing_file)