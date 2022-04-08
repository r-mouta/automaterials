# coding: utf-8

"""
This module provides classes and functions used to store impedance 
data and convert impedance into related properties.
"""

import numpy as np
import pandas as pd
# from abc import ABCMeta, abstractmethod
from typing import Optional, Union, List

# from automaterials.utils.constants import PI, VACUUM_PERMITTIVITY_SI, omega
# from automaterials.experiment.eis.conversions import TO_METER_FROM, FROM_METER_TO, SUPPORTED_LENGTH_UNITS


__author__ = "Rodolpho Mouta"
__maintainer__ = "Rodolpho Mouta"
__email__ = "mouta.rodolpho@gmail.com"


def f_array(start: Union[float, int] = 1.0,
            stop: Union[float, int] = 1.0e6,
            pts_per_decade: int = 30) -> np.ndarray:
    decades = np.log10(stop) - np.log10(start)
    num_of_pts = int(decades * pts_per_decade) + 1
    return np.geomspace(start, stop, num=num_of_pts)

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