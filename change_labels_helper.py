from src.evaluation_and_conversion import label_txt_to_label_dict, label_txt_to_sorted_label_txt, label_dict_to_label_txt

file1 = "/home/jp/Documents/Publications/conforming_results/700_0.03P_0.06-0.02T_0.4.txt"
#old_res/4501_r1.00_n4_v256.volume_0.04P_0.09-0.04T_0.4EP_smallRem.txt" 
# #"/home/jp/Documents/Data/fumane/results/results_old_ridges_morse_wide_range/6626_0.06P_0.055H_0.045L_0.5M.txt" 
# #75_0.04P_0.08H_0.065L_0.3M.txt #2490_0.06P_0.07H_0.065L_0.1M.txt #10356_0.04P_0.05H_0.03L_0.5M.txt
file2 = "/home/jp/Documents/Publications/conforming_results/700_gt_labels.txt"

outfile1 = "/home/jp/Documents/Publications/ready/700_conforming_result_ordered.txt"
outfile2 = "/home/jp/Documents/Publications/ready/700_gt_ordered.txt"

change1 = {
    2:11,
    3:27,
    4:25,
    7:28
}

change2 = {
    2:11,
    5:22,
    3:27,
    4:25,
}

def change_labels(file1: str, file2: str, outfile1: str, outfile2: str, change1: dict=None, change2: dict=None):
    if change1==None and change2==None:
        label_txt_to_sorted_label_txt(file1, outfile1)
        label_txt_to_sorted_label_txt(file2, outfile2)
    else:
        dict_1 = label_txt_to_label_dict(file1)
        dict_2 = label_txt_to_label_dict(file2)
        for old, new in change1.items():
            dict_1[new-1] = dict_1[old-1]
            del dict_1[old-1]
        for old, new in change2.items():
            dict_2[new-1] = dict_2[old-1]
            del dict_2[old-1]
        label_dict_to_label_txt(dict_1, outfile1)
        label_dict_to_label_txt(dict_2, outfile2)

    


if __name__ == '__main__':
    change_labels(file1, file2, outfile1, outfile2, change1, change2)
