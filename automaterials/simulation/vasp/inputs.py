# coding: utf-8

"""
This module provides ...
"""
from typing import Union
import os

from pymatgen.core import Structure
from pymatgen.ext.matproj import MPRester
from pymatgen.io.vasp.sets import MPRelaxSet

from automaterials.utils.constants import MATPROJ_API_KEY

def mp_relax_set(
    structure: Union[str, Structure],
    primitive: bool = False,
    output_dir: str = 'auto',
    make_dir_if_not_present: bool = True,
    user_incar_settings: dict = {},
    potcar_spec: bool = True,
    create_inputs: bool = False,
    only_poscar: bool = False
) -> MPRelaxSet:
    """
    
    """
    if isinstance(structure, str):
        struct_isposcar = structure == 'POSCAR'      
        struct_is_path_to_poscar = structure.endswith('\\POSCAR') or structure.endswith('/POSCAR')
        # The parameter structure is actually a POSCAR file of a path to one
        if struct_isposcar or struct_is_path_to_poscar:
            poscar = structure
            actual_structure = Structure.from_file(poscar, primitive=primitive)
            if output_dir == 'auto':
                output_dir = 'VASP_files'

        # The parameter structure is actually a Materials Project id
        elif structure.startswith('mp-'):
            mp_id = structure
            with MPRester(MATPROJ_API_KEY) as mprester:
                conventional_unit_cell = False if primitive else True
                actual_structure = mprester.get_structure_by_material_id(mp_id, 
                                                                         True,
                                                                         conventional_unit_cell)
            if output_dir == 'auto':
                output_dir = mp_id
        
        # The parameter structure is actually a cif file of a path to one
        elif structure.endswith('.cif'):
            cif = structure
            actual_structure = Structure.from_file(cif, primitive=primitive)
            if output_dir == 'auto':
                cif_path_without_ext = os.path.splitext(cif)[0]
                cif_filename_without_ext = os.path.split(cif_path_without_ext)[1]
                output_dir = cif_filename_without_ext

    # The parameter structure is a Structure object 
    else:
        actual_structure = structure
        if output_dir == 'auto':
            output_dir = 'VASP_files'     
    mp_relax_set = MPRelaxSet(actual_structure, user_incar_settings=user_incar_settings)
    if only_poscar:
        poscar = mp_relax_set.poscar
        if create_inputs:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            poscar.write_file(os.path.join(output_dir,'POSCAR'))
        return poscar
    else:
        if create_inputs:
            mp_relax_set.write_input(output_dir=output_dir, 
                                    make_dir_if_not_present=make_dir_if_not_present,
                                    potcar_spec=potcar_spec)
        return mp_relax_set

def create_vasp_inputs(
    structure: Union[str, Structure],
    primitive: bool = False,
    output_dir: str = 'auto',
    make_dir_if_not_present: bool = True,
    user_incar_settings: dict = {},
    potcar_spec: bool = True,
    run_type: str = 'relax'
) -> None:
    if run_type == 'relax':
        mp_relax_set(structure, primitive, output_dir,
                     make_dir_if_not_present, user_incar_settings,  
                     potcar_spec, True)

def create_poscar(
    structure: Union[str, Structure],
    primitive: bool = False,
    output_dir: str = 'auto',
    make_dir_if_not_present: bool = True,
) -> None:
    mp_relax_set(structure, primitive, output_dir, make_dir_if_not_present,
                 create_inputs = True, only_poscar = True)


    
    
