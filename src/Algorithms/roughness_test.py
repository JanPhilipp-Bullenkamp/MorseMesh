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

import numpy as np

def variance_heat_map(vert_dict: dict, mean_fun_val: float, n: int):
    variance = {}

    for ind, vert in vert_dict.items():
        n_neighborhood = vert.get_n_neighborhood(vert_dict, n)
        fun_vals = []
        for elt in n_neighborhood:
            fun_vals.append(np.square(vert_dict[elt].fun_val-mean_fun_val))
        variance[ind] = np.sum(fun_vals)/len(fun_vals)

    return variance


def extremal_points_ratio(vert_dict: dict, extremal_points: set, n: int):
    ratio = {}

    for ind, vert in vert_dict.items():
        n_neighborhood = vert.get_n_neighborhood(vert_dict, n)
        ratio[ind] = len(n_neighborhood.intersection(extremal_points)) / len(n_neighborhood)

    return ratio

