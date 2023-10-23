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

# Convert groundtruth plys to groundtruth label txts

from src.evaluation_and_conversion import painted_ply_to_label_dict, label_dict_to_label_txt, label_txt_to_sorted_label_txt

import os

folder = "../../Data/test_polyline/"
file = "../../Data/test_polyline/5493_c_1.ply"

def process_folder(folder_name):
    broken = []
    for file in os.listdir(folder_name):
        print("Convert file ", file)
        file_name = file.split(".ply")[0]
        try:
            gt_label_dict = painted_ply_to_label_dict(folder_name+file, clean_thresh=30, connected_components = True)
            label_dict_to_label_txt(gt_label_dict, folder_name+file_name+"_gt_labels")
            label_txt_to_sorted_label_txt(folder_name+file_name+"_gt_labels.txt", folder_name+file_name+"_gt_labels")
        except:
            broken.append(file_name)

    print("Broken files:")
    print(broken)
    
def process_file(filepath):
    file_name = filepath.split("/")[-1].split(".ply")[0]
    file_location = filepath.split(file_name+".ply")[0]
    gt_label_dict = painted_ply_to_label_dict(filepath, clean_thresh=30, connected_components = True)
    label_dict_to_label_txt(gt_label_dict, file_location+file_name+"_gt_labels")
    label_txt_to_sorted_label_txt(file_location+file_name+"_gt_labels.txt", file_location+file_name+"_gt_labels")

if __name__ == '__main__':
    # process folder:
    #process_folder(folder)
    # process single file
    process_file(file)