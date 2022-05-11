import numpy as np
import timeit

def write_header(file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | all labels increased by +1, so that we can give     |\n")
    file.write("# | label = 0 for boundary points (unlabelled points)   |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")
    
def write_labels_txt_file(label_dict, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + ".txt", "w")
      
    write_header(f)
    
    # write labels
    for label, indices in label_dict.items():
        if label != "boundary":
            for index in indices:
                f.write(str(index) + " " + str(label+1) + "\n")
        else:
            for index in indices:
                f.write(str(index) + " " + str(0) + "\n")
            
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing label txt file:', time_writing_file)
 