import numpy as np

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
    
def write_Cell_labels_txt_file(label_dict: dict, target_file: str, params = None):
    with open(target_file + ".txt", "w") as f:
        if params == None:
            write_header(f)
        elif len(params) == 4:
            pers, thr_high, thr_low, merge_thr = params
            write_header_params(f, pers, thr_high, thr_low, merge_thr)
        else:
            raise ValueError("The params variable needs the 4 parameters: pers, thr_high, thr_low, merge_thr!")

        # write labels
        for label, indices in enumerate(label_dict.values(), start=1):
            for index in indices.vertices:
                f.write(str(index) + " " + str(label) + "\n")
    
def write_funval_thresh_labels_txt_file(vert_dict: dict, thresh: float, target_file: str):
    with open(target_file + "_" + str(thresh) + "thresh.txt", "w") as f:
        write_header(f)

        # write labels
        for ind, vert in vert_dict.items():
            if vert.fun_val < thresh:
                f.write(str(ind) + " " +str(1) + "\n")
            else:
                f.write(str(ind) + " " +str(2) + "\n")

def write_variance_heat_map_labels_txt_file(variance: dict, thresh1: float, thresh2: float, target_file: str):
    with open(target_file + "_" + str(thresh1) + "_" + str(thresh2) + "thresh.txt", "w") as f:
        write_header(f)

        # write labels
        for ind, var in variance.items():
            if var < thresh1:
                f.write(str(ind) + " " +str(1) + "\n")
            elif var >= thresh1 and var < thresh2:
                f.write(str(ind) + " " +str(2) + "\n")
            else:
                f.write(str(ind) + " " +str(3) + "\n")
 