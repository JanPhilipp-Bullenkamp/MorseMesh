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

from src.evaluation_and_conversion import label_txt_to_label_dict, label_txt_to_sorted_label_txt, label_dict_to_label_txt

file1 = "/home/jp/Documents/Data/tool_florian/tool_result_ordered.txt"
#old_res/4501_r1.00_n4_v256.volume_0.04P_0.09-0.04T_0.4EP_smallRem.txt" 
# #"/home/jp/Documents/Data/fumane/results/results_old_ridges_morse_wide_range/6626_0.06P_0.055H_0.045L_0.5M.txt" 
# #75_0.04P_0.08H_0.065L_0.3M.txt #2490_0.06P_0.07H_0.065L_0.1M.txt #10356_0.04P_0.05H_0.03L_0.5M.txt
file2 = "/home/jp/Documents/Data/tool_florian/tool_gt_ordered.txt"

outfile1 = "/home/jp/Documents/Data/tool_florian/tool_result_ordered_new"
outfile2 = "/home/jp/Documents/Data/tool_florian/tool_gt_ordered_new"

change1 = {
    2:91,
    23:98,
    53:96,
    21:97,
    12:99,
    51:93,
    55:106,
    31:100,
    30:94,
    8:90,
    36:103,
    6:95,
    41:107,
    45:108,
    9:102,
    10:104,
    15:117,
    28:112,
    52:118,
    46:128,
    35:127,
    54:137,
    47:133,
    60:147,
    61:157,
    58:140
}

change2 = {
    31:138,
    35:137,
    72:131,
    12:134,
    20:132,
    63:144,
    71:147,
    39:145,
    70:149,
    38:155
}

#change1={}
#change2={}

def change_labels(file1: str, file2: str, outfile1: str, outfile2: str, change1: dict=None, change2: dict=None):
    if change1==None and change2==None:
        label_txt_to_sorted_label_txt(file1, outfile1)
        label_txt_to_sorted_label_txt(file2, outfile2)
    else:
        #label_txt_to_sorted_label_txt(file1, outfile1)
        #label_txt_to_sorted_label_txt(file2, outfile2)
        dict_1 = label_txt_to_label_dict(file1,sort_enum=False)
        dict_2 = label_txt_to_label_dict(file2,sort_enum=False)
        for old, new in change1.items():
            dict_1[new] = dict_1[old]
            del dict_1[old]
        for old, new in change2.items():
            dict_2[new] = dict_2[old]
            del dict_2[old]
        label_dict_to_label_txt(dict_1, outfile1)
        label_dict_to_label_txt(dict_2, outfile2)

    


if __name__ == '__main__':
    change_labels(file1, file2, outfile1, outfile2, change1, change2)
