##from phase_stability import *

#entries = mp_computed_entries(['Li','Nb','O'])
#pdentries = phase_diagram_entries(entries)
#print(pdentries)
##plot_phase_diagram('Li2O-Nb2O5', open_to=None)

#from automaterials.simulation.vasp.inputs import *
#create_vasp_inputs(r'c:\Users\Rodolpho\Downloads\POSCAR', primitive=False)
from numpy import argsort 

from pymatgen.transformations.standard_transformations import OrderDisorderedStructureTransformation
from pymatgen.core import Structure
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.transformations.advanced_transformations import EnumerateStructureTransformation, CubicSupercellTransformation
from pymatgen.transformations.standard_transformations import PrimitiveCellTransformation

structure = Structure.from_file(r'c:\Users\Rodolpho\Downloads\Mn1-xCoxO2 nanowires - pmg.cif')
sg_analyzer = SpacegroupAnalyzer(structure)
structure = sg_analyzer.get_symmetrized_structure()


eq_sites = structure.equivalent_sites
distinct_sites = [eq_site_group[0] for eq_site_group in eq_sites]
partial_occ_sites = []
for site in distinct_sites:
    occupancies = list(site.species.values())
    if any([occupancy < 1.0 for occupancy in occupancies]):
        partial_occ_sites.append(site)
print(partial_occ_sites)

sites = structure.species_and_occu
min_occupancy = min([min(site.get_el_amt_dict().values()) for site in sites])
print(min_occupancy)
mncoo2 = mncoo2.get_primitive_structure()
sorted_cell_param_indices = argsort(mncoo2.lattice.abc) # find which cell parameters are the smaller ones;
print(sorted_cell_param_indices)                        # now define permutations of supercell multiples

#mncoo2 = super_transf.apply_transformation(mncoo2)
print(mncoo2)
ordering_transf = OrderDisorderedStructureTransformation(symmetrized_structures=False)
print('DONE!')
structures = ordering_transf.apply_transformation(mncoo2, return_ranked_list=100)

print(len(structures))

print(structures[0])