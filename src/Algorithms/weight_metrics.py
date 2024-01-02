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

# idea: percentage of salient edge pts on a boundary between two cells
def compute_weight_saledge(points: set, sal_points: set):
    return len(points.intersection(sal_points))/len(points)

# idea: average fun_val on a boundary between two cells
def compute_weight_funvals(points: set, vert_dict: dict):
    fun_vals = []
    for ind in points:
        fun_vals.append(vert_dict[ind].fun_val)
    return sum(fun_vals)/len(fun_vals)