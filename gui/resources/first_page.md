### **1. Load ply file**

Select *Load ply* under the *File* menu. Note that you need a .ply file that contains 
a function value under **quality**. 

### **2. Compute Morse Complex**

Compute the Morse complex for a loaded mesh in the *Compute* menu under 
*Compute Morse complex*.

### **Comments on the mesh:**

Please make sure that your mesh has a manifold-like structure, i.e. especially there 
should be no edges with more than 2 adjacent triangles. Holes or boundaries in the
mesh are no problem algorithmically, but depending on the application it might make 
sense to fill them.
To do mesh preprocessing we recommend using e.g. [GigaMesh](https://gigamesh.eu/).