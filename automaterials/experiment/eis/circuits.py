# coding: utf-8

"""
This module provides classes used to define electrical elements and circuits.
"""

import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod
from typing import Dict, List, Optional, Union

from automaterials.experiment.eis.properties import ZData, omega, f, F_DEFAULT

__author__ = "Rodolpho Mouta"
__maintainer__ = "Rodolpho Mouta"
__email__ = "mouta.rodolpho@gmail.com"

class ElectricalElement(metaclass = ABCMeta):
    """
    Generic electrical element. This serves as an abstract base class for 
    Resistor, Capacitor, CPE, and Inductor. Not meant to be instantiated 
    directly. 
    """
    def __init__(
        self,
        R: Optional[float] = None,
        C: Optional[float] = None,
        L: Optional[float] = None,
        T: Optional[float] = None, 
        p: Optional[float] = None,
        label: Optional[float] = None
    ):
        """
        Pending
        """
        self.R = R
        self.C = C
        self.L = L
        self.T = T
        self.p = p
        self.parameters = {'R':self.R, 
                           'C':self.C, 
                           'L':self.L,
                           'T':self.T,
                           'p':self.p}
        self.label = label
        

    def __sub__(self, other: Union["ElectricalElement", "Circuit"]) -> "SeriesCircuit":
        """
        Pending
        """
        if other.is_series_circuit:
            pieces = [self, *other.pieces]
            return SeriesCircuit(*pieces)
        else:
            return SeriesCircuit(self, other)
    
    def __floordiv__(self, other: Union["ElectricalElement", "Circuit"]) -> "ParallelCircuit":
        """
        Pending
        """
        if self.is_resistor and other.is_cpe:
            return RQ(resistor=self, cpe=other)
        elif self.is_cpe and other.is_resistor:
            return RQ(resistor=other, cpe=self)
        elif self.is_resistor and other.is_capacitor:
            return RC(resistor=self, capacitor=other)
        elif self.is_capacitor and other.is_resistor:
            return RC(resistor=other, capacitor=self)
        elif other.is_parallel_circuit:
            pieces = [self, *other.pieces]
            return ParallelCircuit(*pieces)
        else:
            return ParallelCircuit(self, other)

    def __eq__(self, other: Union["ElectricalElement", "Circuit"]) -> bool:
        if isinstance(other, ElectricalElement):
            return self.parameters == other.parameters
        else:
            return False

    def __ne__(self, other: Union["ElectricalElement", "Circuit"]) -> bool:
        return not self.__eq__(other)

    @abstractmethod
    def z(self, f):
        """
        Returns the impedance.
        """

    def zdata_as_dict(
        self,
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
        minus_imag: bool = False
    ) -> dict:
        """
        Returns a dict representation of impedance data, with keys f, Z_re, and Z_im.
        """
        z = self.z(f)
        zdata = ZData(f, z)
        zdata_dict = zdata.as_dict(minus_imag)
        return zdata_dict
    
    def zdata_as_dataframe(
        self,
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
        minus_imag: bool = False
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with columns f, Z_re, and Z_im. If this is 
        the last command in a Jupyter or Google Colab notebook cell, the 
        dataframe will be displayed.  
        """
        z = self.z(f)
        zdata = ZData(f, z)
        zdata_df = zdata.as_dataframe(minus_imag)
        return zdata_df

    def zdata_to_zview(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
        filename: str = 'zdata_output.txt',
        minus_imag: bool = False
    ) -> None:
        """
        Writes impedance data to a text file formatted as a ZView input file, 
        i.e., with columns f, Z_re, and Z_im spaced by tabs. Recommended 
        extensions: .dat or .txt.
        """
        z = self.z(f)
        zdata = ZData(f, z)
        zdata.to_zview(filename, minus_imag)
    
    def zdata_to_csv(
        self,
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
        filename: str = 'zdata_output.csv', 
        sep: str = ',',
        decimal: str = '.', 
        minus_imag: bool = False,
        **kwargs
    ) -> None:
        """
        Writes impedance data to a comma-separated values (csv) file, with 
        columns f, Z_re, and Z_im. 
        **kwargs: parameters passed through to pd.DataFrame.as_csv().
        """
        z = self.z(f)
        zdata = ZData(f, z)
        zdata.to_csv(filename = filename, 
                     sep = sep, 
                     decimal = decimal, 
                     minus_imag = minus_imag, 
                     **kwargs)                       

    @property
    def is_resistor(self) -> bool:
        return isinstance(self, Resistor)
    
    @property
    def is_r(self) -> bool:
        return self.is_resistor
    
    @property
    def is_capacitor(self) -> bool:
        return isinstance(self, Capacitor)
    
    @property
    def is_c(self) -> bool:
        return self.is_capacitor

    @property
    def is_cpe(self) -> bool:
        return isinstance(self, CPE)
    
    @property
    def is_q(self) -> bool:
        return self.is_cpe
    
    @property
    def is_inductor(self) -> bool:
        return isinstance(self, Inductor)
    
    @property
    def is_l(self) -> bool:
        return self.is_inductor

    @property
    def is_parallel_circuit(self) -> bool:
        return False
    
    @property
    def is_series_circuit(self) -> bool:
        return False

    @property
    def is_rc(self) -> bool:
        return False 
    
    @property
    def is_rq(self) -> bool:
        return False


class Resistor(ElectricalElement):
    """
    An ElectricalElement subclass representing a resistor.
    """
    def __init__(self, R: float, label: str = 'R'):
        """
        Pending
        """
        super().__init__(R = R, label = label)

    def z(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
    ) -> Union[complex, np.ndarray]:
        """
        Pending
        """
        z = complex(self.R, 0)
        if isinstance(f, (list, np.ndarray)):
            z = z*np.ones(len(f))
        return z
    
    def as_dict(self) -> Dict[str,float]:
        return {self.label:self.R}


class Capacitor(ElectricalElement):
    """
    An ElectricalElement subclass representing a capacitor.
    """
    def __init__(self, C: float, label: str = 'C'):
        """
        Pending
        """
        super().__init__(C = C, label = label)


    def z(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
    ) -> Union[complex, np.ndarray]:
        """
        Pending
        """
        w = omega(f)
        i = complex(0,1)
        denominator = i*w*self.C
        z = 1/denominator          
        return z
    
    def as_dict(self) -> Dict[str,float]:
        return {self.label:self.C}


class CPE(ElectricalElement):
    """
    An ElectricalElement subclass representing a constant phase element (CPE).
    Identical to the class Q.
    """
    def __init__(self, T: float, p: float, label: str = 'Q'):
        super().__init__(T = T, p = p, label = label)
        """
        Pending
        """

    def z(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
    ) -> Union[complex, np.ndarray]:
        """
        Pending
        """
        w = omega(f)
        i = complex(0,1)
        denominator = self.T*(i*w)**self.p
        z = 1/denominator          
        return z
    
    def as_dict(self) -> Dict[str,Dict[str,float]]:
        return {self.label:{'T':self.T, 'p':self.p}}


class Inductor(ElectricalElement):
    """
    An ElectricalElement subclass representing an inductor.
    """
    def __init__(self, L: float, label: str = 'L'):
        super().__init__(L = L, label = label)
        """
        Pending
        """

    def z(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
    ) -> Union[complex, np.ndarray]:
        """
        Pending
        """
        w = omega(f)
        i = complex(0,1)
        z = i*w*self.L          
        return z
    
    def as_dict(self) -> Dict[str,float]:
        return {self.label:self.L}


class R(Resistor):
    """
    Shorthand for the class Resistor.  
    """
    def __init__(self, R: float, label: str = 'R'):
        super().__init__(R = R, label = label)
        """
        Pending
        """


class C(Capacitor):
    """
    Shorthand for the class Capacitor.  
    """
    def __init__(self, C: float, label: str = 'C'):
        super().__init__(C = C, label = label)
        """
        Pending
        """


class Q(CPE):
    """
    Shorthand for the class CPE  
    """
    def __init__(self, T: float, p: float, label: str = 'Q'):
        super().__init__(T = T, p = p, label = label)
        """
        Pending
        """


class L(Inductor):
    """
    Shorthand for the class Inductor.  
    """
    def __init__(self, L: float, label: str = 'L'):
        super().__init__(L = L, label = label)
        """
        Pending
        """


class Circuit(metaclass=ABCMeta):
    """
    Simple generic circuit, comprised of at least two pieces (each an electrical 
    element or subcircuit) that are in series or in parallel. This serves as an
    abstract base class for SeriesCircuit and ParallelCircuit. Not meant to be 
    instantiated directly.
    """
    def __init__(self):
        self.pieces = None
        self.label = None
        self.association_symbol = None
        

    def __sub__(self, other: Union["ElectricalElement", "Circuit"]) -> "SeriesCircuit":
        """
        Pending
        """
        series_pieces = []
        for piece in [self, other]:
            if piece.is_series_circuit:
                series_pieces.extend(piece.pieces)
            else:
                series_pieces.append(piece)          
        return SeriesCircuit(*series_pieces)
    
    def __floordiv__(self, other: Union["ElectricalElement", "Circuit"]) -> "ParallelCircuit":
        """
        Pending
        """
        parallel_pieces = []
        for piece in [self, other]:
            if piece.is_parallel_circuit and not piece.is_rc and not piece.is_rq:
                parallel_pieces.extend(piece.pieces)
            else:
                parallel_pieces.append(piece)          
        return ParallelCircuit(*parallel_pieces)
    
    def __eq__(self, other: Union["ElectricalElement", "Circuit"]) -> bool:
        if isinstance(other, Circuit) and len(self) == len(other):
            both_are_parallel_circuits = self.is_parallel_circuit and other.is_parallel_circuit
            both_are_series_circuits = self.is_series_circuit and other.is_series_circuit
            if both_are_parallel_circuits or both_are_series_circuits:
                for piece in self:
                    sorted_self = sorted(self.pieces, key = attrgetter())
                    direct_match = self.piece1 == other.piece1 and self.piece2 == other.piece2
                    reverse_match =  self.piece1 == other.piece2 and self.piece2 == other.piece1
                return direct_match or reverse_match
            else:
                return False
        else:
            return False

    def __ne__(self, other: Union["ElectricalElement", "Circuit"]) -> bool:
        return not self.__eq__(other)

    def __iter__(self):
        return self.pieces.__iter__()

    def __getitem__(self, idx):
        return self.pieces[idx]

    def __len__(self):
        return len(self.pieces)

    @property
    def sorted_pieces(self) -> dict:
        disassembled_pieces = {'R':[],'C':[],'Q':[],
                               'L':[],'RC':[],'RQ':[],
                               'RC U RQ':[],'Parallel':[],
                               'Series':[]}
        dp = disassembled_pieces
        pieces = self.pieces
        extended_pieces = pieces
        if self.is_series_circuit:
            for piece in pieces:
                if piece.is_series_circuit:
                    extended_pieces.extend(piece.pieces)
        # sort pieces by class
        for piece in extended_pieces:
            if piece.is_resistor:
                dp['R'].append(piece)
            elif piece.is_cpe:
                dp['Q'].append(piece)
            elif piece.is_capacitor:
                dp['C'].append(piece)
            elif piece.is_inductor:
                dp['L'].append(piece)
            elif piece.is_rq:
                dp['RQ'].append(piece)
                dp['RC U RQ'].append(piece)
            elif piece.is_rc:
                dp['RC'].append(piece)
                dp['RC U RQ'].append(piece)
            elif piece.is_parallel_circuit:
                dp['Parallel'].append(piece)
            elif piece.is_series_circuit:
                dp['Series'].append(piece)
        # sort pieces within same class
        new_pieces = []
        if self.is_series_circuit:
            dp['R'].sort(key=lambda r: r.R)
            dp['Q'].sort(key=lambda l: l.Q)
            dp['C'].sort(key=lambda l: l.C)
            dp['L'].sort(key=lambda l: l.L)
            dp['RQ'].sort(key=lambda rq: rq.relax_freq)
            dp['RC'].sort(key=lambda rc: rc.relax_freq)
            dp['RC U RQ'].sort(key=lambda rc_or_rq: rc_or_rq.relax_freq)           
            #dp['Parallel']. # Continue
        elif self.is_parallel_circuit:
            nothing = True # fix phony line
        return dp

    def sorted(self, inplace=False) -> "Circuit":
        nothing = True # fix phony line
        #pieces = 




    def as_dict(self) -> Dict[str,dict]:
        pieces_keys = []
        pieces_values = []
        for piece in self.pieces:
            piece_key = list(piece.as_dict().keys())[0]
            piece_value = list(piece.as_dict().values())[0]
            pieces_keys.append(piece_key)
            pieces_values.append(piece_value)
        # Check for repeated keys and relabel all of them
        for idx1,key1 in enumerate(pieces_keys):
            repeated_key_indices = [idx1]
            for idx2,key2 in enumerate(pieces_keys):
                if idx1 != idx2 and key1 == key2:
                    repeated_key_indices.append(idx2)
            if len(repeated_key_indices) >= 2:
                for number,index in enumerate(repeated_key_indices):
                    pieces_keys[index] += str(number+1)
        pieces_dict = dict(zip(pieces_keys, pieces_values))
        return {self.label:pieces_dict}

    @abstractmethod
    def z(self, f) -> complex:
        """
        Returns the impedance.
        """

    def zdata_as_dict(
        self,
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
        minus_imag: bool = False
    ) -> dict:
        """
        Returns a dict representation of impedance data, with keys f, Z_re, and Z_im.
        """
        z = self.z(f)
        zdata = ZData(f, z)
        zdata_dict = zdata.as_dict(minus_imag)
        return zdata_dict
    
    def zdata_as_dataframe(
        self,
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
        minus_imag: bool = False
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with columns f, Z_re, and Z_im. If this is 
        the last command in a Jupyter or Google Colab notebook cell, the 
        dataframe will be displayed.  
        """
        z = self.z(f)
        zdata = ZData(f, z)
        zdata_df = zdata.as_dataframe(minus_imag)
        return zdata_df

    def zdata_to_zview(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
        filename: str = 'zdata_output.txt', 
        minus_imag: bool = False
    ) -> None:
        """
        Writes impedance data to a text file formatted as a ZView input file, 
        i.e., with columns f, Z_re, and Z_im spaced by tabs. Recommended 
        extensions: .dat or .txt.
        """
        z = self.z(f)
        zdata = ZData(f, z)
        zdata.to_zview(filename, minus_imag)
    
    def zdata_to_csv(
        self,
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
        filename: str = 'zdata_output.csv', 
        sep: str = ',',
        decimal: str = '.', 
        minus_imag: bool = False,
        **kwargs
    ) -> None:
        """
        Writes impedance data to a comma-separated values (csv) file, with 
        columns f, Z_re, and Z_im. 
        **kwargs: parameters passed through to pd.DataFrame.as_csv().
        """
        z = self.z(f)
        zdata = ZData(f, z)
        zdata.to_csv(filename = filename, 
                     sep = sep, 
                     decimal = decimal, 
                     minus_imag = minus_imag, 
                     **kwargs)
    
    def zdata_to_sql(
        self,
        con: Union["sqlalchemy.engine.Engine","sqlalchemy.engine.Connection","sqlite3.Connection"],
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
        name: str = 'zdata_output',
        schema: Optional[str] = None,
        if_exists: str = 'fail',
        minus_imag: bool = False,
        **kwargs
    ) -> None:
        """
        Writes records stored in a DataFrame with columns f, Z_re, and Z_im to
        a SQL database.
        """
        z = self.z(f)
        zdata = ZData(f, z)
        zdata.to_sql(name, 
                     con, 
                     schema=schema, 
                     if_exists=if_exists, 
                     minus_imag=minus_imag,
                     **kwargs)
    @property
    def label(self) -> str:
        if self.is_rq:
            label = 'RQ'
        elif self.is_rc:
            label = 'RC'
        else:
            labels = []
            for piece in self.pieces:
                piece_label = piece.label
                if isinstance(piece,Circuit) and not piece.is_rc and not piece.is_rq:
                    piece_label = f'({piece_label})'
                labels.append(piece_label)
            label = self.association_symbol.join(labels)
        return label

    @property
    def is_resistor(self) -> bool:
        return False
    
    @property
    def is_r(self) -> bool:
        return False
    
    @property
    def is_capacitor(self) -> bool:
        return False
    
    @property
    def is_c(self) -> bool:
        return False

    @property
    def is_cpe(self) -> bool:
        return False
    
    @property
    def is_q(self) -> bool:
        return False
    
    @property
    def is_inductor(self) -> bool:
        return False
    
    @property
    def is_l(self) -> bool:
        return False

    @property
    def is_parallel_circuit(self) -> bool:
        return isinstance(self, ParallelCircuit)
    
    @property
    def is_series_circuit(self) -> bool:
        return isinstance(self, SeriesCircuit)

    @property
    def is_rc(self) -> bool:
        return isinstance(self, RC) 
    
    @property
    def is_rq(self) -> bool:
        return isinstance(self, RQ)

    @property
    def is_compatible_with_blmlike(self) -> bool:
        series_RC_or_RQ_count = 0
        parallel_RC_or_RQ_count = 0
        for piece in self.pieces:
            if piece.is_RC or piece.is_RQ:
                series_RC_or_RQ_count += 1
            elif piece.is_parallel_circuit:
                parallel_RC_or_RQ_count_partial = 0
                for subpiece in piece.pieces:
                    if subpiece.is_RC or subpiece.is_RQ:
                        parallel_RC_or_RQ_count_partial += 1
                if parallel_RC_or_RQ_count_partial == 2:
                    parallel_RC_or_RQ_count += 1
        if series_RC_or_RQ_count >= 1 and parallel_RC_or_RQ_count == 1:
            return True
        else:
            return False
    


class SeriesCircuit(Circuit):
    """
    Defines a generic circuit comprised by at least two pieces 
    (each an electrical element or subcircuit) in series.
    """
    def __init__(
        self, 
        *pieces: Union["ElectricalElement", "Circuit"]
    ):
        """
        Pending
        """
        self.pieces = pieces
        self.association_symbol = '-'

    def z(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
    ) -> Union[complex, np.ndarray]:
        """
        Pending
        """
        z = np.sum([piece.z(f) for piece in self.pieces], axis=0)
        return z   


class ParallelCircuit(Circuit):
    """
    Defines a generic circuit comprised by at least two pieces 
    (each an electrical element or subcircuit) in parallel.
    """
    def __init__(
        self, 
        *pieces: Union["ElectricalElement", "Circuit"]
    ):
        """
        Pending
        """
        self.pieces = pieces
        self.association_symbol = '//'

    def z(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
    ) -> Union[complex, np.ndarray]:
        """
        Pending
        """
        # 1/z = 1/z1 + 1/z2 + ...
        z_inverse = np.sum([1/piece.z(f) for piece in self.pieces],axis=0)
        z = 1/z_inverse    
        return z


class RC(ParallelCircuit):
    """
    An RC circuit, i.e., a circuit with a resistor and a capacitor in parallel.
    """
    def __init__(self, resistor: Resistor, capacitor: Capacitor):
        """
        Pending
        """
        super().__init__(resistor, capacitor)
        self.res = resistor
        self.cap = capacitor
        self.R = self.res.R
        self.C = self.cap.C
    
    def as_dict(self) -> Dict[str,Dict[str,float]]:
        return {self.label:{'R':self.R, 'C':self.C}}

    @property
    def tau(self):
        return self.R*self.C
    
    @property
    def relax_freq(self, unit: str = 'Hz'):
        relax_omega = 1/self.tau
        relax_f = f(relax_omega)
        if unit == 'rad/s':
            return relax_omega
        elif unit == 'Hz':
            return relax_f


class RQ(RC):
    """
    An RQ circuit, i.e., a circuit with a resistor and a constant phase element
    (CPE) in parallel.
    """
    def __init__(self, resistor: Resistor, cpe: CPE):
        """
        Pending
        """
        super().__init__(resistor, cpe)
        self.res = resistor
        self.cpe = cpe
        self.R = self.res.R
        self.T = self.cpe.T
        self.p = self.cpe.p
        self.C = (self.R*self.T)**(1/self.p)/self.R    

    def as_dict(self) -> Dict[str,Dict[str,float]]:
        return {self.label:{'R':self.R, 
                            'T':self.T, 
                            'p':self.p}}

    
class BrickLayerModelLike(Circuit):
    """
    A circuit with same structure as the Brick Layer Model circuit, but
    that does not necessarily complies with its physical constraints.
    """
    def __init__(self, parallel_piece1: Union[RQ,RC], 
                 parallel_piece2: Union[RQ,RC], series_piece: Union[RQ,RC]):
        self.pieces = [parallel_piece1, parallel_piece2, series_piece]

    def z(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
    ) -> Union[complex, np.ndarray]:
        """
        Pending
        """
        blm_like = self.pieces[0]//self.pieces[1]-self.pieces[2] 
        return blm_like.z(f) 
    
    def sorted(self, inplace: bool=False) -> 'BrickLayerModelLike':
        r1 = parallel_piece1.res
        r2 = parallel_piece2.res
        r3 = series_piece.res
        c_or_q1 = parallel_piece1.cpe if parallel_piece1.cpe else parallel_piece1.cap
        c_or_q2 = parallel_piece2.cpe if parallel_piece2.cpe else parallel_piece2.cap
        c_or_q3 = series_piece.cpe if series_piece.cpe else series_piece.cap
        par_Rs = [r1, r2]
        par_Cs = []
        par_Qs = []
        for c_or_q in [c_or_q1, c_or_q2]:
            if c_or_q.is_q:
               par_Qs.append(c_or_q) 
            else:
               par_Cs.append(c_or_q)
        if len(par_Cs) == 0:
            ser_p = c_or_q3.p if c_or_q3.p else 1.0
            par_Qs.sort(key=lambda q: abs(ser_p - q.p), reverse=True)
            par_Rs.sort(key=lambda r: r.R)
            par_Rs.sort(key=lambda r: abs((r//par_Qs[1]).tau - series_piece.tau),
                        reverse = True)
        elif len(par_Cs) == 1:
            par_Cs_and_Qs = [par_Qs[0], par_Cs[0]] 
            par_Rs.sort(key=lambda r: abs((r//par_Cs[0]).tau - series_piece.tau),
                        reverse = True)  
        else:
            rc_or_rq_permutations = [r1//c_or_q1, r1//c_or_q2, r2//c_or_q1, r2//c_or_q2]
            complement = [r2//c_or_q2, r2//c_or_q1, r1//c_or_q2, r1//c_or_q1]
            ser_tau = series_piece.tau
            par_gb = sorted(rc_or_rq_permutations,
                            key = lambda rc_or_rq: abs(rc_or_rq.tau - ser_tau))
            g = complement[rc_or_rq_permutations.index(par_gb)]
            pieces = sorted([g, par_gb, series_piece], key = lambda rc_or_rq: rc_or_rq.tau)
            par_Cs_and_Qs = [pieces[0].cap, pieces[1].cap]
            par_Rs = [pieces[0].res, pieces[1].res]
        new_pieces = [par_Rs[0]//par_Cs_and_Qs[0],
                      par_Rs[1]//par_Cs_and_Qs[1],
                      series_piece] 
        if inplace:
            self.pieces = new_pieces
        return BrickLayerModelLike(*new_pieces)

          






### implementar o método mágico que permite saber se um elemento ou subcircuito 
### está contido no circuito

### Consertar __eq__ de Circuit

### Fazer RQ//R//Q ser interpretado como RQ//RQ

