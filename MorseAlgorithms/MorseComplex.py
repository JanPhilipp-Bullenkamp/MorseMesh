from .ProcessLowerStar import ProcessLowerStar, ProcessLowerStarCoface
# not  needed at the moment, kept as backup
#from .ExtractMorseComplex_old import ExtractMorseComplex_old
from .GetSeparatrices import GetSeparatrices
from .CancellationQueue import CancellationQueue
from .BettiNumbers_efficient import BettiViaPairCells, pair_cells
from .PersistenceDiagram import Persistence_Diagram

# improved version
from .ExtractMorseComplex import ExtractMorseComplex

from collections import Counter
import numpy as np
import timeit
from copy import deepcopy


class MorseComplex:
    def __init__(self, data, simplicial = False, cubical = True):
        if simplicial:
            self.N = 3
        elif cubical:
            self.N = 4
        if simplicial and cubical:
            print('Data has to be either simplicial or cubical!')
            raise ValueError
            
        self.data = data
        
        self.C, self.V = ProcessLowerStar(self.data, self.N)
        
        
        self.Facelist, self.max_conn, self.saddle_conn, self.min_conn, self.Paths = ExtractMorseComplex(self.data,self.C,self.V,self.N)
        
        # not needed anymore due to smarter things in Extract MorseComplex2, 
        # only kept for backup if problems occur with ExtractMorseComplex2
        #GetSeparatrices(self.Paths, self.Facelist, self.N)
        
        self.newV = self._create_newV()

        self.partner = None
        
        
    def info(self):
        print('Number of vertices in data:',len(self.data['vertex']))
        print('Number of critical 0-simplices:',len(self.C[0]))
        print('Number of critical 1-simplices:',len(self.C[1]))
        print('Number of critical 2-simplices:',len(self.C[2]))
        print('Euler number from critical simplices:',len(self.C[0])-len(self.C[1])+len(self.C[2]))
        
        
    def CancelCriticalPairs(self, threshold):
        start_eff = timeit.default_timer()
        
        CancelPairs = CancellationQueue()
        # fill queue
        for saddle in self.saddle_conn.keys():
            close = self._get_closest_extremum(saddle)
            if close != None:
                closest, dist = close
                if dist < threshold:
                    CancelPairs.insert(tuple((dist,saddle)))
        
        # work down queue
        while CancelPairs.notEmpty():
            prio, saddle = CancelPairs.pop_front()
            check = self._get_closest_extremum(saddle)
            if check != None:
                closest, dist = check
                if dist <= CancelPairs.check_distance():
                    self._cancel_one_critical_pair(saddle,closest)
                else:
                    CancelPairs.insert(tuple((dist,saddle)))
                    
        time_eff = timeit.default_timer() - start_eff
        print('Time cancel critical points:', time_eff)


    def calculateBettinumbers(self):
        betti, self.partner = BettiViaPairCells(self.C, self.Facelist)
        print('Betti numbers:',betti)
        return betti

    def plot_persistence_diagram(self,pointsize = 3, save = False, filepath = None):
        if self.partner == None:
            self.partner = pair_cells(self.C, self.Facelist)
        maxval = max(self.data['vertex'].values())
        minval = min(self.data['vertex'].values())
        Persistence_Diagram(self.C, self.partner, maxval, minval, pointsize, save, filepath)

        
    def _create_newV(self):
        newV = {}
        for key, value in self.V.items():
            newV[key] = value[0]
        return newV
            
        
    def _cancel_one_critical_pair(self,saddle,extremum):
        
        if np.array(extremum).shape == ():
            
            
            new_saddles = []
            for elt in self.min_conn[extremum]:
                if elt != saddle:
                    new_saddles.append(elt)
                '''
                ERROR JUST FOR 3D DATASET!!!!!!!!!!!!!!!!!
                not sure where the error is, but 
                
                self.saddle_conn[elt].remove(extremum)
                
                produces the any all error although extremum is a tuple, the following implementation is quite bad compared 
                to just the remove 
                
                Same happens for the (N,) case 
                '''
                for index, sad_list_tup in enumerate(self.saddle_conn[elt]):
                    if np.array(sad_list_tup).shape == ():
                        if sad_list_tup == extremum:
                            self.saddle_conn[elt].pop(index)     
                for index, sad_tuple in enumerate(self.Facelist[elt]):
                    if np.array(sad_tuple[0]).shape == ():
                        if sad_tuple[0] == extremum:
                            self.Facelist[elt].pop(index)            
                
            new_min = []
            for elt in self.saddle_conn[saddle]:
                if np.array(elt).shape == ():
                    if elt != extremum:
                        new_min.append(elt)
                    self.min_conn[elt].remove(saddle)
                    for index, min_tuple in enumerate(self.Facelist[saddle]):
                        if np.array(min_tuple[0]).shape == ():
                            if min_tuple[0] == elt:
                                self.Facelist[saddle].pop(index)     
                # delete connections from saddle to 2-cells
                elif np.array(elt).shape == (self.N,):
                    self.max_conn[elt].remove(saddle)
                    self.Paths[elt].pop(saddle,None)
                    for index, sad_tuple in enumerate(self.Facelist[elt]):
                        if np.array(sad_tuple[0]).shape == (2,):
                            if sad_tuple[0][0] == saddle[0] and sad_tuple[0][1] == saddle[1]:
                                self.Facelist[elt].pop(index)
                    
            # change the V field new V (needs to be done before the paths are changed
            self._change_V_field(extremum, saddle)
            
            # reconnect saddles and minima via cancelled path
            for sad in new_saddles:
                for mini in new_min:
                    self.min_conn[mini].append(sad)
                    self.saddle_conn[sad].append(mini)
                    self._update_paths(extremum, saddle, mini, sad)
                    self.Facelist[sad].append(tuple((mini,self.C[0][mini])))
                    
            
            for sad in new_saddles:
                self.Paths[sad].pop(extremum,None)
                    
            # delete saddle and extremum from the conn lists
            self.min_conn.pop(extremum)
            self.saddle_conn.pop(saddle)
            self.C[0].pop(extremum)
            self.C[1].pop(saddle)
            self.Paths.pop(saddle)
            self.Facelist.pop(saddle)
            
            
                    
        elif np.array(extremum).shape == (self.N,):
            
            new_saddles = []
            for elt in self.max_conn[extremum]:
                if elt != saddle:
                    new_saddles.append(elt)
                '''
                ERROR JUST FOR 3D DATASET!!!!!!!!!!!!!!!!!
                not sure where the error is, but 
                
                self.saddle_conn[elt].remove(extremum)
                
                produces the any all error although extremum is a tuple, the following implementation is quite bad compared 
                to just the remove 
                '''
                for index, sad_list_tup in enumerate(self.saddle_conn[elt]):
                    if np.array(sad_list_tup).shape == (self.N,):
                        if sad_list_tup[0] == extremum[0] and sad_list_tup[1] == extremum[1] and sad_list_tup[2] == extremum[2]:
                            self.saddle_conn[elt].pop(index)
                
            new_max = []
            for elt in self.saddle_conn[saddle]:
                if np.array(elt).shape == (self.N,):
                    if elt != extremum:
                        new_max.append(elt)
                    self.max_conn[elt].remove(saddle)
                    '''
                    !!! same problem as above!!!!!
                    '''
                    for index, sad_tuple in enumerate(self.Facelist[elt]):
                        if np.array(sad_tuple[0]).shape == (2,):
                            if sad_tuple[0][0] == saddle[0] and sad_tuple[0][1] == saddle[1]:
                                self.Facelist[elt].pop(index)
                # delete connections from saddle to 0-cells
                elif np.array(elt).shape == ():
                    self.min_conn[elt].remove(saddle)
                    
            # change the V field new V (needs to be done before the paths are changed
            self._change_V_field(extremum, saddle)
            
            # reconnect saddles and minima via cancelled path
            for sad in new_saddles:
                for maxi in new_max:
                    self.max_conn[maxi].append(sad)
                    self.saddle_conn[sad].append(maxi)
                    self._update_paths(extremum, saddle, maxi, sad)
                    self.Facelist[maxi].append(tuple((sad,self.C[1][sad])))
                    
            for maxi in new_max:
                self.Paths[maxi].pop(saddle)
                
                    
            # delete saddle and extremum from the conn lists
            self.max_conn.pop(extremum)
            self.saddle_conn.pop(saddle)
            self.C[2].pop(extremum)
            self.C[1].pop(saddle)
            self.Paths.pop(extremum)
            self.Paths.pop(saddle)
            self.Facelist.pop(extremum)
            self.Facelist.pop(saddle)
            
            
    def _update_paths(self, extremum, saddle, new_extr, new_sad):
        if np.array(extremum).shape == (self.N,):
            path_to_saddle = self.Paths[new_extr][saddle]
            path_to_reverse = self.Paths[extremum][saddle]
            path_to_extremum = self.Paths[extremum][new_sad]
            
            combined_path = path_to_saddle + path_to_reverse[::-1][1:-1] + path_to_extremum
            
            self.Paths[new_extr][new_sad] = combined_path
            
            
            
        elif np.array(extremum).shape == ():
            path_to_extremum = self.Paths[new_sad][extremum]
            path_to_reverse = self.Paths[saddle][extremum]
            path_to_saddle = self.Paths[saddle][new_extr]
            
            combined_path = path_to_extremum + path_to_reverse[::-1][1:-1] + path_to_saddle
            
            self.Paths[new_sad][new_extr] = combined_path
            
            
    def _change_V_field(self, extremum, saddle):
        if np.array(extremum).shape == (self.N,):
            path = self.Paths[extremum][saddle][::-1]
            for position, cell in enumerate(self.Paths[extremum][saddle][::-1]):
                if np.array(cell).shape == (2,):
                    self.newV[cell] = path[position+1]
                    
                    '''
                    maybe needs to be changed: issue if path splits  might occur, 
                    as the order is not necessarily right in that case
                    '''
            
        elif np.array(extremum).shape == ():
            path = self.Paths[saddle][extremum][::-1]
            for position, cell in enumerate(self.Paths[saddle][extremum][::-1]):
                if np.array(cell).shape == ():
                    self.newV[cell] = path[position+1]
                
            
            
    def _get_highest_value(self,cell):
        if np.array(cell).shape == (self.N,) or np.array(cell).shape == (2,):
            return max(self.data['star'][cell[0]][cell])
        else:
            return self.data['vertex'][cell]
            
    def _get_closest_extremum(self,saddle):
        conns = self.saddle_conn[saddle]
        
        conn_count = Counter(conns)
        dist=[]
        
        for conn, nb in conn_count.items():
            if nb == 1:
                dist.append(tuple((conn,abs(self._get_highest_value(conn)-self._get_highest_value(saddle)))))
        if sorted(dist, key=lambda item: item[1]):
            closest, dist = sorted(dist, key=lambda item: item[1])[0] 
            return closest, dist
        else: 
            return None
        
