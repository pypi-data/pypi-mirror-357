import os
import sys
import argparse
from pymatgen.core import Structure


def read_structures_from_cif(folder_path="./data"):
    """
    Read all CIF files from the given folder and return a list of Structure objects.
    """
    structures = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".cif"):
            file_path = os.path.join(folder_path, file_name)
            try:
                structure = Structure.from_file(file_path)
                structures.append(structure)
            except Exception as e:
                print(f"[WARN] Failed to parse {file_name}: {e}")
    return structures


def main(cache_file,):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from parse import StructureEvaluation

    try:
        base_dir = os.path.dirname(__file__)
    except NameError:
        base_dir = os.getcwd()
    tuka_root = os.path.abspath(os.path.join(base_dir, ".."))
    folder_path = os.path.join(tuka_root, "TUKAkit", "testing","data")

    print(f"Reading structures from '{folder_path}'...")
    structures = read_structures_from_cif(folder_path)

    if not structures:
        print("No valid CIF files found.")
        exit(1)

    print(f"Total structures loaded: {len(structures)}")

    # Initialize evaluator
    tester = StructureEvaluation(cache_file=cache_file)

    # Analyze
    passed_indices, passing_rate = tester.analyze_structures(structures)

    print("\n=== Evaluation Result ===")
    print(f"Passed structure indices: {passed_indices}")
    print(f"Passing rate: {passing_rate * 100:.2f}%")

