import numpy as np
import timeit
from collections import Counter


def BettiViaPairCells(C,Facelist):
    start_eff = timeit.default_timer()
    
    partner = pair_cells(C,Facelist)

    betti = np.zeros(3)
    for p in range(3):
        for key in C[p].keys():
            if np.array(partner[key]).size == 0:
                betti[p] += 1
    
    time_eff = timeit.default_timer() -start_eff
    print('Time Betti numbers:', time_eff)  
    return betti, partner


def pair_cells(M, Facelist):
    
    partner = {}
    cascade = {}
    dell_cascade = {}
    
    for p in range(3):
        M[p] = {k: v for k, v in sorted(M[p].items(), key=lambda item: item[1])}
        
        for sigma in M[p].keys():
            
            partner[sigma] = []
            cascade[sigma] = [sigma]
            dell_cascade[sigma] = Dell()
            dell_cascade[sigma].add(sigma, Facelist)
            
            eliminate_boundaries(sigma, cascade, partner, dell_cascade, Facelist)
            
            if dell_cascade[sigma].nonzero():
                tau = dell_cascade[sigma].youngest()

                partner[tau] = sigma
                partner[sigma] = tau
                
    return partner


class Dell:
    def __init__(self): 
        self.dell = set()
  
    # for checking if the dell is empty 
    def nonzero(self): 
        return len(self.dell) != 0
  
    # for adding an element to dell 
    def add(self, sigma, Facelist): 
        if (np.array(sigma).size == 1 and isinstance(sigma,int)):
            return
        else:
            for elt in Facelist[sigma]:
                if elt in self.dell:
                    self.dell.remove(elt)
                else:
                    self.dell.add(tuple((elt)))
            return self.dell
        
    def copy(self, dell_list):
        for elt in dell_list:
            if elt in self.dell:
                self.dell.remove(elt)
            else:
                self.dell.add(tuple((elt)))
        return self.dell
    
    def youngest(self):
        return sorted(self.dell, key=lambda item: item[1])[-1][0]


def eliminate_boundaries(sigma, cascade, partner, dell_cascade, Facelist):
    while dell_cascade[sigma].nonzero():
        tau = dell_cascade[sigma].youngest()
        
        if not partner[tau]:
            return
        else:
            cascade[sigma] += cascade[partner[tau]]
            
            dell_cascade[sigma].copy(dell_cascade[partner[tau]].dell)


