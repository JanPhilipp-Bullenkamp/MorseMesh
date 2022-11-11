import numpy as np
import timeit

def write_header(file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")
    
def write_header_params(file, pers, thr_high, thr_low, merge_thr):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Persistence: "+ str(pers)+"\n")
    file.write("# | High edge Threshold: "+ str(thr_high)+"\n")
    file.write("# | Low edge Threshold: "+ str(thr_low)+"\n")
    file.write("# | Merge Threshold: "+ str(merge_thr)+"\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")
    
def write_Cell_labels_txt_file(label_dict, target_file, params = None):
    start_timer = timeit.default_timer()
    
    with open(target_file + ".txt", "w") as f:
        if params == None:
            write_header(f)
        elif len(params) == 4:
            pers, thr_high, thr_low, merge_thr = params
            write_header_params(f, pers, thr_high, thr_low, merge_thr)
        else:
            raise ValueError("The params variable needs the 4 parameters: pers, thr_high, thr_low, merge_thr!")

        # write labels
        for label, indices in enumerate(label_dict.values()):
            for index in indices.vertices:
                f.write(str(index) + " " + str(label+1) + "\n")
            
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing label txt file:', time_writing_file)
    
def write_funval_thresh_labels_txt_file(vert_dict, thresh, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + str(thresh) + "thresh.txt", "w")
      
    write_header(f)
    
    # write labels
    for ind, vert in vert_dict.items():
        if vert.fun_val < thresh:
            f.write(str(ind) + " " +str(1) + "\n")
        else:
            f.write(str(ind) + " " +str(2) + "\n")
        
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing label txt file:', time_writing_file)
 