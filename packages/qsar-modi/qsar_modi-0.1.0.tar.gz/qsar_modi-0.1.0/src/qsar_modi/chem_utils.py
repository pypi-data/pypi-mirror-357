"""Chemical utilities for Modi"""

from typing import Literal, Union, overload

import numpy as np
import numpy.typing as npt
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from rdkit.DataStructs import ConvertToNumpyArray
from rdkit.rdBase import BlockLogs


Molable = Union[str, Chem.Mol]


def _get_fp_generator(fp_type: str, use_chirality: bool = False):
    """Get a fingerprint generator function for the specified fingerprint type"""
    match fp_type:
        case "bFCFP4":
            return rdFingerprintGenerator.GetMorganGenerator(
                radius=2,
                fpSize=2048,
                includeChirality=use_chirality,
                atomInvariantsGenerator=rdFingerprintGenerator.GetMorganFeatureAtomInvGen(),
            ).GetFingerprints
        case "bFCFP6":
            return rdFingerprintGenerator.GetMorganGenerator(
                radius=3,
                fpSize=2048,
                includeChirality=use_chirality,
                atomInvariantsGenerator=rdFingerprintGenerator.GetMorganFeatureAtomInvGen(),
            ).GetFingerprints
        case "bECFP4":
            return rdFingerprintGenerator.GetMorganGenerator(
                radius=2, fpSize=2048, includeChirality=use_chirality
            ).GetFingerprints
        case "bECFP6":
            return rdFingerprintGenerator.GetMorganGenerator(
                radius=3, fpSize=2048, includeChirality=use_chirality
            ).GetFingerprints
        case "bAtomPair":
            return rdFingerprintGenerator.GetAtomPairGenerator(
                fpSize=2048, includeChirality=use_chirality
            ).GetFingerprints
        case "bTopologicalTorsion":
            return rdFingerprintGenerator.GetTopologicalTorsionGenerator(
                fpSize=2048, includeChirality=use_chirality
            ).GetFingerprints
        case "bRDKit":
            return rdFingerprintGenerator.GetRDKitFPGenerator(
                fpSize=2048, includeChirality=use_chirality
            ).GetFingerprints
        case _:
            raise ValueError(
                f"Unsupported fingerprint type: {fp_type};"
                f"supported types are: 'bFCFP4',  'bFCFP6', 'bECFP4', "
                f"'bECFP6', 'bAtomPair', 'bTopologicalTorsion', "
                f"'bRDKit'. See docs for more details."
            )


@overload
def to_mol(smi: Molable, fail_on_error: Literal[False]) -> Chem.Mol: ...


@overload
def to_mol(smi: Molable, fail_on_error: Literal[True]) -> Chem.Mol | None: ...


def to_mol(smi: Molable, fail_on_error: bool = True) -> Chem.Mol | None:
    """
    Given an object, attempt to convert it to a Chem.Mol object

    Notes
    -----
    Can only covert valid SMILES str and rdkit.Mol objects.
    If a rdkit.Mol object is passed, the same object will be returned.

    Parameters
    ----------
    smi: Any
        object to convert to a Chem.Mol
    fail_on_error: bool
        whether to raise an exception when converting fails.
        if True, will return None when a conversion fails

    Returns
    -------
    Chem.Mol

    Raises
    ------
    ValueError
        if the SMILES cannot be parsed by rdkit
    TypeError
        if the passed object is not a type that can be converted to a Chem.Mol
    """
    _lock = BlockLogs()  # this turns off the rdkit logger
    if isinstance(smi, Chem.Mol):
        return smi
    elif isinstance(smi, str):
        _mol = Chem.MolFromSmiles(smi)
        if _mol is None:
            if fail_on_error:
                raise ValueError(f"SMILES {smi} cannot be parsed by RDKit")
        return _mol
    else:
        if fail_on_error:
            raise TypeError(f"cannot convert type {type(smi)} to type rdkit.Mol")
        else:
            return None


def to_smi(mol: Chem.Mol) -> str:
    """
    Given a Chem.Mol object, convert it to a SMILES

    Notes
    -----
    It is my understanding that the Chem.MolToSmiles function cannot fail
    for sanitized Mols. This function expects all Mols passed are sanitized

    Parameters
    ----------
    mol: Any
        object to convert to a Chem.Mol

    Returns
    -------
    str
    """
    _lock = BlockLogs()  # this turns off the rdkit logger
    return Chem.MolToSmiles(mol)


def mols_to_fps_array(
    mols: list[Chem.Mol], fp_type: str = "bFCFP4", use_chirality: bool = False
) -> npt.NDArray:
    """
    Given a list of Chem.Mol or SMILES strings, convert them to a list of fingerprints

    Parameters
    ----------
    mols: list[Chem.Mol]
        list of Chem.Mol objects
    fp_type: str, default="bFCFP4"
        the type of fingerprint to generate
        options are:
            "bFCFP4", "bFCFP6",
            "bECFP4", "bECFP6", "bAtomPair",
            "bTopologicalTorsion", "bRDKit",
        the 'b' prefix indicates a binary fingerprint
        MODI is only useful with binary fingerprints
    use_chirality: bool, default=False
        whether to include chirality in the fingerprint

    Returns
    -------
    npt.NDArray
        an array of shape (n_chemicals, fp_size) of the fingerprints
    """
    fp_generator = _get_fp_generator(fp_type, use_chirality)

    fps = fp_generator(mols)
    _arrays = []
    for fp in fps:
        _array = np.zeros((0,), dtype=np.int16)
        ConvertToNumpyArray(fp, _array)
        _arrays.append(_array)
    return np.vstack(_arrays)
