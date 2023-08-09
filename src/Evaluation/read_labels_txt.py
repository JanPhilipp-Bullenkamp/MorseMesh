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

def read_labels_txt(filename, params=False):
    labels = {}
    pers = None
    high_thr = None
    low_thr = None
    merge_thr = None
    with open(filename, "r") as f:
        ind = 0
        for line in f:
            if line[0] == "#":
                if params:
                    if ind == 3:
                        pers = float(line.split()[-1])
                    if ind == 4:
                        high_thr = float(line.split()[-1])
                    if ind == 5:
                        low_thr = float(line.split()[-1])
                    if ind == 6:
                        merge_thr = float(line.split()[-1])
                    ind += 1
                else:
                    continue
            else:
                ind = int(line.split()[0])
                label = int(line.split()[1])
                
                if label not in labels.keys():
                    labels[label] = set()
                    labels[label].add(ind)
                else:
                    labels[label].add(ind)
                
    if params:
        return labels, pers, high_thr, low_thr, merge_thr
    else:
        return labels