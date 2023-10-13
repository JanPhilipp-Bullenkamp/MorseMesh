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

# Usage:
# Need to update the folder where to write the label txts of the steps in the 
# datastructures.py (at the bottom) in the function call "segment" of the 
# class MorseCells.

from src.morse import Morse

filename = "../../Data/fumane/curvature/31/31_GMOCF_r1.00_n4_v256.volume.ply"

persistence = 0.06
thresh_high = 0.07
thresh_low = 0.06
merge_thresh = 0.2

data = Morse()
data.plot_segmentation_steps(filename, persistence, thresh_high, thresh_low, merge_thresh)