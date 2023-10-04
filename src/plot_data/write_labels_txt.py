"""
    MorseMesh
    Copyright (C) 2023  Jan Philipp Bullenkamp

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
    
def write_Cell_labels_txt_file(label_dict: dict, 
                               target_file: str, 
                               params = None, 
                               cell_structure: bool = True,
                               enum: bool = True):
    with open(target_file + ".txt", "w") as f:
        if params == None:
            write_header(f)
        elif len(params) == 4:
            pers, thr_high, thr_low, merge_thr = params
            write_header_params(f, pers, thr_high, thr_low, merge_thr)
        else:
            raise ValueError("The params variable needs the 4 "
                             "parameters: pers, thr_high, thr_low, merge_thr!")

        # write labels enumerated
        if enum:
            if cell_structure:
                for label, indices in enumerate(label_dict.values(), start=1):
                    for index in indices.vertices:
                        f.write(str(index) + " " + str(label) + "\n")
            else:
                for label, indices in enumerate(label_dict.values(), start=1):
                    for index in indices:
                        f.write(str(index) + " " + str(label) + "\n")
        else: # not enumerated but key as label
            if cell_structure:
                for label, indices in label_dict.items():
                    for index in indices.vertices:
                        f.write(str(index) + " " + str(label) + "\n")
            else:
                for label, indices in label_dict.items():
                    for index in indices:
                        f.write(str(index) + " " + str(label) + "\n")
    
def write_funval_thresh_labels_txt_file(vert_dict: dict, 
                                        thresh: float, 
                                        target_file: str):
    with open(target_file + "_" + str(thresh) + "thresh.txt", "w") as f:
        write_header(f)

        # write labels
        for ind, vert in vert_dict.items():
            if vert.fun_val < thresh:
                f.write(str(ind) + " " +str(1) + "\n")
            else:
                f.write(str(ind) + " " +str(2) + "\n")

def write_variance_heat_map_labels_txt_file(variance: dict, 
                                            thresh1: float, 
                                            thresh2: float, 
                                            target_file: str):
    with open(target_file + "_" + str(thresh1) + "_" 
              + str(thresh2) + "thresh.txt", "w") as f:
        write_header(f)

        # write labels
        for ind, var in variance.items():
            if var < thresh1:
                f.write(str(ind) + " " +str(1) + "\n")
            elif var >= thresh1 and var < thresh2:
                f.write(str(ind) + " " +str(2) + "\n")
            else:
                f.write(str(ind) + " " +str(3) + "\n")
 