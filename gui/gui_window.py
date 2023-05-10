import numpy as np

import vtk
from PyQt5.QtWidgets import QGridLayout, QWidget, QSizePolicy
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

color_list = [[255,0,0],  #red
              [0,0,255], # blue
              [0,255,0], #lime
              [255,255,0], # yellow
              [0,255,255], #cyan
              [255,0,255], #magenta
              [192,192,192], #silver
              [128,0,0], #maroon
              [128,128,0], #olive
              [0,128,0], # green
              [128,0,128], #purple
              [0,128,128], #teal
              [0,0,128] #navy
             ]

class CustomInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self):
        self.AddObserver("MouseWheelForwardEvent", self.zoomIn)
        self.AddObserver("MouseWheelBackwardEvent", self.zoomOut)

    def zoomIn(self, obj, event):
        self.GetCurrentRenderer().ResetCameraClippingRange()
        self.GetCurrentRenderer().GetActiveCamera().Zoom(1.1)
        self.GetInteractor().GetRenderWindow().Render()
    
    def zoomOut(self, obj, event):
        self.GetCurrentRenderer().ResetCameraClippingRange()
        self.GetCurrentRenderer().GetActiveCamera().Zoom(0.9)
        self.GetInteractor().GetRenderWindow().Render()

class Window:
    def __init__(self):
        self.window = QWidget()
        #self.window.setGeometry(100,100,1300,1300)
        self.window.setWindowTitle("MorseMesh")
        self.layout = QGridLayout()

        # Create the VTK widget and add it to the layout
        self.vtkWidget = QVTKRenderWindowInteractor(self.window)
        self.layout.addWidget(self.vtkWidget, 0,0)
        ren = vtk.vtkRenderer()
        ren.SetBackground(1, 1, 1)
        self.vtkWidget.GetRenderWindow().AddRenderer(ren)
        interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        style = CustomInteractorStyle()
        interactor.SetInteractorStyle(style)
        self.window.setLayout(self.layout)
        self.window.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.window.setMinimumSize(800,800)
        self.window.show()

    def print_vertex_info(self, points):
        interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        key = interactor.GetKeySym()
        print(key)
        if key == 'i':
            # Get the mouse position
            mouse_x, mouse_y = interactor.GetEventPosition()

            # Get the viewport and camera
            viewport = interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().GetViewport()
            print(viewport)
            camera = interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().GetActiveCamera()

            # Convert the mouse position to world coordinates
            mouse_pos = vtk.vtkCoordinate()
            mouse_pos.SetCoordinateSystemToNormalizedViewport()
            mouse_pos.SetValue((mouse_x - viewport[0]) / (viewport[2] - viewport[0]), 
                               (mouse_y - viewport[1]) / (viewport[3] - viewport[1]))
            world_pos = mouse_pos.GetComputedWorldValue(camera)
            world_pos = (world_pos[0], world_pos[1], 0)

            # Find the closest point to the mouse position
            closest_point = None
            min_distance = float('inf')
            for i in range(points.GetNumberOfPoints()):
                point = points.GetPoint(i)
                distance = vtk.vtkMath.Distance2BetweenPoints(point, world_pos)
                if distance < min_distance:
                    closest_point = point
                    min_distance = distance

            # Print the information about the closest point
            if closest_point is not None:
                print(f"Closest vertex: ({closest_point[0]:.2f}, "
                      f"{closest_point[1]:.2f}, {closest_point[2]:.2f})")


    def update_mesh(self, vert_dict: dict, face_dict: dict):
        ren = self.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        if ren != None:
            ren.RemoveAllViewProps()

        mesh = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        polys = vtk.vtkCellArray()
        for vert in vert_dict.values():
            points.InsertNextPoint(np.array([vert.x, vert.y, vert.z]))
        for face in face_dict.values():
            polys.InsertNextCell(len(face.indices), np.array(list(face.indices)))
        mesh.SetPoints(points)
        mesh.SetPolys(polys)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(mesh)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Add the mesh actor to the vtk renderer and show the window
        ren.AddActor(actor)
        ren.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()

        interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        interactor.AddObserver('KeyPressEvent', self.print_vertex_info(points))

    def update_mesh_color(self, 
                          label_dict: dict, 
                          partial: bool = False, 
                          cell_structure: bool = True):
        # Get the renderer and mesh actor
        ren = self.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        actor = ren.GetActors().GetLastActor()

        # Get the mapper and the mesh data
        mapper = actor.GetMapper()
        mesh = mapper.GetInput()

        # Set the color of the points in the mesh
        point_data = mesh.GetPointData()
        color_array = vtk.vtkUnsignedCharArray()
        color_array.SetNumberOfComponents(3)
        color_array.SetName("Colors")

        if partial: # write all points in white and update color points afterwards
            number_of_points = mesh.GetNumberOfPoints()
            white = (255, 255, 255)
            for i in range(number_of_points):
                color_array.InsertTypedTuple(i, white)
        if cell_structure:
            for label, cell in label_dict.items():
                cell_color = color_list[label%len(color_list)]
                for ind in cell.vertices:
                    color_array.InsertTypedTuple(ind, (cell_color[0],
                                                       cell_color[1],
                                                       cell_color[2]))
        else:
            for label, points in label_dict.items():
                cell_color = color_list[label%len(color_list)]
                for ind in points:
                    color_array.InsertTypedTuple(ind, (cell_color[0],
                                                       cell_color[1],
                                                       cell_color[2]))
        point_data.SetScalars(color_array)

        # Update the mapper and render the window
        mapper.Update()
        self.vtkWidget.GetRenderWindow().Render()

    def update_fun_val_color(self, vert_dict: dict, value_range: float, min_value: float):
        # Get the renderer and mesh actor
        ren = self.vtkWidget.GetRenderWindow().GetRenderers().GetFirstRenderer()
        actor = ren.GetActors().GetLastActor()

        # Get the mapper and the mesh data
        mapper = actor.GetMapper()
        mesh = mapper.GetInput()

        # Set the color of the points in the mesh
        point_data = mesh.GetPointData()
        color_array = vtk.vtkUnsignedCharArray()
        color_array.SetNumberOfComponents(3)
        color_array.SetName("Colors")
        for ind, vert in vert_dict.items():
            lamb = (vert.fun_val-min_value)/value_range
            color = int(lamb*255) 
            color_array.InsertTypedTuple(ind, (color,color,color))
        point_data.SetScalars(color_array)

        # Update the mapper and render the window
        mapper.Update()
        self.vtkWidget.GetRenderWindow().Render()