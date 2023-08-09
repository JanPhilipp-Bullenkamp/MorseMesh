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

from plyfile import PlyData

def read_labels_from_color_ply(filename: str):
    rawdata = PlyData.read(filename)
    
    labels = {}
    conversion = {}
    
    label = 0
    for ind, pt in enumerate(rawdata['vertex']):
        if tuple((pt['red'], pt['green'], pt['blue'])) not in conversion.keys():
            conversion[ tuple((pt['red'], pt['green'], pt['blue'])) ] = label
            labels[label] = set()
            labels[label].add(ind)
            
            label+=1
        else:
            labels[conversion[ tuple((pt['red'], pt['green'], pt['blue'])) ]].add(ind)
            
    return labels, len(rawdata['vertex'])
         