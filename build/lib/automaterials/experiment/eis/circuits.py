# coding: utf-8

"""
This module provides classes used to define electrical elements and circuits.
"""

import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod
from typing import List, Optional, Union

from automaterials.experiment.eis.properties import ZData
from automaterials.experiment.eis.property_conversions import omega, f
from automaterials.utils.constants import F_DEFAULT


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
        self.label = label
        

    def __sub__(self, other: Union["ElectricalElement", "Circuit"]) -> "SeriesCircuit":
        """
        Pending
        """
        return SeriesCircuit(self, other)
    
    def __floordiv__(self, other: Union["ElectricalElement", "Circuit"]) -> "ParallelCircuit":
        """
        Pending
        """
        if self.is_resistor and other.is_capacitor:
            return RC(resistor=self, capacitor=other)
        elif self.is_capacitor and other.is_resistor:
            return RC(resistor=other, capacitor=self)
        elif self.is_resistor and other.is_cpe:
            return RQ(resistor=self, cpe=other)
        elif self.is_cpe and other.is_resistor:
            return RQ(resistor=other, cpe=self)
        else:
            return ParallelCircuit(self, other)

    def __eq__(self, other: Union["ElectricalElement", "Circuit"]) -> bool:
        if isinstance(other, ElectricalElement):
            selfparams = (self.R, self.C, self.L, self.T, self.p)
            otherparams = (other.R, other.C, other.L, other.T, other.p)
            return selfparams == otherparams
        else:
            return NotImplemented

    def __neq__(self, other: Union["ElectricalElement", "Circuit"]) -> bool:
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
    def is_capacitor(self) -> bool:
        return isinstance(self, Capacitor)

    @property
    def is_cpe(self) -> bool:
        return isinstance(self, CPE)
    
    @property
    def is_q(self) -> bool:
        return self.is_cpe
    
    @property
    def is_inductor(self) -> bool:
        return isinstance(self, Inductor)


class Resistor(ElectricalElement):
    """
    An ElectricalElement subclass representing a resistor.
    """
    def __init__(self, R: float, label: Optional[str] = None):
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


class Capacitor(ElectricalElement):
    """
    An ElectricalElement subclass representing a capacitor.
    """
    def __init__(self, C: float, label: Optional[str] = None):
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


class CPE(ElectricalElement):
    """
    An ElectricalElement subclass representing a constant phase element (CPE).
    Identical to the class Q.
    """
    def __init__(self, T: float, p: float, label: Optional[str] = None):
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


class Q(CPE):
    """
    An alternative but identical class to represent a constant phase element
    (CPE). The duplicity accounts for the existence of both naming conventions
    in the literature. Which one to choose is just a matter of personal 
    preference.  
    """
    def __init__(self, T: float, p: float, label: Optional[str] = None):
        super().__init__(T = T, p = p, label = label)
        """
        Pending
        """


class Inductor(ElectricalElement):
    """
    An ElectricalElement subclass representing an inductor.
    """
    def __init__(self, L: float, label: Optional[str] = None):
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


class Circuit(metaclass=ABCMeta):
    """
    Simple generic circuit, comprised of two pieces (each an electrical 
    element or subcircuit) that are in series or in parallel. This serves as an
    abstract base class for SeriesCircuit and ParallelCircuit. Not meant to be 
    instantiated directly.
    """
    def __init__(self):
        self.piece1 = None
        self.piece2 = None

    def __sub__(self, other: Union["ElectricalElement", "Circuit"]) -> "SeriesCircuit":
        """
        Pending
        """
        return SeriesCircuit(self, other)
    
    def __floordiv__(self, other: Union["ElectricalElement", "Circuit"]) -> "ParallelCircuit":
        """
        Pending
        """
        return ParallelCircuit(self, other)
    
    def __eq__(self, other: Union["ElectricalElement", "Circuit"]) -> bool:
        if isinstance(other, Circuit):
            both_are_parallel_circuits = self.is_parallel_circuit and other.is_parallel_circuit
            both_are_series_circuits = self.is_series_circuit and other.is_series_circuit
            if both_are_parallel_circuits or both_are_series_circuits:
                direct_match = self.piece1 == other.piece1 and self.piece2 == other.piece2
                reverse_match =  self.piece1 == other.piece2 and self.piece2 == other.piece1
                return direct_match or reverse_match
            else:
                return False
        else:
            return NotImplemented

    def __neq__(self, other: Union["ElectricalElement", "Circuit"]) -> bool:
        return not self.__eq__(other)

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
    def is_parallel_circuit(self) -> bool:
        return isinstance(self, ParallelCircuit)
    
    @property
    def is_series_circuit(self) -> bool:
        return isinstance(self, SeriesCircuit)


class SeriesCircuit(Circuit):
    """
    Defines a generic circuit comprised by two pieces (each an electrical 
    element or subcircuit) in series.
    """
    def __init__(
        self, 
        piece1: Union["ElectricalElement", "Circuit"],
        piece2: Union["ElectricalElement", "Circuit"] 
    ):
        """
        Pending
        """
        self.piece1 = piece1
        self.piece2 = piece2
    
    def z(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
    ) -> Union[complex, np.ndarray]:
        """
        Pending
        """
        z1 = self.piece1.z(f)
        z2 = self.piece2.z(f)
        z = z1 + z2
        return z   


class ParallelCircuit(Circuit):
    """
    Defines a generic circuit comprised by two pieces (each an electrical 
    element or subcircuit) in parallel.
    """
    def __init__(
        self, 
        piece1: Union["ElectricalElement", "Circuit"],
        piece2: Union["ElectricalElement", "Circuit"] 
    ):
        """
        Pending
        """
        self.piece1 = piece1
        self.piece2 = piece2

    def z(
        self, 
        f: Union[float, int, List[Union[int, float]], np.ndarray] = F_DEFAULT,
    ) -> Union[complex, np.ndarray]:
        """
        Pending
        """
        z1 = self.piece1.z(f)
        z2 = self.piece2.z(f)
        z = z1*z2/(z1 + z2)
        return z

    @property
    def is_RC(self) -> bool:
        return isinstance(self, ParallelCircuit) 


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
    
    @property
    def tau(self):
        R = self.res.R
        C = self.cap.C
        return R*C
    
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
    
    @property
    def C(self):
        R = self.res.R
        T = self.cpe.T
        p = self.cpe.p
        return (R*T)**(1/p)/R

    @property
    def tau(self):
        R = self.res.R
        C = self.C
        return R*C
    

### implementar o método mágico que permite saber se um elemento ou subcircuito 
### está contido no circuito

