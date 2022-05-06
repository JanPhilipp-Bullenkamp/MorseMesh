import numpy as np
import timeit
from collections import Counter

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
    file.write(str(vert_dict[vert].x) + " " + str(vert_dict[vert].y) + " " + str(vert_dict[vert].z) + " ") 
    file.write(str(color[0]) + " " + str(color[1]) + " " + str(color[2]) + "\n")
        
def write_cells_overlay_ply_file(MorseCells, vert_dict, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + "_Cells_overlay.ply", "w")
    
    nb_points = 0
    for cell in MorseCells.values():
        nb_points += len(cell)
        
    write_header(f, nb_points)
    
    for key, cells in MorseCells.items():
        cell_color = color_list[key%len(color_list)]
        for ind in cells:
            write_vertex(f, ind, vert_dict, color=cell_color)
            
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing Cells overlay file:', time_writing_file)