### **1. Load ply file**

Select *Load ply* under the *File* menu. Note that you need a .ply file that contains 
a function value under **quality**. 

#### **Comments on the mesh:**

Please make sure that your mesh has a manifold-like structure, i.e. especially there 
should be no edges with more than 2 adjacent triangles. Holes or boundaries in the
mesh are no problem algorithmically, but depending on the application it might make 
sense to fill them.
To do mesh preprocessing we recommend using e.g. [GigaMesh](https://gigamesh.eu/).

### **2. Compute Morse Complex**

Compute the Morse complex for a loaded mesh in the *Compute* menu under 
*Compute Morse complex*.

### **3. Determine edges**

You can now use the two sliders in the bottom to determine the edges correctly. Just
move them and the mesh will update automatically. 

The upper slider determines a **strong threshold** which includes all edges surpassing this 
threshold, while the lower slider determines the **weak threshold** which adds only edges 
that are below the strong threshold, but above the weak threshold, therefore refining 
the result a bit.

Under *advanced edge detection* in the sidebar you can choose more edge settings, the 
only ones that might be interesting though are the "Separatrix density* which could be 
ticked to *All* or the *Extremal line type*, which can be switched between *ridges* 
and *valleys*. 
### **4. Segmentation**

Use the **Morse segmentation method** or the **Cluster segmentation method** in the 
*Segmentations* menu. 

You can change parameters of the segmentation in the sidebar under *Morse segmentation* 
or *Cluster segmentation*.

### **5. Save result**

YOu can rerun the segmentations until you have a sufficient result. The segmentation 
can be saved as a label.txt file in the *File* menu.