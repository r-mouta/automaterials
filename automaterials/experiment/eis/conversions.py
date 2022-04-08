# coding: utf-8

"""
This module provides classes and functions to convert between properties, 
as well as some conversion factors.
"""

import numpy as np
from typing import Optional, Union, List
from automaterials.utils.constants import I, PI
from automaterials.utils.constants import VACUUM_PERMITTIVITY_SI as E0
from automaterials.utils.constants import F_DEFAULT

__author__ = "Rodolpho Mouta"
__maintainer__ = "Rodolpho Mouta"
__email__ = "mouta.rodolpho@gmail.com"

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


    


