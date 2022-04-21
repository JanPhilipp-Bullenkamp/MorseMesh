#Load data functions
from LoadData.load_image_data import load_data
from LoadData.load_data3D import load_data3D
# only for Betti number comparison:
from LoadData.load_data_forBettiComparison import load_data_forBettiComparison

#Morse algorithm
from MorseAlgorithms.MorseComplex import MorseComplex
#only for Betti number comparison:
from MorseAlgorithms.BettiNumbers_efficient import BettiViaPairCells

#Mesh size reduction
from MeshSizeReduction.MorseCellEdgeCollapse import MorseCells

#Plotting functions:
#for images:
from PlotData.plot_functions_images import (plot_criticals, 
                                            plot_criticals_with_Paths, 
                                            plot_criticals_with_gradient_vectors,
                                            plot_criticals_with_gradient_vectors_MonoG)
#for ply files
from PlotData.plot_functions_write3Dfile import (write_crit_and_base_filesWITHPATH, 
                                                 write_crit_and_base_files,
                                                 write_crit_and_base_filesWITHPATH_and_new)
from PlotData.plot_reduced_complex import write_crit_and_base_filesWITHPATH_reducedComplex

# 0. Determine filepath and position of the values for the discrete Morse function: (2 is the z value)
path, position = "filename.ply", 2


# 1. Load data:
rawdata, data = load_data3D(path, position)

# 2. Create Morse-Smale Complex:
morsecomplex = MorseComplex(data, simplicial = True, cubical = False)
morsecomplex.info()

# 3. Calculate Betti numbers and create Persistence Diagram:
betti = morsecomplex.calculateBettinumbers()

morsecomplex.plot_persistence_diagram(save=False,filepath='PersistenceDiagram.png')

# 4. Cancel Critical Points:
morsecomplex.CancelCriticalPairs(0.06)
morsecomplex.info()

# 5. Create Morse Cells and Reduce Mesh Size:
coll_iteration = 8
cell_threshold = 7

MorseCells = MorseCells(morsecomplex, rawdata, collapse_iterations=coll_iteration, threshold = cell_threshold)

# 6. Create ply file of the reduced simplicial complex:
target_base_file = 'filename_reduced.ply'
#write_crit_and_base_filesWITHPATH_reducedComplex(morsecomplex.C, morsecomplex.Paths, MorseCells.data, rawdata, target_base_file)
