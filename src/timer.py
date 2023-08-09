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

import time
def timed(flag: bool = True):
    def time_fct(function):
        def wrapper(*args, **kwargs):
            before = time.time()
            return_value = function(*args, **kwargs)
            after = time.time()
            fname = function.__name__
            if flag:
                print(f"{fname} took {(after-before):.5f} seconds to execute!")
            return return_value
        return wrapper
    return time_fct