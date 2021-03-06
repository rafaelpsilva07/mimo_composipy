import numbers
import numpy as np
from .ply_class import Ply

class Laminate:
    '''
    ===========================================
    The class

    This class creates laminate object. It needs ply objects and the angle information.
    Some formulation characteristics are:
        - Laminate formulations ares used (see References)
        - Main reference is the chapter 4 of reference 2.
    ===========================================

    Use

    Laminate(layup)
    It creates a laminate object, where:
        - layup ==> indicates the stacking sequence of the laminate

    The layup instance is composed of a list containing a tuple to each ply.
    The tuple must contain the ply angle (float in degrees) with relation to the 1 direciton
    and a ply object (of Ply class).
    - [(angle_of_ply_1, ply_1),(angle_of_ply_2, ply_2), ... (angle_of_ply_n, ply_n)]

    Example:
    >>> layup_1 = [(90,ply_1),(90,ply_1),(0,ply_1),(90,ply_1),(90,ply_1),(0,ply_1),(90,ply_1),(90,ply_1)]
    >>> laminate_1 = Laminate(layup_1)
    >>> laminate_1.D # retunrs a array containing bending stiffness matrix [D] of the laminate
    >>> laminate_1.A # retunrs a array containing stiffness matrix [A] of the laminate
    >>> laminate_1.B # retunrs a array containing coupled stiffness matrix [B] of the laminate
    >>> laminate_1.print_ABD() # method that prints ABD matrices of the laminate

    ===========================================

    References:
        1 - JONES, M. Robert. Mechanics of Composite Materials. Taylor & Francis: 2nd ed 1999.
        2 - Analysis and Design of composite structures. Class notes. ITA 2020.
    '''


    def __init__(self,layup):
        
        if not isinstance(layup,list):
            raise ValueError('layup must be a list of tuples.\
 Each tuple must contain a angle value and a Ply object')
        
        for ply in layup:
            if not isinstance(ply[0],numbers.Real):
                raise ValueError(f'the angle must be a real number. Check {ply}')
            if not isinstance(ply[1],Ply):
                print(type(ply[1]))
                raise ValueError(f'the ply mus be a Ply object. Check {ply}')
            
        self.layup = layup
        self._z_position = None
        self._Q_layup = None
        self._A = None
        self._B = None
        self._D = None

#Properties
    @property
    def z_position(self):
        
        total_thickness = 0
        for t in self.layup:
            total_thickness += t[1].thickness
        
        current_z = -total_thickness/2
        ply_position = [current_z]
        for t in self.layup:
            current_z += t[1].thickness
            ply_position.append(current_z)
        
        return ply_position
    
    @property
    def Q_layup(self):    
        if self._Q_layup is None:
            
            self._Q_layup = []
            for theta in self.layup:
                c = np.cos(theta[0]*np.pi/180)
                s = np.sin(theta[0]*np.pi/180)

                T_real = np.array([[c**2,s**2,2*c*s],
                                   [s**2,c**2,-2*c*s],
                                   [-c*s,c*s,c**2-s**2]])

                T_engineering =  np.array([[c**2,s**2,c*s],
                                           [s**2,c**2,-c*s],
                                           [-2*c*s,2*c*s,c**2-s**2]])

                self._Q_layup.append((np.linalg.inv(T_real))@theta[1].Q_0@T_engineering)
        return self._Q_layup
        
    @property
    def A(self):
        if self._A is None:
            self._A = np.zeros(9).reshape(3,3)

            for i in enumerate(self.Q_layup):
                zk1 = self.z_position[i[0]+1]
                zk0 = self.z_position[i[0]]
                self._A += (zk1 - zk0)*i[1]
        return self._A
    
    @property
    def B(self):
        if self._B is None:
            self._B = np.zeros(9).reshape(3,3)

            for i in enumerate(self.Q_layup):
                zk1 = self.z_position[i[0]+1]
                zk0 = self.z_position[i[0]]
                self._B += (1/2)*(zk1**2 - zk0**2)*i[1]
        return self._B
    
    @property
    def D(self):
        if self._D is None:
            self._D = np.zeros(9).reshape(3,3)

            for i in enumerate(self.Q_layup):
                zk1 = self.z_position[i[0]+1]
                zk0 = self.z_position[i[0]]
                self._D += (1/3)*(zk1**3 - zk0**3)*i[1]
        return self._D

#Representation (str not implemented)
    def __repr__(self):
        return(f'Laminate(\n{self.layup})')

#Comparisons
    def __eq__(self, other):
        if isinstance(other, Laminate):
            return (self.layup == other.layup)
        return NotImplemented

#Methods
    def print_ABD(self):
        print("[A] is:")
        print(self.A)
        print("\n")
        print("[B] is:")
        print(self.B)
        print("\n")
        print("[D] is:")
        print(self.D)
        
