import os 
import warnings
from typing import List, Tuple
from pymatgen.core import Structure
from tqdm import tqdm
import matgl
from _util import _critera as TUKAcritera
import os


class StructureEvaluation:
    def __init__(self, cache_file: str = "mp_cache.pkl"):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        warnings.filterwarnings("ignore", category=UserWarning)


        self.MPAnalyzer = TUKAcritera.MPAnalyzer(cache_file)
        self.megnet = matgl.load_model("MEGNet-MP-2018.6.1-Eform")
        

    def _evaluate_single(self, args: Tuple[int, Structure]) -> Tuple[int, int]:
        idx, structure = args
        try:
            # Step 1: Predict formation energy
            formation_energy_per_atom = get_energy_per_atom(self.megnet,structure)
    
            if formation_energy_per_atom >= 0.:  
                return idx, -1

            # Step 2: Check stability above convex hull
            elif (e_above := self.MPAnalyzer.compute_hull_energy(structure, formation_energy_per_atom)) is None or e_above > 0.1:
                return idx, -1

            # Step 3: Check phonon stability
            elif not self.MPAnalyzer.compute_phonon_stability(structure):
                return idx, -1

            # Step 4: Check uniqueness
            elif not self.MPAnalyzer.is_structure_unique(structure):
                return idx, -1
            
            return idx, 1

        except Exception as e:
            print(f"[ERROR] Structure {idx} failed evaluation: {e}")
            return idx, -1

    def analyze_structures(self, structures: List[Structure]) -> Tuple[List[int], float]:
        """
        Analyze list of structures and return passing indices and pass rate.

        Args:
            structures (List[Structure]): List of pymatgen Structure objects

        Returns:
            Tuple[List[int], float]: Passing indices and pass rate
        """
        results = []
        for item in tqdm(enumerate(structures), total=len(structures),desc="Analyzing structures"):
            results.append(self._evaluate_single(item))

        passed_indices = [idx for idx, result in results if result == 1]
        pass_rate = len(passed_indices) / len(structures) if structures else 0.0

        return passed_indices, pass_rate


def get_energy_per_atom(model, structure):
    eform = model.predict_structure(structure)
    return float(eform.numpy())



""" 
from pymatgen.io.ase import AseAtomsAdaptor
from m3gnet.models import M3GNet, Potential, M3GNetCalculator
def get_energy_per_atom(structure):
    atoms = AseAtomsAdaptor().get_atoms(structure)
    atoms.calc = M3GNetCalculator(potential = Potential(M3GNet.load()))
    return atoms.get_potential_energy()/len(structure)
"""