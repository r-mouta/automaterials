# coding: utf-8

"""
This module provides classes and functions used to store and convert between 
quantities relevant to EIS. 
"""

import numpy as np
import pandas as pd

from automaterials.utils.constants import I, PI
from automaterials.utils.constants import VACUUM_PERMITTIVITY_SI as E0

from typing import Optional, Union, List

__author__ = "Rodolpho Mouta"
__maintainer__ = "Rodolpho Mouta"
__email__ = "mouta.rodolpho@gmail.com"

def f_array(start: Union[float, int] = 1.0,
            stop: Union[float, int] = 1.0e6,
            pts_per_decade: int = 30) -> np.ndarray:
    decades = np.log10(stop) - np.log10(start)
    num_of_pts = int(decades * pts_per_decade) + 1
    return np.geomspace(start, stop, num=num_of_pts)

"""
Constants
"""
F_DEFAULT = f_array()

"""
Conversion factors
"""
TO_METER_FROM = {'m':1, 'cm':0.01, 'mm':0.001}
FROM_METER_TO = {'m':1, 'cm':100, 'mm':1000}
SUPPORTED_LENGTH_UNITS = tuple(TO_METER_FROM.keys())

"""
Conversion functions
"""
def omega(
    f: Union[int, float, List[Union[int, float]], np.ndarray] = F_DEFAULT
) -> Union[float, np.ndarray]:
    """
    Pending
    """
    if isinstance(f, list):
        f = np.array(f)
    w = 2*PI*f
    return w

