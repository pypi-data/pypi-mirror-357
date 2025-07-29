import pickle
import os
import numpy as np
import tensorflow as tf
from pymatgen.core import Structure, Composition, Element, Species
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDEntry
import warnings
from phonopy import Phonopy
# from phonopy.interface.ase import read_ase
from phonopy.structure.atoms import PhonopyAtoms
from pymatgen.io.ase import AseAtomsAdaptor
from matgl import load_model
from matgl.ext.ase import PESCalculator
from ase import Atoms
import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import re

       


class MPAnalyzer:
    """
    Analyze structures against a cached Materials Project dataset (`mp_cache.pkl`) and
    evaluate phonon stability using Phonopy and M3GNet.

    Methods:
        is_structure_unique: Check if structure is unique in cached dataset.
        compute_hull_energy: Compute energy above convex hull (eV/atom).
        compute_phonon_stability: Compute phonon frequencies, detect imaginary modes.
        calculate_forces: Use M3GNet to compute atomic forces.
        analyze_structure: Run full analysis (unique, hull stable, phonon stable).
    """

    def __init__(self, cache_file="mp_cache.pkl"):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        warnings.filterwarnings("ignore", category=UserWarning)

        # Load cached entries from pickle
        with open(cache_file, "rb") as f:
            self.entries = pickle.load(f)

        #self.matcher = StructureMatcher( 
        #    ltol=0.2, stol=0.3, angle_tol=5,
        #    primitive_cell=True, scale=True,
        #    attempt_supercell=False  
        #    )  
                                                        

        # Define PhaseDiagram cache file path
        try:
            base_dir = os.path.dirname(__file__)
        except NameError:
            base_dir = os.getcwd()
        tuka_root = os.path.abspath(os.path.join(base_dir, ".."))
        cache_dir = os.path.join(tuka_root, "TUKAkit", "_pd_cache")
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "pd_cache.pkl")

        # Try to load existing pd_cache
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "rb") as f:
                self.pd_cache = pickle.load(f)
        else:
            self.pd_cache = {}
    

    def is_structure_unique(self, structure) -> bool:
        """
        First filter MP entries by element set, then check structure uniqueness.
        """
        target_formula = structure.composition.reduced_formula
        target_lattice = list(structure.lattice.abc) + list(structure.lattice.angles)
        target_elements = {remove_charge_num(el) for el in structure.composition.elements}

        # Step 1: filter entries based on element set
        filtered_entries = []
        for entry in self.entries:
            db_elements = entry.get("elements", [])
            if set(db_elements) == set(target_elements):
                filtered_entries.append(entry)
        print('filtered_entries',len(filtered_entries))

        if not filtered_entries:
            return True  # No similar elemental system found
        
        num_workers = multiprocessing.cpu_count()
        batch_size = max(1, len(filtered_entries) // num_workers)
        total = len(filtered_entries)
        batches = list(batched(filtered_entries, batch_size=batch_size))
        

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            with tqdm(total=total, desc="Comparing structures", ascii=True) as pbar:
                for batch in batches:
                    futures = [
                        executor.submit(compare_entry, entry, structure, target_formula, target_lattice)
                        for entry in batch
                    ]

                    for future in as_completed(futures):
                        result = future.result()
                        pbar.update(1)
                        if result:
                            for f in futures:
                                f.cancel()
                            return False

        return True


    def _is_structure_unique(self, structure) -> bool:
        
        target_formula = structure.composition.reduced_formula
        target_lattice = list(structure.lattice.abc) + list(structure.lattice.angles)

        batch_size = 512
        total = len(self.entries)
        batches = list(batched(self.entries, batch_size=batch_size))

        num_workers = multiprocessing.cpu_count()

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            with tqdm(total=total, desc="Comparing structures",ascii=True) as pbar:
                for batch in batches:
                    futures = [
                        executor.submit(compare_entry, entry, structure, target_formula, target_lattice)
                        for entry in batch
                    ]

                    for future in as_completed(futures):
                        result = future.result()
                        pbar.update(1)

                        if result:
                            # Cancel all running futures (optional)
                            for f in futures:
                                f.cancel()
                            return False
        return True


    

    def compute_hull_energy(self, structure: Structure, formation_energy_per_atom: float) -> float:

        #elements = sorted({remove_charge_suffix(el) for el in structure.composition.elements})
        #elements,amount = get_sorted_elements_and_amounts(structure.composition)

        comp_ele = sorted({remove_charge_num(el) for el in structure.composition.elements})
        key = tuple(comp_ele)

        if key not in self.pd_cache:
            entries = []

            for entry in self.entries:
                try:
                    db_structure = entry["structure"]
                    db_elements = entry["elements"]
                    if set(db_elements).issubset(comp_ele):
                        form_e = entry["energy_per_atom"]
                        total_energy = form_e * db_structure.composition.num_atoms
                        entries.append(PDEntry(db_structure.composition, total_energy))
                except Exception as e:
                    print(f"[WARN] Failed to include entry in phase diagram: {e}")
                    continue
            
            """
            # Composition can input cluster "Cu2" element only support offical type
            for el_sym, am_sym in zip(elements, amount):
                amt = int(am_sym) 
                entries.append(PDEntry(Composition({Element(el_sym): amt}), 0.0))
            A
            """
            add_elemental_entries(comp_ele,entries)
            pd = PhaseDiagram(entries, elements=[Element(e) for e in comp_ele])
            self.pd_cache[key] = pd

            try:
                with open(self.cache_file, "wb") as f:
                    pickle.dump(self.pd_cache, f)
            except Exception as e:
                print(f"[ERROR] Failed to save pd_cache: {e}")

        pd = self.pd_cache[key]
        total_energy = formation_energy_per_atom * structure.composition.num_atoms

        comp = structure.composition

        comp_neutral = Composition({
            str(el.element if isinstance(el, Species) else el): amt
            for el, amt in comp.items()
        })
        entry = PDEntry(comp_neutral, total_energy)
        try:
            e_above = pd.get_e_above_hull(entry)
        except Exception as e:
            # cal a negative value
            e_above = 0
        return e_above


    def compute_phonon_stability(self,
        structure: Structure,
        supercell_matrix=(2, 2, 2),
        displacement=0.01,
        mesh=[8, 8, 8],
        model_name="M3GNet-MP-2021.2.8-PES"
    ) -> bool:
        """
        Compute phonon spectrum using Phonopy + MatGL PES model and check for imaginary frequencies.

        Args:
            structure: pymatgen Structure object
            supercell_matrix: tuple for supercell size
            displacement: float, atomic displacement in Å
            mesh: list of 3 ints for phonon mesh density
            model_name: pretrained PES model name from MatGL

        Returns:
            True if no imaginary frequencies (stable); False otherwise
        """
        # Convert pymatgen structure to PhonopyAtoms
        ase_atoms = AseAtomsAdaptor.get_atoms(structure)
        phonopy_atoms = PhonopyAtoms(
            symbols=ase_atoms.get_chemical_symbols(),
            cell=ase_atoms.get_cell(),
            positions=ase_atoms.get_positions(),
            masses=ase_atoms.get_masses()
        )

        # Setup Phonopy, generate displacements
        phonon = Phonopy(phonopy_atoms, supercell_matrix=supercell_matrix)
        phonon.generate_displacements(distance=displacement)
        supercells = phonon.get_supercells_with_displacements()
        #supercells = phonon.supercells_with_displacements

        # Load MatGL pretrained PES model and attach as ASE calculator
        pes_model = load_model(model_name)
        calculator = PESCalculator(pes_model)

        # Calculate forces on each displaced supercell
        forces = []
        for idx, sc in enumerate(supercells):
            atoms = Atoms(
                symbols=sc.symbols,
                positions=sc.positions,
                masses=sc.masses,
                cell=sc.cell,
                pbc=True,
                calculator=calculator
            )
            try:
                f = atoms.get_forces()
            except Exception as exc:
                print(f"[ERROR] Force calculation failed for supercell {idx}: {exc}")
                return False
            forces.append(f)

        # Build force constants and sample mesh
        phonon.set_forces(forces)
        phonon.produce_force_constants()
        phonon.run_mesh(mesh, with_eigenvectors=False)

        # Retrieve mesh data as dict and check frequencies
        mesh_data = phonon.get_mesh_dict()
        frequencies = mesh_data["frequencies"]  # shape: (nqpoints, natom*3)

        # Return True only if all frequencies are ≥ 0 (no imaginary modes)
        has_imag = any((freq < 1e-1).any() for freq in frequencies)
        return not has_imag



"""
    def analyze_structure(self, structure: Structure, formation_energy_per_atom: float) -> dict:
      
        unique = self.is_structure_unique(structure)
        e_above = self.compute_hull_energy(structure, formation_energy_per_atom)
        stable = (e_above is not None) and (e_above <= 0.1)
        phonon_stable = self.compute_phonon_stability(structure)
        return {"unique": unique, "stable": stable, "phonon_stable": phonon_stable}
"""

def compare_entry(entry, structure, target_formula, target_lattice):
    try:
        db_structure = entry["structure"]
        # db_formula = db_structure.composition.reduced_formula
        compare_lattice_constants = list(db_structure.lattice.abc) + list(db_structure.lattice.angles)

        
        if len(db_structure) != len(structure):
            return False
        #elif db_formula != target_formula:
        #    return False
        elif not _lattice_similar(target_lattice, compare_lattice_constants):
            return False
        
        matcher = StructureMatcher(
            ltol=0.3, stol=0.5, angle_tol=10,
            primitive_cell=False, scale=False
        )
        return matcher.fit(structure, db_structure)
    except Exception as e:
        print(f"[WARN] Structure comparison failed: {e}")
        return False

def _lattice_similar(lat1, lat2, tol=0.1):
    return all(abs(a - b) / a < tol for a, b in zip(lat1, lat2))


def batched(iterable, batch_size):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]


