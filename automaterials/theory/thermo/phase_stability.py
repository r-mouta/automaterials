# coding: utf-8

"""
This module provides ... ???.
"""
from typing import Optional, Union, List
from automaterials.utils.constants import MATPROJ_API_KEY
from pymatgen.entries.computed_entries import ComputedEntry
from pymatgen.analysis.phase_diagram import PDEntry, PhaseDiagram, PDPlotter, CompoundPhaseDiagram
from pymatgen.core.composition import Composition
from pymatgen.ext.matproj import MPRester

__author__ = "Rodolpho Mouta"
__maintainer__ = "Rodolpho Mouta"
__email__ = "mouta.rodolpho@gmail.com"

"""
???
"""
def elements_from_formula(formula: str) -> List[str]:
    composition = Composition(formula)
    composition_dict = composition.get_el_amt_dict()
    elements = list(composition_dict.keys())
    return elements


def mp_computed_entries(criteria: Union[str, List[str], dict]) -> List[ComputedEntry]:
    with MPRester(MATPROJ_API_KEY) as mprester:
        if type(criteria) == list:
            elements = criteria
            entries = mprester.get_entries_in_chemsys(elements)
        #else:
            #chemsys_formula_id_criteria = criteria
            #entries = mprester.get_entries(chemsys_formula_id_criteria)
    return entries

def phase_diagram_entries(entries: List[ComputedEntry]) -> List[PDEntry]:
    pdentries = [PDEntry(entry.composition, entry.energy) for entry in entries]
    return entries

def plot_phase_diagram(
    criteria: Union[str, List[str], dict], 
    open_to: Optional[str] = None,
    temperature_range: tuple = (300,1300),
    voltage_range: tuple = (0,4)
) -> None:
    composition = None
    terminal_compounds = None
    try:
        composition = Composition(criteria)
        elements = elements_from_formula(criteria)  
    except:
        if '-' in criteria:
            elements_or_compounds = criteria.split('-')
            if any([len(el_or_comp) > 2 for el_or_comp in elements_or_compounds]):
                compounds = elements_or_compounds
                elements = []
                for compound in compounds:
                    elements.extend(elements_from_formula(compound))
                terminal_compounds = [Composition(formula) for formula in compounds]
            else:
                elements = elements_or_compounds
    entries = mp_computed_entries(elements)
    pdentries = phase_diagram_entries(entries)
    phase_diagram = PhaseDiagram(pdentries)
    plotter = PDPlotter(phase_diagram)
    if open_to is None:
        contour_pd_plot = plotter.get_contour_pd_plot()
        pd_plot = plotter.get_plot()
        if terminal_compounds is not None:
            compound_phase_diagram = CompoundPhaseDiagram(pdentries, terminal_compounds)
            plotter_compounds = PDPlotter(compound_phase_diagram)
            compound_pd_plot = plotter_compounds.get_plot()
    else:
        if composition is not None:
            profile_element = open_to
            element_profile_plot = plotter.plot_element_profile(profile_element, composition)
    compound_pd_plot.show()
        
       


        


        