def f(
    omega: Union[int, float, List[Union[int, float]], np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Pending
    """
    if isinstance(omega, list):
        w = np.array(omega)
    f = w/(2*PI)
    return f

"""
Classes to store data.
"""
class ZData:
    """
    An object to store impedance data and corresponding linear frequencies. 
    """
    def __init__(
        self,
        f: Union[float, int, List[Union[int, float]], np.ndarray],
        z: Union[complex, np.ndarray]
    ):
        """
        Pending
        """
        self.f = np.array(f)
        self.z = np.array(z)
        self.z_real = np.array(z.real)
        self.z_imag = np.array(z.imag)
    
    def as_dict(self, minus_imag: bool = False) -> dict:
        """
        Returns a dict representation of impedance data, with keys f, Z_re, 
        and Z_im.
        """ 
        sign = -1 if minus_imag else 1
        z_im_key = '-Z_im' if minus_imag else 'Z_im'
        return {'f':self.f, 'Z_re':self.z_real, z_im_key:sign*self.z_imag}
    
    def as_dataframe(self, minus_imag: bool = False) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with columns f, Z_re, and Z_im. If this is 
        the last command in a Jupyter or Google Colab notebook, the dataframe 
        will be displayed.  
        """
        df = pd.DataFrame(self.as_dict(minus_imag))
        df
        return df

    @classmethod
    def from_f_zreal_zimag(
        cls,
        f: Union[float, int, List[Union[int, float]], np.ndarray],
        z_real: Union[float, int, List[Union[int, float]], np.ndarray],
        z_imag: Union[float, int, List[Union[int, float]], np.ndarray]
    ) -> "ZData":
        """
        Allows initialization from real and imaginary parts, instead of 
        full (complex) impedance. 
        """
        i = complex(0,1)
        f_array = np.array(f)
        z_real_array = np.array(z_real)
        z_imag_array = np.array(z_imag)
        z_array = z_real_array + i*z_imag_array 
        return cls(f_array,z_array)

    def to_zview(self, filename: str, minus_imag: bool = False) -> None:
        """
        Writes impedance data to a text file formatted as a ZView input file, 
        i.e., with columns f, Z_re, and Z_im spaced by tabs. Recommended 
        extensions: .dat or .txt.
        """
        self.to_csv(filename, sep='\t', header=False, minus_imag=minus_imag)

    def to_csv(self, 
               filename: str, 
               sep: str = ',',
               index: bool = False,
               decimal: str = '.', 
               minus_imag: bool = False,
               **kwargs) -> None:
        """
        Writes impedance data to a comma-separated values (csv) file, with 
        columns f, Z_re, and Z_im. 
        **kwargs: parameters passed through to pd.DataFrame.as_csv().
        """
        df = self.as_dataframe(minus_imag)
        df.to_csv(filename, sep=sep, index=index, decimal=decimal, **kwargs) 
    
    def to_sql(self,
               name: str, 
               con: Union["sqlalchemy.engine.Engine","sqlalchemy.engine.Connection","sqlite3.Connection"],
               schema: Optional[str] = None,
               if_exists: str = 'fail',
               minus_imag: bool = False,
               **kwargs) -> None:
        """
        Writes records stored in a DataFrame with columns f, Z_re, and Z_im 
        to a SQL database.
        """
        df = self.as_dataframe(minus_imag)
        df.to_sql(name, con, schema=schema, if_exists=if_exists, **kwargs)


"""
Conversion classes
"""
class ImpedanceConverter():
    """
    A class to convert impedance into related properties. 
    """
    def __init__(
        self,
        zdata: "ZData",
        form_factor: Union[int, float] = 1.0,
        form_factor_unit: str = 'cm'     
    ):
        """
        Pending
        """
        self.form_factor_unit = form_factor_unit
        self.form_factor = form_factor
        self.f = zdata.f
        f = self.f
        w = omega(f) # angular frequency
        u = I*w*E0
        s = form_factor*TO_METER_FROM[form_factor_unit] # form_factor in m
        z = zdata.z
        self.z = z
        self.y = 1/z
        self.m = u*s*z
        self.c = 1/(I*w*z)
        self.rho = s*z
        self.sigma = 1/(s*z)
        self.epsilon_r = 1/(u*s*z)
        self.loss_tan = -self.epsilon_r.imag/self.epsilon_r.real
        self.output = {'z': self.z, 'impedance': self.z,
                       'y': self.y, 'admittance': self.y,
                       'm': self.m, 'modulus': self.m,
                       'c': self.c, 'capacitance': self.c,
                       'rho': self.rho, 'resistivity': self.rho,
                       'sigma': self.sigma, 'conductivity': self.sigma,
                       'epsilon_r': self.epsilon_r, 'dielectric constant': self.epsilon_r,
                       'loss tangent': self.loss_tan, 'dielectric loss': self.loss_tan}

    def to_property(self, 
                    property: str, 
                    unit_type:str = 'auto',
                    component: Optional[str] = None
    ) -> Union[float, complex, np.ndarray]:
        """
        ...

        unit_type = 'auto' has the same effect as unit = 'SI', except for the
        length unit in resistivities and conductivities, which are output in 
        cm, instead of m. 
        """
        if unit_type not in ('SI', 'auto'):
            print('WARNING: unit_type '+unit_type+' not supported. Switching to auto...')
            unit_type = 'auto'
        output_property = self.output[property.lower()]
        if unit_type == 'auto':
            if output_property == self.rho:
                output_property = output_property*FROM_METER_TO['cm'] # convert Ω•m into Ω•cm
            elif output_property == self.sigma:
                output_property = output_property/FROM_METER_TO['cm'] # convert Ω/m into Ω/cm
        supported_components = ('real', 'imag', 'imaginary', 'magnitude', 'phase', None)  
        if component not in supported_components:
            print('WARNING: component '+component+' not supported. Switching to None...')
            component = None
        elif component is not None and output_property == self.loss_tan:
            print('WARNING: loss tangent does not support components. Switching to None...')
            component = None
        if component is None:
            return output_property
        elif component == 'real':
            return output_property.real
        elif component in ('imag','imaginary'):
            return output_property.imag
        elif component == 'magnitude':
            return output_property.absolute
        elif component == 'phase':
            return output_property.angle(deg=True)
    
    @property
    def form_factor_unit(self) -> str:
        return self._form_factor_unit

    @form_factor_unit.setter
    def form_factor_unit(self, unit: str):
        if unit not in SUPPORTED_LENGTH_UNITS:
            print('WARNING: the unit '+unit+' is currently unavailable. Assuming cm...')
            self._form_factor_unit = 'cm'
        else:
            self._form_factor_unit = unit