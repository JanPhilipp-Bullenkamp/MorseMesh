import numpy as np
import timeit
from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty

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
    
      
def write_overlay_ply_file(input_file, points, target_file, color_correct=[0,0,255], color_wrong=[255,0,0]):
    start_timer = timeit.default_timer()
    
    with open(target_file +"_OverlayCorrect.ply", "w") as f:
        # write points
        rawdata = PlyData.read(input_file)
        write_header(f, len(rawdata['vertex']))

        print("Total correct points:", len(points), " of ", len(rawdata['vertex']))
        print("That is: ", len(points)/len(rawdata['vertex'])*100,"%")
        for ind, pt in enumerate(rawdata['vertex']):
            if ind in points:
                f.write(str(pt['x']) + " " + str(pt['y']) + " " + str(pt['z']) + " " 
                        + str(color_correct[0]) + " " + str(color_correct[1]) + " " + str(color_correct[2]) + "\n") 
            else:
                f.write(str(pt['x']) + " " + str(pt['y']) + " " + str(pt['z']) + " " 
                        + str(color_wrong[0]) + " " + str(color_wrong[1]) + " " + str(color_wrong[2]) + "\n") 
        
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing overlay for correct points : ', time_writing_file)
    
    