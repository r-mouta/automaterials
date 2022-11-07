# coding: utf-8

import numpy as np
import pandas as pd

from automaterials.experiment.eis.properties import ZData, omega
from automaterials.utils.constants import I

from typing import List, Optional

__author__ = "Rodolpho Mouta"
__maintainer__ = "Rodolpho Mouta"
__email__ = "mouta.rodolpho@gmail.com"

class SmartFileReader:
    """
    A class for reading Smart output files (usually in in .csv or .dat format).
    """ 
    def __init__(self, filename:str):
        self.filename = filename
        self.bootstrap()

    def without_extension(self, filename) -> str:
        ext_begin_index = filename.rfind('.')
        if ext_begin_index == -1:
            filename_wo_extension = self.filename 
        else:
            filename_wo_extension = self.filename[:ext_begin_index]
        return filename_wo_extension
    
    def extension(self, filename) -> str:
        total_length = len(filename)
        partial_length = len(self.without_extension(filename))
        extension = filename[partial_length - total_length + 1:]
        return extension

    def bootstrap(self) -> None:
        """
        Identifies the header row and fixes separator issues.
        """
        with open(self.filename) as file:
            lines = file.readlines()
        overwrite_file = False
        for row_idx,row in enumerate(lines):
            if any([label in row for label in ('Set Ac Level', 'DC Level (V)')]):
                self.header_row_idx = row_idx
        if '.' in lines[self.header_row_idx]:
            lines[self.header_row_idx] = lines[self.header_row_idx].replace('.',';')
        if ';' in lines[self.header_row_idx + 1]:
            lines[self.header_row_idx] = lines[self.header_row_idx].replace(',',';')
            overwrite_file = True
        if overwrite_file:
            with open(self.filename,'w') as file:
                file.writelines(lines)
            with open(self.filename,'r+') as file:
                filecontent = file.read()
            filecontent = filecontent.replace(',','.')
            filecontent = filecontent.replace(';',',')
            with open(self.filename,'w') as file:
                file.write(filecontent)
    
    def to_dataframe(self) -> pd.DataFrame:
        df = pd.read_csv(self.filename, sep=',', index_col=False, 
                         skiprows=self.header_row_idx)                  
        return df
    
    def get_zdata(self, dataframe) -> ZData:
        df = dataframe
        zreal_labels = ['Impedance Real (Ohms)', 'Z Real']
        zimag_labels = ['Impedance Imaginary (Ohms)', 'Z Imag']
        zabs_labels = ['Impedance Magnitude (Ohms)']
        z_phase_deg_labels = ["Impedance Phase Degrees (')"]
        creal_labels = ['Capacitance Real (F)']
        cimag_labels = ['Capacitance Imaginary (F)']
        f_labels = ['Frequency (Hz)', 'Frequency']
        zreal_label = None
        zimag_label = None
        zabs_label = None
        z_phase_deg_label = None
        creal_label = None
        cimag_label = None
        f_label = None
        for label in zreal_labels:
            if label in df.columns:
                zreal_label = label
        for label in zimag_labels:
            if label in df.columns:
                zimag_label = label 
        for label in zabs_labels:
            if label in df.columns:
                zabs_label = label
        for label in z_phase_deg_labels:
            if label in df.columns:
                z_phase_deg_label = label
        for label in creal_labels:
            if label in df.columns:
                creal_label = label
        for label in cimag_labels:
            if label in df.columns:
                cimag_label = label
        for label in f_labels:
            if label in df.columns:
                f_label = label
        f = df[f_label].values
        if zreal_label and zimag_label:
            z_real = df[zreal_label].values
            z_imag = df[zimag_label].values
        elif creal_label and cimag_label:
            c_real = df[creal_label].values
            c_imag = df[cimag_label].values
            w = omega(f)
            c = c_real - I*c_imag
            z = 1/(I*w*c)
            z_real = z.real
            z_imag = z.imag
        else:             
            z_abs = df[zabs_label].values
            z_phase_deg = df[z_phase_deg_label].values
            z_phase_rad = np.deg2rad(z_phase_deg)
            z_real = z_abs*np.cos(z_phase_rad)
            z_imag = z_abs*np.sin(z_phase_rad)
        return ZData.from_f_zreal_zimag(f, z_real, z_imag)
    
    def to_zview(
        self, 
        minus_imag: bool = False,
        filename: Optional[str] = None 
    ) -> None:
        """
        Writes impedance data to a text file formatted as a ZView input file, 
        i.e., with columns f, Z_re, and Z_im spaced by tabs. Valid output 
        extensions: .dat or .txt. If filename is not provided, it is assumed 
        to be the same as self.filename, but the extension (if present) is 
        changed, so that the original file is not replaced. This is, if 
        self.filename already has an extension that is not .txt, the output 
        file extension is going to be .txt; if the extension of self.filename
        is .txt, the output file extension will be .dat; if self.filename has
        no extension, the output file name will be the same as self.filename, 
        but with .txt appended.
        """
        if filename:
            if self.extension(filename) not in ('txt', 'dat'):
                extension = 'txt'
            else:
                extension = self.extension(filename)
        else:
            filename = self.filename
            if self.extension(self.filename) == 'txt':
                extension = 'dat'
            else:
                extension = 'txt'
        filename_wo_extension = self.without_extension(filename)
        temperature_labels = ["Set Point ('C)", "Set Point (K)", "Set Temperature"]
        temperature_label = None
        df = self.to_dataframe()
        for label in temperature_labels:
            if label in df.columns:
                temperature_label = label
        if df[temperature_label].dtypes in ('int64', 'float64'):
            temperature_data_exists = True
        else:
            temperature_data_exists = False
        if 'Sweep Number' in df.columns:
            sweeps = df['Sweep Number'].iat[-1]
        else:
            sweeps = 1
        if sweeps > 1:
            for sweep in range(1,sweeps+1):
                df_slice = df.loc[(df['Sweep Number'] == sweep)]
                zdata = self.get_zdata(df_slice)
                if temperature_data_exists:
                    temperature = df_slice[temperature_label].iat[-1]
                    index = temperature
                else:
                    sweep = df_slice['Sweep Number'].iat[-1] 
                    index = sweep
                output_filename = f'{filename_wo_extension}_[{index}].{extension}'
                zdata.to_zview(output_filename, minus_imag)
        else:
            zdata = self.get_zdata(df)
            output_filename = f'{filename_wo_extension}.{extension}'
            zdata.to_zview(output_filename, minus_imag)