def remove_charge_suffix(el):
    if isinstance(el, Element):
        el = el.symbol 
    return re.sub(r'[+-]+$', '', str(el))


def remove_charge_num(el):
    if isinstance(el, Element):
        el = el.symbol 
    return re.sub(r'[\d]*[+-]+$', '', str(el))


def get_sorted_elements_and_amounts(composition):
    """
    Given a pymatgen Composition object, returns two lists:
    - Sorted list of element symbols (e.g., ['Ca', 'O'])
    - Corresponding list of amounts as strings (e.g., ['2', '4'])

    Integer amounts are converted to integer strings,
    fractional amounts remain as floats converted to strings.
    """
    elements = []
    amounts = []
    for el, amt in composition.items():
        elements.append(el.symbol)
        if amt.is_integer():
            amounts.append(str(int(amt)))
        else:
            amounts.append(str(amt))
    # Sort both lists by element symbol to keep correspondence
    zipped = sorted(zip(elements, amounts), key=lambda x: x[0])
    sorted_elements, sorted_amounts = zip(*zipped)
    return list(sorted_elements), list(sorted_amounts)



def add_elemental_entries(elements: list[str], entries: list[PDEntry]):
    """
    Add standard elemental entries (0 eV) for the given element symbols.

    Args:
        elements (list[str]): List of element symbols (e.g., ['Ca', 'O', 'H'])
        entries (list[PDEntry]): List to append PDEntry(Composition, 0.0)
    """
    DIATOMIC_ELEMENTS = {"H", "N", "O", "F", "Cl", "Br", "I"}
    added = set()

    for el_sym in sorted(set(elements)):
        if el_sym in added:
            continue  # avoid duplicates
        added.add(el_sym)

        try:

            # Use diatomic form if applicable
            if el_sym in DIATOMIC_ELEMENTS:
                formula = f"{el_sym}2"
            else:
                formula = el_sym

            comp = Composition(formula)
            entries.append(PDEntry(comp, 0.0))
        except Exception as e:
            print(f"[WARN] Failed to add elemental entry for {el_sym}: {e}")


