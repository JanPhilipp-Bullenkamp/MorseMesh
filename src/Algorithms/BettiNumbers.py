##
# @file BettiNumbers.py
#
# @brief Contains the betti_via_pair_cells function described in Zomorodian: “Computational Topology”. 
# In: Algorithms and Theory of Computation Handbook: Special Topics and Techniques.
# (https://doc.lagout.org/science/0_Computer%20Science/2_Algorithms/Algorithms%20and%20Theory%20of%20Computation%20Handbook_%20Special%20Topics%20and%20Techniques%20%282nd%20ed.%29%20%5BAtallah%20%26%20Blanton%202009-11-20%5D.pdf)
#
# @section libraries_BettiNumbers Libraries/Modules
# - numpy standard library
# - collections standard library
#   - need Counter

# imports
import numpy as np
from collections import Counter


def betti_via_pair_cells(MorseComplex):
    """! @brief The wrapper for the PairCells algorithm described by Zomorodian.
    
    @details Calculates Betti numbers by pairing up all critical simplices of the Morse Complex; 
    leaving some unpaired. The unpaired cells give us the betti numbers while the paired cells 
    can be used to obtain a persistence diagram.
    
    @param MorseComplex A Morse Complex class object that we want to calculate the betti numbers from.
    
    @return betti, partner0, partner1, partner2 The betti numbers in a 3 long array, and the paired 
    cells for each dimension in dictionaries.
    """
    partner0, partner1, partner2 = pair_cells(MorseComplex)

    betti = np.zeros(3)
    for cell in MorseComplex.CritVertices.keys():
        if np.array(partner0[cell]).size == 0:
            betti[0] += 1
    for cell in MorseComplex.CritEdges.keys():
        if np.array(partner1[cell]).size == 0:
            betti[1] += 1
    for cell in MorseComplex.CritFaces.keys():
        if np.array(partner2[cell]).size == 0:
            betti[2] += 1
    return betti, partner0, partner1, partner2


def pair_cells(MorseComplex):
    """! @brief The PairCells algorithm described by Zomorodian.
    
    @details Calculates Betti numbers by pairing up all critical simplices of the Morse Complex; 
    leaving some unpaired. The unpaired cells give us the betti numbers while the paired cells 
    can be used to obtain a persistence diagram.
    
    @param MorseComplex A Morse Complex class object that we want to calculate the betti numbers from.
    
    @return partner0, partner1, partner2 The paired cells for each dimension in dictionaries. 
    Can get betti numbers by finding out which cells havent been paired.
    """
    partner0 = {}
    cascade0 = {}
    
    partner1 = {}
    cascade1 = {}
    dell_cascade1 = {}
    
    partner2 = {}
    cascade2 = {}
    dell_cascade2 = {}
    
    M = {}
    M[0] = {k: v for k, v in sorted(MorseComplex.CritVertices.items(), key=lambda item: item[1].fun_val)}
    M[1] = {k: v for k, v in sorted(MorseComplex.CritEdges.items(), key=lambda item: item[1].fun_val)}
    M[2] = {k: v for k, v in sorted(MorseComplex.CritFaces.items(), key=lambda item: item[1].fun_val)}
    
    for sigma in M[0].keys():
        partner0[sigma] = []
        cascade0[sigma] = [sigma]
        
    for sigma in M[1].keys():
        partner1[sigma] = []
        cascade1[sigma] = [sigma]
        dell_cascade1[sigma] = Dell()
        dell_cascade1[sigma].add(M[1][sigma], 1)
        
        eliminate_boundaries(sigma, cascade1, partner1, partner0, dell_cascade1, MorseComplex, 1)
            
        if dell_cascade1[sigma].nonzero():
            tau = dell_cascade1[sigma].youngest(MorseComplex, 1)

            partner0[tau] = sigma
            partner1[sigma] = tau
            
    for sigma in M[2].keys():
        partner2[sigma] = []
        cascade2[sigma] = [sigma]
        dell_cascade2[sigma] = Dell()
        dell_cascade2[sigma].add(M[2][sigma], 2)
        
        eliminate_boundaries(sigma, cascade2, partner2, partner1, dell_cascade2, MorseComplex, 2)
            
        if dell_cascade2[sigma].nonzero():
            tau = dell_cascade2[sigma].youngest(MorseComplex, 2)

            partner1[tau] = sigma
            partner2[sigma] = tau

    return partner0, partner1, partner2


class Dell:
    """! @brief A class to contain and check boundaries"""
    def __init__(self): 
        """! @brief The constructor of a boundary (Dell class) """
        self.dell = set()
  
    # for checking if the dell is empty 
    def nonzero(self): 
        """! @brief Checks if the boundary is empty.
        @return Bool. True if the boundary is not empty, False if it is.
        """
        return len(self.dell) != 0
  
    # for adding an element to dell 
    def add(self, critElt, p):
        """! @brief Adds a critical simplex to the boundary (modulo 2) so it eliminates cycles (removes if 
        it is the second occurance).
        @param critElt The critical simplex we want to add. Should be type CritEdge or CritFace.
        @param p The dimension of the simplex. (Should be 1 or 2 / edge or face)
        """
        if p==1:
            for elt in critElt.connected_minima:
                if elt in self.dell:
                    self.dell.remove(elt)
                else:
                    self.dell.add(elt)
        elif p==2:
            for elt in critElt.connected_saddles:
                if elt in self.dell:
                    self.dell.remove(elt)
                else:
                    self.dell.add(elt)
        
    def copy(self, dell_set):
        """! @brief Copies another set of boundary into this one (modulo 2) so removes if already 
        contained and adds otherwise.
        
        @param dell_set A set of boundary elements, that should be included to this boundary mod 2.
        """
        for elt in dell_set:
            if elt in self.dell:
                self.dell.remove(elt)
            else:
                self.dell.add(elt)
        return self.dell
    
    def youngest(self, MorseComplex, p):
        """! @brief Returns the boundary with the highest function value.
        
        @param MorseComplex The Morse Complex object.
        @param p The dimension of the simplex. (Should be 1 or 2 / edge or face)
        
        return The youngest/ highest valued element of the boundary.
        """
        if p==1:
            return sorted(self.dell, key=lambda item: MorseComplex.CritVertices[item].fun_val)[-1]
        elif p==2:
            return sorted(self.dell, key=lambda item: MorseComplex.CritEdges[item].fun_val)[-1]


def eliminate_boundaries(sigma, cascade, partner, partner_below, dell_cascade, MorseComplex, p):
    """! @brief Function described by Zomorodian to remove boundaries if possible.
    @param sigma \todo Add description
    @param cascade \todo Add description
    @param partner \todo Add description
    @param partner_below \todo Add description
    @param dell_cascade \todo Add description
    @param MorseComplex \todo Add description
    @param p The dimension of the simplex. (Should be 1 or 2 / edge or face)
    """
    while dell_cascade[sigma].nonzero():
        tau = dell_cascade[sigma].youngest(MorseComplex, p)
        
        if not partner_below[tau]:
            return
        else:
            cascade[sigma] += cascade[partner_below[tau]]
            
            dell_cascade[sigma].copy(dell_cascade[partner_below[tau]].dell)


