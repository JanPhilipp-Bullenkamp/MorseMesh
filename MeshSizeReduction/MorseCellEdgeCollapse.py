import numpy as np
import timeit

class MorseCells:
    def __init__(self, MorseComplex, rawdata, collapse_iterations=8, threshold=7):
        
        self.threshold =  threshold
        self.rawdata = rawdata
        
        self.C = MorseComplex.C
        self.Paths = MorseComplex.Paths
        
        self.data = MorseComplex.data
        self.N = MorseComplex.N
        
        # only implemented (and probably needed) for simplicial 3D complex so far
        if self.N == 3:
            start_eff3 = timeit.default_timer()
            self.boundary_points = self._get_boundary_points()
            #print('Number boundary points:',len(self.boundary_points))
            
            self.new_vertices={}
            self.new_faces = []
        
            self.replaced_faces = []
            
            self._add_vertices()
            self._clean_data()
            
            self.nonboundary = self._get_nonboundary_points()
            #print('Number nonboundary:',len(self.nonboundary)) 
            
            self.MorseCells = self._create_Morse_cells()
            
            
            self.data['link'] = {}
            self.data['position'] = {}
            
            self._add_links_and_positions()
            #print('Added links and Positions to self.data dictionary')
            
            self.index = len(self.rawdata.elements[0].data) + len(self.new_vertices) 
            
            time_eff3 = timeit.default_timer() - start_eff3
            print('Time preparing Morse cells:', time_eff3)
            
            
            start_eff2 = timeit.default_timer()
            
            number_of_collapses = collapse_iterations
            for i in range(number_of_collapses):
                #print('/////////Start Iteration',i,'//////////////')
                self._collapse_Morse_Cell()
                self._collapse_Morse_Cell_boundary()
                
            
            
            time_eff2 = timeit.default_timer() - start_eff2
            print('Time collapsing edges in Morse cells:', time_eff2,' (for',number_of_collapses,'times)')
            
            
            
            
    def _collapse_Morse_Cell(self):
        # iterate over morse cells:
        for key in self.MorseCells.keys():
            #check if sufficiently many inner cells 
            if len(self.MorseCells[key]['inner']) > self.threshold:
                
                collapsed = set()
                added = set()
                for vertex in self.MorseCells[key]['inner']:
                    if vertex not in collapsed:
                        closest = self._sort_link_distances(vertex,key)
                        if len(closest) != 0:
                            # need to add here, cause index will be updated in collapse edge
                            added.add(self.index)

                            # maybe needs to be changed (or rather the sort link dist, so that new vertices also count as 'inner'

                            self._collapse_edge(vertex,closest[0])
                            collapsed.add(vertex)
                            collapsed.add(closest[0])
                        
                # update MorseCells inner vertices
                for cell in added:
                    self.MorseCells[key]['inner'].add(cell)
                for cell in collapsed:
                    self.MorseCells[key]['inner'].discard(cell)
                    
                    
    def _collapse_Morse_Cell_boundary(self):            
        for key in self.MorseCells.keys():
            collapsed_bd = set()
            for vertex in self.MorseCells[key]['boundary']:
                if vertex not in collapsed_bd:
                    queue = set()
                    conn = set()
                    coll = set()
                    end = set()
                    
                    if len(self.MorseCells[key]['boundary'].intersection(self.data['link'][vertex])) == 2 and                         len(self.data['link'][vertex].difference(self.MorseCells[key]['boundary'])) == 2:
                        # save the connections
                        for elt in self.data['link'][vertex].difference(self.MorseCells[key]['boundary']):
                            conn.add(elt)
                            
                        # add the new boundaries to queue
                        for elt in self.MorseCells[key]['boundary'].intersection(self.data['link'][vertex]):
                            if elt not in coll and elt not in collapsed_bd:
                                queue.add(elt)
                            
                        # add vertex to collapsed (need to check later wether at least two elts are part
                        coll.add(vertex)
                        
                        while len(queue) != 0:
                            check = queue.pop()
                            
                            if len(self.MorseCells[key]['boundary'].intersection(self.data['link'][check])) == 2 and                                conn == self.data['link'][check].difference(self.MorseCells[key]['boundary']):
                                
                                coll.add(check)
                                
                                # add the new boundaries to queue
                                for elt in self.MorseCells[key]['boundary'].intersection(self.data['link'][check]):
                                    if elt not in coll and elt not in collapsed_bd:
                                        queue.add(elt)
                                        
                                        
                            elif conn.issubset( self.data['link'][check].difference(self.MorseCells[key]['boundary']) ):
                                
                                end.add(check)
                                        
                        # need to check wether we have a two ends with cells in between that can be collapsed
                        if len(end)==2:
                            # remove coll from all other boundaries
                            for rem in coll:
                                for cellkey in self.MorseCells.keys():
                                    if cellkey != key and rem in self.MorseCells[cellkey]['boundary']:
                                        self.MorseCells[cellkey]['boundary'].discard(rem)
                            
                            
                            # remove coll points from links of ends and conns
                            for inn in conn:
                                for rem in coll:
                                    self.data['link'][inn].discard(rem)
                            for endpt in end:
                                for rem in coll:
                                    self.data['link'][endpt].discard(rem)
                                
                                # add new links btw ends
                                for elt in end:
                                    if elt != endpt:
                                        self.data['link'][endpt].add(elt)
                        
                            # delete coll points and add to collapsed for later iterations and remove
                            for rem in coll:
                                collapsed_bd.add(rem)
                                del self.data['position'][rem]
                                del self.data['link'][rem]
                                del self.data['vertex'][rem]
                                del self.data['star'][rem]
                                
            # need to remove from this morse cell boundary 
            for cell in collapsed_bd:
                self.MorseCells[key]['boundary'].discard(cell)
                    
    def _collapse_Morse_Cell_boundary2(self):            
        for key in self.MorseCells.keys():
            collapsed_bd = set()
            for vertex in self.MorseCells[key]['boundary']:
                if vertex not in collapsed_bd:
                    queue = set()
                    conn = set()
                    coll = set()
                    end = set()
                    
                    if len(self.data['link'][vertex].difference(self.MorseCells[key]['boundary'])) == 2 and len(self.MorseCells[key]['boundary'].intersection(self.data['link'][vertex])) == 2:
                        # save the connections
                        for elt in self.data['link'][vertex].difference(self.MorseCells[key]['boundary']):
                            conn.add(elt)
                            
                        # add the new boundaries to queue
                        for elt in self.MorseCells[key]['boundary'].intersection(self.data['link'][vertex]):
                            if elt not in coll and elt not in collapsed_bd:
                                queue.add(elt)
                        # add vertex to collapsed (need to check later wether at least two elts are part
                        coll.add(vertex)
                        
                        while len(queue) != 0:
                            check = queue.pop()
                            if conn == self.data['link'][check].difference(self.MorseCells[key]['boundary']) and len(self.MorseCells[key]['boundary'].intersection(self.data['link'][check])) == 2:
                                coll.add(check)
                                
                                # add the new boundaries to queue
                                for elt in self.MorseCells[key]['boundary'].intersection(self.data['link'][check]):
                                    if elt not in coll and elt not in collapsed_bd:
                                        queue.add(elt)
                                        
                                        
                            elif conn.issubset( self.data['link'][check].difference(self.MorseCells[key]['boundary']) ):
                                end.add(check)
                                
                        if len(end) != 2 and len(coll) > 2:
                            temp = set()
                            for elt in coll:
                                if len(coll.intersection(self.data['link'][elt])) == 1 and coll.intersection(self.data['link'][elt]) not in end:
                                    end.add(elt)
                                    temp.add(elt)
                            for t in temp:
                                coll.remove(t)
                                        
                        # need to check wether we have a two ends with cells in between that can be collapsed
                        if len(end)==2:
                            # remove coll from all other boundaries
                            print('Found',len(coll),'to collapse')
                            for rem in coll:
                                for cellkey in self.MorseCells.keys():
                                    if cellkey != key and rem in self.MorseCells[cellkey]['boundary']:
                                        self.MorseCells[cellkey]['boundary'].discard(rem)
                            
                            
                            # remove coll points from links of ends and conns
                            for inn in conn:
                                for rem in coll:
                                    self.data['link'][inn].discard(rem)
                            for endpt in end:
                                for rem in coll:
                                    self.data['link'][endpt].discard(rem)
                                
                                # add new links btw ends
                                for elt in end:
                                    if elt != endpt:
                                        self.data['link'][endpt].add(elt)
                        
                            # delete coll points and add to collapsed for later iterations and remove
                            for rem in coll:
                                collapsed_bd.add(rem)
                                del self.data['position'][rem]
                                del self.data['link'][rem]
                                del self.data['vertex'][rem]
                                del self.data['star'][rem]
                            
                                
            # need to remove from this morse cell boundary 
            for cell in collapsed_bd:
                self.MorseCells[key]['boundary'].discard(cell)
    
    
                            
                '''
                FIND NEIGHBOURS AND CREATE LINKS DO THE SAME THING => SIMPLIFY CODE
                '''
                       
                    
    def _collapse_edge(self,vert1,vert2):
        new_position = (self.data['position'][vert1]+self.data['position'][vert2])/2
        new_index = self.index
        self.index += 1
        
        # add new vert to data and MorseCell
        self.data['position'][new_index] = new_position
        self.data['link'][new_index] = set()
        self.data['vertex'][new_index] = 0
        self.data['star'][new_index] = {}
        
        # add new link connections for new vert
        for linkelt in self.data['link'][vert1]:
            if linkelt != vert2:
                self.data['link'][new_index].add(linkelt)
                self.data['link'][linkelt].add(new_index)
                self.data['link'][linkelt].discard(vert1)
                self.data['link'][linkelt].discard(vert2)
                
        for linkelt in self.data['link'][vert2]:
            if linkelt != vert1:
                self.data['link'][new_index].add(linkelt)
                self.data['link'][linkelt].add(new_index)
                self.data['link'][linkelt].discard(vert1)
                self.data['link'][linkelt].discard(vert2)
                
        # remove vert1 and vert2 from data
        del self.data['position'][vert1]
        del self.data['position'][vert2]
        del self.data['link'][vert1]
        del self.data['link'][vert2]
        del self.data['vertex'][vert1]
        del self.data['vertex'][vert2]
        del self.data['star'][vert1]
        del self.data['star'][vert2]
        
        
        # new faces??
        
        
        
    def _boundary_collapse_condition(self,vert,key):
        # should check wether boundary can be collapsed and return closest boundary that can be collapsed as well
        dist = []
        elts = []
        nonbd = []
        for linkelt in self.data['link'][vert]:
            if linkelt in self.MorseCells[key]['boundary']:
                #check wether neighbor has only 2 links to inner points
                counter = 0
                for neighlinkelt in self.data['link'][linkelt]:
                    if neighlinkelt not in self.MorseCells[key]['boundary']:
                        counter+=1
                if counter == 2:
                    dist.append(np.sqrt(np.sum(np.square(self.data['position'][vert]-self.data['position'][linkelt]))))
                    elts.append(linkelt)
            else:
                nonbd.append(linkelt)
                
        # check if exactly 2 nonboundary, and return closest bd that exists
        if len(nonbd) == 2 and len(elts) != 0:
            return np.take(elts,np.argsort(dist))
        else:
            return []
        
    
    def _sort_link_distances_boundary(self,vert,key):
        dist = []
        elts = []
        for ind, linkelt in enumerate(self.data['link'][vert]):
            # check if intersection of links has exaclty two elements and linkelt is not boundary
            if len(self.data['link'][vert].intersection(self.data['link'][linkelt])) == 2 and linkelt in self.MorseCells[key]['boundary']:
                dist.append(np.sqrt(np.sum(np.square(self.data['position'][vert]-self.data['position'][linkelt]))))
                elts.append(linkelt)
        return np.take(elts,np.argsort(dist))
                    
    def _sort_link_distances(self,vert,key):
        # rewrite to: check if closest link fulfills link condition
        dist = []
        elts = []
        for linkelt in self.data['link'][vert]:
            dist.append(np.sqrt(np.sum(np.square(self.data['position'][vert]-self.data['position'][linkelt]))))
            elts.append(linkelt)
            
        closest = np.take(elts,np.argsort(dist))[0]
        #secondclosest = np.take(elts,np.argsort(dist))[1]
        # check if intersection of links has exaclty two elements and linkelt is not boundary
        if len(self.data['link'][vert].intersection(self.data['link'][closest])) == 2 and closest in self.MorseCells[key]['inner']:
            return [closest]
        #elif len(self.data['link'][vert].intersection(self.data['link'][secondclosest])) == 2 and secondclosest in self.MorseCells[key]['inner']:
        #    return [secondclosest]
        else:
            return []
                
        
    def _add_links_and_positions(self):
        for vert in self.data['vertex'].keys():
            self.data['link'][vert] = set()
            
            # old vertices positions
            if vert < len(self.rawdata.elements[0].data):
                self.data['position'][vert] = np.array([self.rawdata.elements[0].data[vert][0],
                                                        self.rawdata.elements[0].data[vert][1],
                                                        self.rawdata.elements[0].data[vert][2]])
            
            # add links
            for cell in self.data['star'][vert].keys():
                if np.array(cell).shape == (3,):
                    self.data['link'][vert].add(cell[0])
                    self.data['link'][vert].add(cell[1])
                    self.data['link'][vert].add(cell[2])
                    
            # remove elt itself from link
            self.data['link'][vert].remove(vert)
                
        # new vertices positions
        for value in self.new_vertices.values():
            vert = value[0]
            position = value[1]
            self.data['position'][int(vert)] = np.array(position)
            
            
        
        ''' BACKUP IF NEW VERSION DOESNT WORK. NEW VERSION CAUSE CLEAN_DATA ALSO UPDATES THE STARS OF THE VERTICES
        # add old vertices and their positions and old links
        i=0
        for vert in self.rawdata.elements[0].data:
            self.data['link'][int(i)] = set()
            self.data['position'][int(i)] = np.array([vert[0],vert[1],vert[2]])
            for cell in self.data['star'][int(i)].keys():
                if np.array(cell).shape == (3,):
                    self.data['link'][int(i)].add(cell[0])
                    self.data['link'][int(i)].add(cell[1])
                    self.data['link'][int(i)].add(cell[2])
            i+=1
        
        # add new vertices with position (without links for now)
        for key, value in self.new_vertices.items():
            vert = value[0]
            position = value[1]
            self.data['link'][int(vert)] = set()
            self.data['position'][int(vert)] = np.array(position)
            
        # remove links generated by replaced faces (some will be reconnected by the new faces)
        for cell in self.replaced_faces:
            do=0

        # add new links from the new added faces
        '''
        
        
    def _create_Morse_cells(self):
        MorseCells = {}
        while len(self.nonboundary) != 0:
            elt = self.nonboundary.pop()
            MorseCells[elt] = {}
            MorseCells[elt]['boundary'] = set()
            MorseCells[elt]['inner'] = set()
            MorseCells[elt]['inner'].add(elt)
            
            Queue = set()
            Queue.add(elt)
                    
            while len(Queue) != 0:
                queue_elt = Queue.pop()
                neighbors = self._find_neighbors(queue_elt)
                for cell in neighbors:
                    if cell in self.boundary_points:
                        MorseCells[elt]['boundary'].add(cell)
                    elif cell in self.nonboundary:
                        self.nonboundary.remove(cell)
                        MorseCells[elt]['inner'].add(cell)
                        Queue.add(cell)
                        
        return MorseCells
    
            
    def _find_neighbors(self, vertex):
        neighbors = set()
        for cell in self.data['star'][vertex].keys():
            if np.array(cell).shape == (3,):
                for i in range(3):
                    neighbors.add(cell[i])
                    
        neighbors.remove(vertex)
        return neighbors
    
    def _get_nonboundary_points(self):
        nonboundary = set()
        for vertex in self.data['vertex'].keys():
            nonboundary.add(vertex)
        for bd in self.boundary_points:
            if np.array(bd).shape == ():
                nonboundary.remove(bd)
                
        return nonboundary
            
    def _get_boundary_points(self):
        boundary_points = set()
        for key in self.Paths.keys():
            for destination, path in self.Paths[key].items():
                for cell in path:
                    boundary_points.add(cell)

        return boundary_points
            
        
        
    def _clean_data(self):
        
        # add new vert to vertex data and initialize their stars
        for key, value in self.new_vertices.items():
            index = value[0]
            
            #dont need height value so far, so just add 0 for new vertices
            self.data['vertex'][int(index)] = 0
            self.data['star'][int(index)] = {}
            self.boundary_points.add(int(index))
        
        # remove replaced faces from stars
        for face in self.replaced_faces:
            for i in range(3):
                self.data['star'][face[i]].pop(face,None)
                
        # add new faces ( dont need height_values so far, so just put to (0,0,0) for now)        
        for face in self.new_faces:
            for i in range(3):
                self.data['star'][face[i]][face] = tuple((0,0,0))
            
            
    def _add_vertices(self):
        
        index = len(self.rawdata.elements[0].data)
        for cell in self.boundary_points:
                
            if np.array(cell).shape == (3,):
                # add up to 3 vertices (dependeing on the 1 cells surrounding it and add min 3, max 6 faces
                self.new_vertices[cell] = tuple((index, self._midpoint_coordinates(cell)))
                index += 1
                
                adj_1cells = self._adjacent_1cells(cell)
                # adja cell [0] is true or false, true if in boundary and need a new vertex
                # adja cell[1] is tuple of 1 cell (if false still gives onecell, but doesnt need a new vertex)
                
                for adja_cell in adj_1cells:
                    
                    # case vertex needs to be created and does not exist yet
                    if adja_cell[0] and (adja_cell[1] not in self.new_vertices.keys()):
                        self.new_vertices[adja_cell[1]] = tuple((index, self._edgepoint_coordinates(adja_cell[1])))
                        index += 1
                        self.new_faces.append((index-1, self.new_vertices[cell][0], adja_cell[1][0]))
                        self.new_faces.append((index-1, self.new_vertices[cell][0], adja_cell[1][1]))
                        
                    # case no vertex needs to be created, so just add the face
                    elif not adja_cell[0]:
                        self.new_faces.append((adja_cell[1][0], adja_cell[1][1], self.new_vertices[cell][0]))
                    
                    # case vertex has been created already, just add the faces
                    elif adja_cell[0] and (adja_cell[1] in self.new_vertices.keys()):
                        self.new_faces.append((self.new_vertices[adja_cell[1]][0], self.new_vertices[cell][0], adja_cell[1][0]))
                        self.new_faces.append((self.new_vertices[adja_cell[1]][0], self.new_vertices[cell][0], adja_cell[1][1]))
                
                self.replaced_faces.append(cell)
                
            elif np.array(cell).shape == (2,):
                cofaces = self._check_adjacent_twocells(cell)
                
                # need to check wether the edge is not at the boundary of the complex
                if len(cofaces) == 2:
                    # case both are boundarycells -> nothing to be done, will be dealt with from the twocells
                    if cofaces[0] in self.boundary_points and cofaces[1] in self.boundary_points:
                        continue

                    # two casees: one in boundary cells: need too see wether we have to initiate, and than add faces
                    if cofaces[0] in self.boundary_points and cofaces[1] not in self.boundary_points:
                        if cell in self.new_vertices.keys():
                            self.new_faces.append((self.new_vertices[cell][0], cell[0], tuple((set(cell).symmetric_difference(cofaces[1])))[0])) 
                            self.new_faces.append((self.new_vertices[cell][0], cell[1], tuple((set(cell).symmetric_difference(cofaces[1])))[0])) 

                        else:
                            self.new_vertices[cell] = tuple((index, self._edgepoint_coordinates(cell)))
                            index += 1
                            self.new_faces.append((self.new_vertices[cell][0], cell[0], tuple((set(cell).symmetric_difference(cofaces[1])))[0])) 
                            self.new_faces.append((self.new_vertices[cell][0], cell[1], tuple((set(cell).symmetric_difference(cofaces[1])))[0])) 

                        self.replaced_faces.append(cofaces[1])

                    # second part with swapped roles coface[0] and [1]
                    if cofaces[1] in self.boundary_points and cofaces[0] not in self.boundary_points:
                        if cell in self.new_vertices.keys():
                            self.new_faces.append((self.new_vertices[cell][0], cell[0], tuple((set(cell).symmetric_difference(cofaces[0])))[0])) 
                            self.new_faces.append((self.new_vertices[cell][0], cell[1], tuple((set(cell).symmetric_difference(cofaces[0])))[0])) 

                        else:
                            self.new_vertices[cell] = tuple((index, self._edgepoint_coordinates(cell)))
                            index += 1
                            self.new_faces.append((self.new_vertices[cell][0], cell[0], tuple((set(cell).symmetric_difference(cofaces[0])))[0])) 
                            self.new_faces.append((self.new_vertices[cell][0], cell[1], tuple((set(cell).symmetric_difference(cofaces[0])))[0])) 

                        self.replaced_faces.append(cofaces[0])

                    # case both not in boundary cells: than in 0101010101 sequence and no need to add new cells
                    if cofaces[0] not in self.boundary_points and cofaces[1] not in self.boundary_points:
                        continue
                
                # case: edge has not 2 cofaces (so only one probably)
                else:
                    continue

                    
                    
        return 0
    
    
                
    def _check_adjacent_twocells(self, onecell):
        twocells = []
        for cell in self.data['star'][onecell[0]].keys():
            if set(onecell).issubset(cell):
                twocells.append(cell)
                
        twocells.remove(onecell)
        return twocells
                
    def _edgepoint_coordinates(self, onecell):
        x, y, z = 0, 0, 0
        for i in range(2):
            x += self.rawdata.elements[0].data[onecell[i]][0]
            y += self.rawdata.elements[0].data[onecell[i]][1]
            z += self.rawdata.elements[0].data[onecell[i]][2]
            
        return tuple((x/2,y/2,z/2))
        
                
    def _midpoint_coordinates(self, twocell):
        x, y, z = 0, 0, 0
        for i in range(3):
            x += self.rawdata.elements[0].data[twocell[i]][0]
            y += self.rawdata.elements[0].data[twocell[i]][1]
            z += self.rawdata.elements[0].data[twocell[i]][2]
            
        return tuple((x/3,y/3,z/3))
                
                
    def _adjacent_1cells(self, twocell):
        adj_cells = []
        
        # check first boundary
        if tuple((twocell[0],twocell[1])) in self.boundary_points:
            adj_cells.append(tuple((True, tuple((twocell[0],twocell[1])))))
        elif tuple((twocell[1],twocell[0])) in self.boundary_points:
            adj_cells.append(tuple((True, tuple((twocell[1],twocell[0])))))
        else:
            adj_cells.append(tuple((False, tuple((twocell[1],twocell[0])))))
        
        # check second boundary
        if tuple((twocell[0],twocell[2])) in self.boundary_points:
            adj_cells.append(tuple((True, tuple((twocell[0],twocell[2])))))
        elif tuple((twocell[2],twocell[0])) in self.boundary_points:
            adj_cells.append(tuple((True, tuple((twocell[2],twocell[0])))))
        else:
            adj_cells.append(tuple((False, tuple((twocell[2],twocell[0])))))
            
        # check third boundary
        if tuple((twocell[1],twocell[2])) in self.boundary_points:
            adj_cells.append(tuple((True, tuple((twocell[1],twocell[2])))))
        elif tuple((twocell[2],twocell[1])) in self.boundary_points:
            adj_cells.append(tuple((True, tuple((twocell[2],twocell[1])))))
        else:
            adj_cells.append(tuple((False, tuple((twocell[1],twocell[2])))))
            
        return adj_cells

