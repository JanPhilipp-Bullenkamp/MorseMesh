def write_header(file, correctness, gt_file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Compared with Groundtruth: " + str(gt_file)        +"\n")
    file.write("# | Correctly calassified: " + str(correctness)  +    "% \n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")
    
def write_correctness_mask_txt(total_points, points, gt_file, target_file, label_correct=1, label_wrong=2):
    if label_wrong == label_correct:
        raise ValueError('cannot label correct and wrong points the same')
    
    correctness = len(points)/total_points*100
    
    f = open(target_file + ".txt", "w")
    write_header(f, correctness, gt_file)
    
    for ind in range(total_points):
        if ind in points:
            # label for correct points
            f.write(str(ind) + " " + str(label_correct) + "\n")
        else:
            # label for wrong points
            f.write(str(ind) + " " + str(label_wrong) + "\n") 
        
    f.close()
    