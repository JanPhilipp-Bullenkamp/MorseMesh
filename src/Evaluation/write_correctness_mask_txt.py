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

def write_header(file, correctness, gt_file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Compared with Groundtruth: " + str(gt_file)        +"\n")
    file.write("# | Correctly calassified: " + str(correctness)  +    "% \n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")
    
def write_correctness_mask_txt(total_points: int, 
                               points: set, 
                               gt_file: str, 
                               target_file: str, 
                               label_correct: int = 1, 
                               label_wrong: int = 2):
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
    