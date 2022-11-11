import numpy as np
import timeit
from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty

def write_header(file, correctness, gt_file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Compared with Groundtruth: " + str(gt_file)        +"\n")
    file.write("# | Correctly calassified: " + str(correctness)  +    "% \n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")
    
def write_labels_txt_file(total_points, points, gt_file, target_file, label_correct=1, label_wrong=2):
    start_timer = timeit.default_timer()
    
    if label_wrong == label_correct:
        raise ValueError('cannot label correct and wrong points the same')
    
    # write points
    #rawdata = PlyData.read(input_file)
    
    correctness = len(points)/total_points*100
    #print("Total correct points:", len(points), " of ", len(rawdata['vertex']))
    print(target_file,"\n"+"has correctness of: ", correctness,"%")
    
    f = open(target_file + "_correct.txt", "w")
    write_header(f, correctness, gt_file)
    
    for ind in range(total_points):
        if ind in points:
            # label for correct points
            f.write(str(ind) + " " + str(label_correct) + "\n")
        else:
            # label for wrong points
            f.write(str(ind) + " " + str(label_wrong) + "\n") 
        
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing correctness label txt file:', time_writing_file)
    
    return correctness
    