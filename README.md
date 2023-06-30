# MorseMesh

NOT UP TO DATE...

This repo provides code for working with discrete Morse theory on meshes. It contains functions for Morse theory based edge detection and segmentation, a cluster based segmentation using only the edges as well as a graphical user interface to use the methods.

# Contents
- [Quick and Easy Usage](#quick-and-easy-usage)
- [Segmentation Method](#segmentation-method)
- [Dependencies](#dependencies)
- [Visualization](#visualization)
- [License](#license)
- [Contact](#contact)

# Quick and Easy Usage

**You need:** A manifold like mesh (ply file) with a scalar function given in the quality property of the vertices. (E.g. curvature values)

1. Open GUI Tool and load mesh
2. Press ***Compute Morse*** under **Processing**
3. Use sliders to get visually well recognized edges
4. Press ***Segmentation Morse*** or ***Segmentation cluster*** under **Visualization**
5. ***Save segmentation*** under file or run again with different parameters

# Dependencies

- Python 3.x (3.9 definitely works, probably also before)
- plyfile (run pip install plyfile or: https://github.com/dranjan/python-plyfile)

# Visualization
We offer different ways to visualize what's going on: 
1. Label .txt files to be visualized in the GUI tool or imported by GigaMesh.
2. (Overlay .ply files to be loaded on top of the original mesh.)

The first option are .ply files that contain colored points. Loading the original mesh with e.g. MeshLab and than importing the overlay file, allows to visualize (interim) results by enlarging the point size of the overlay file.

The second option is only suitable for Morse cell or segmentation result visualization, but offers a better looking result in these cases. Therefore the original mesh needs to be loaded in GigaMesh and the according labels .txt file should be imported under **File - Import - Import Labels** (confirm YES when asked whether the vertex is in the first column and choose **Labels-Connected Comp.** on the right to see the results.)

# License

The MorseMesh source is published under the [GPL License](https://www.gnu.org/licenses/gpl-3.0.de.html)

# Contact

Jan Philipp Bullenkamp: jan-philipp.bullenkamp (at) informatik.uni-halle.de