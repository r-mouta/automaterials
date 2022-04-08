# coding: utf-8

import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod
from typing import List, Optional, Union

from automaterials.experiment.eis.circuits import Resistor, Capacitor, CPE, Inductor
from automaterials.experiment.eis.circuits import Circuit

class ZViewResistor(Resistor):
    """
    A Resistor subclass to represent resistors used in equivalent circuit 
    models in ZView.
    """
    def __init__(self, R: float, label: str, R_isfixed: bool = False):
        """
        Pending
        """
        super().__init__(R = R, label = label)
        self.R_isfixed = R_isfixed


class ZViewCapacitor(Capacitor):
    """
    A Capacitor subclass to represent capacitors used in equivalent circuit 
    models in ZView.
    """
    def __init__(self,label: str, C: float, C_isfixed: bool = False):
        """
        Pending
        """
        super().__init__(C = C, label = label)
        self.C_isfixed = C_isfixed


class ZViewCPE(CPE):
    """
    An alternative but identical class to represent a constant phase element
    (CPE) used in equivalent circuit models in ZView. The duplicity accounts 
    for the existence of both naming conventions in the literature. Which one
    to choose is just a matter of personal preference.
    """
    def __init__(
        self,
        label: str,
        T: float, 
        p: float = 1.0, 
        T_isfixed: bool = False,
        p_isfixed: bool = True):
        """
        Pending
        """        
        super().__init__(T = T, p = p, label = label)
        self.T_isfixed = T_isfixed
        self.p_isfixed = p_isfixed


class ZViewQ(ZViewCPE):
    """
    A CPE subclass to represent constant phase elements (CPEs) used in 
    equivalent circuit models in ZView.
    """
    def __init__(
        self,
        label: str,
        T: float, 
        p: float = 1.0, 
        T_isfixed: bool = False,
        p_isfixed: bool = True):
        """
        Pending
        """        
        super().__init__(T = T,
                         p = p, 
                         T_isfixed=T_isfixed,
                         p_isfixed=p_isfixed, 
                         label = label)


class ZViewInductor(Inductor):
    """
    An Inductor subclass to represent inductors used in equivalent circuit 
    models in ZView.
    """
    def __init__(self, L: float, label: str, L_isfixed: bool = False):
        """
        Pending
        """
        super().__init__(L = L, label = label)
        self.L_isfixed = L_isfixed


# class ZViewCircuit(Circuit, metaclass=ABCMeta):
#     """
#     Circuit subclass representing equivalent circuits used to model impedance
#     response in ZView. This serves as an abstract base class for 
#     ZViewSeriesCircuit and ZViewParallelCircuit. Not meant to be instantiated
#     directly.
#     """
#     def __init__(self):
#         self.piece1 = None
#         self.piece2 = None

#     def __sub__(
#         self,
#         other: Union["ElectricalElement", "ZViewCircuit"]
#     ) -> "ZViewSeriesCircuit":
#         """
#         Pending
#         """
#         return ZViewSeriesCircuit(self, other)
    
#     def __floordiv__(
#         self, 
#         other: Union["ElectricalElement", "ZViewCircuit"]
#     ) -> "ZViewParallelCircuit":
#         """
#         Pending
#         """
#         return ZViewParallelCircuit(self, other)
    
#     @abstractmethod
#     def z(self, f) -> complex:
#         """
#         Returns the impedance.
#         """

#     @property
#     def is_parallel_circuit(self) -> bool:
#         return isinstance(self, ZViewParallelCircuit)
    
#     @property
#     def is_series_circuit(self) -> bool:
#         return isinstance(self, ZViewSeriesCircuit)

class MdlReader:
    def __init__(self, filename):
        self.filename = filename
    
    @property
    def mdllines(self):
        with open(self.filename) as file:
            mdllines = file.readlines()
        return mdllines
    
    @property
    def circ_mdl_begin_idx(self):   
        row_where_circ_begins = [row for row in self.mdllines if "Begin Circuit Model:" in row][0] #improve strategy
        index_where_circ_begins = self.mdllines.index(row_where_circ_begins)
        return index_where_circ_begins
    
    @property
    def element_id_map_ungrouped(self):
        element_id_map_ungrouped = {'id':[],
                                    'row_idx':[]}
        for row_idx, row in enumerate(self.mdllines):
            key = row.split(":")[0]
            if 'Type' in key:
                id_ = row.split(":")[1].strip()
                element_id_map_ungrouped['id'].append(id_)
                element_id_map_ungrouped['row_idx'].append(row_idx)
        return element_id_map_ungrouped

    def zview_element_from_mdl(self, id_, row_idx):
        isfixed = {'0':False, '1':True, '2':True}
        label = self.mdllines[row_idx + 1].split(":")[1].strip()
        R_C_T_or_L_string = self.mdllines[row_idx + 3].split(":")[1]
        R_C_T_or_L = float(R_C_T_or_L_string.strip().replace(',','.'))
        R_C_T_or_L_isfixed_key = self.mdllines[row_idx + 4].split(":")[1].strip()
        R_C_T_or_L_isfixed = isfixed[R_C_T_or_L_isfixed_key]
        if id_ == '1':
            R = R_C_T_or_L
            R_label = label
            R_isfixed = R_C_T_or_L_isfixed
            return ZViewResistor(R, R_label, R_isfixed)
        elif id_ == '2':
            C = R_C_T_or_L
            C_label = label
            C_isfixed = R_C_T_or_L_isfixed
            return ZViewCapacitor(C, C_label, C_isfixed)
        elif id_ == '3':
            L = R_C_T_or_L
            L_label = label
            L_isfixed = R_C_T_or_L_isfixed
            return ZViewInductor(L, L_label, L_isfixed)
        elif id_ == '11':
            Q_label = label
            T = R_C_T_or_L
            p = float(self.mdllines[row_idx + 6].split(":")[1].strip().replace(',','.'))
            T_isfixed = R_C_T_or_L_isfixed
            p_isfixed_key = self.mdllines[row_idx + 7].split(":")[1].strip()
            p_isfixed = isfixed[p_isfixed_key]
            return ZViewCPE(Q_label, T, p, T_isfixed, p_isfixed)
    
    @property
    def elements_grouped(self):
        elements_grouped = []
        is_parallel_subcircuit_open = False
        map_ = zip(self.element_id_map_ungrouped['id'], 
                   self.element_id_map_ungrouped['row_idx'])
        for id_,row_idx in map_:
            if id_ == '-1': # Begin_Parallel
                is_parallel_subcircuit_open = True
                element_group = []
            elif id_ == '-2': # End_Parallel 
                is_parallel_subcircuit_open = False
                elements_grouped.append(element_group)
            elif id_ in ('1', '2', '3', '11'):
                element = self.zview_element_from_mdl(id_, row_idx)
                if is_parallel_subcircuit_open:
                    element_group.append(element)
                else:
                    elements_grouped.append([element])
                    
        return elements_grouped
     

class ZViewCircuit:
    def __init__(self, filename):
        self.filename = filename
    
    @property
    def circuit(self):
        mdl = MdlReader(self.filename)
        elements_grouped = mdl.elements_grouped
        for group_idx, group in enumerate(elements_grouped):
            first_element = group[0]
            subcircuit = first_element
            if len(group) > 1:
                other_elements = group[1:] 
                for element in other_elements:
                    subcircuit = subcircuit//element # parallel association
            if group_idx == 0:
                circuit = subcircuit
            else:
                circuit = circuit - subcircuit # series association
        return circuit

                



        

