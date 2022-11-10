# Morse Theory Mesh Segmentation

Provides a discrete Morse theory framework for 3D mesh data. Work in progress...

# Contents
- [Discrete Morse Theory Introduction](#discrete-morse-theory-introduction)
- [Segmentation Method](#segmentation-method)
- [Requirements](#requirements)
- [Usage](#usage)
# Discrete Morse Theory Introduction

Smooth Morse theory enables to perform topological calculations on a manifold, by just looking at a scalar function (Morse function) on it. Translating this to the discrete case, discrete Morse theory (DMT) aims to do the same on simplicial complexes. While this also works for volumes and higher dimensional data, we are interested in unregular triangular meshes and thereby restrict to 2D surfaces that are embedded in 3D. 

We get a reduced skeleton of the mesh, providing us with topological information, as well as an initial segmentation of the mesh. We can filter out noise from the input scalar function using *persistence* and use the lines of the skeleton to get edges.

<details>
  <summary>More detailed description</summary>

## Setup

Looking at the gradient of the scalar function we get minima, saddle points and maxima, also called critical points, on our surface and we can connect them with lines by following the flow or steepest descent of the gradient. These extremal lines are also called Separatrices and give adjacency information between the critical points.

## Morse-Smale Complex

We get a Morse-Smale complex, which represents the topology of the underlying mesh, by taking the critical points of their respective dimension for the chain groups and the adjacency information as boundary operator. Further the separatrices span a skeleton on the mesh, which leads to separated areas of the mesh enclosed by separatrices. These cells are called Morse cells and give a first segmentation of the mesh.

## Noise Reduction

## Edge Detection
</details>

# Segmentation Method

# Requirements
 
 # Usage

