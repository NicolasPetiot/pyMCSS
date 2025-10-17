
from .log import log
from .params import ONE_LETTER_CODE, THREE_LETTER_CODE, RESIDUE_NAME

from math import exp
from random import uniform, choice, choices, randint

__all__ = [
    "metropolis_criterion",
    "select_mutation",
    "get_pdb_sequence",
]

def metropolis_criterion(delta:float, T=2.5) -> bool:
    """Standard Metropolis Criterion.

    args:
     delta (float): Scoring variation between previous and new iteration.
     T (float): Temperature.

    returns:
     bool: Acceptation boolean.

    caution: 
     If you are working with quantities that have units, T and delta should have the same ones ! 
    """
    log.debug(f"Metropolis criterion: delta={delta:.3f}; T={T:.3f}")

    if delta < 0:
        acceptation_proba = 1.0
        accepted = True
    
    else:
        acceptation_proba = exp(-delta/T)
        accepted = uniform(0, 1) < acceptation_proba
    log.debug(f"Acceptation probability: {acceptation_proba:.6f}")
    log.debug(f"Mutation accepted" if accepted else "Mutation rejected")

    return accepted

def select_mutation(seq:str, allowed_mutation = None, force_change = False) -> tuple[str, int, str]:
    """Randomly select a mutation to apply on an amino acid sequence.

    This function selects a residue position in the sequence and chooses a new amino acid
    to mutate to. Optionally, you can restrict the mutation positions and allowed amino acids,
    and enforce that the new amino acid is different from the original.

    Args:
        seq (str): Amino acid sequence to modify.
        allowed_mutation (list[int] | dict[int, list[str]] | dict[int, dict[str, float]], optional):
            Specifies the allowed mutation sites and/or target amino acids.

            - If a list of integers: mutation is restricted to those residue indices (1-based).
            - If a dict[int, list[str]]: keys are residue indices; values are lists of allowed amino acids.
            - If a dict[int, dict[str, float]]: keys are residue indices; values are dictionaries mapping
              target amino acids to their relative probabilities.

        
        force_change (bool, optional): If True, disallows mutations where the residue
            does not change (e.g., A → A). Defaults to False.

    Returns:
        tuple[str, int, str]: A tuple containing:
            - the original amino acid (str),
            - the 1-based position of the mutation (int),
            - the new amino acid (str).
    """
    log.debug("Mutation Selection")

    # Select Mutation Site:
    if allowed_mutation is None:
        # Choose any residue of the sequence
        Nres = len(seq)
        resi = randint(1, Nres)
        allowed_aa = RESIDUE_NAME.copy()

    elif isinstance(allowed_mutation, list):
        # Choose any residue of the provided mutation site
        resi = choice(allowed_mutation)
        allowed_aa = RESIDUE_NAME.copy() # No allowed residue provided: whole 20 possibilities
        resi = int(resi)

    elif isinstance(allowed_mutation, dict):
        # Choose any residue of the provided mutation site
        resi = choice(list(allowed_mutation.keys()))
        allowed_aa = allowed_mutation[resi] # Only allowed residue from input dict
        resi = int(resi)

    else:
        raise ValueError(f"allowed_mutation cannot be of type {type(allowed_mutation)}. Only support None, list[int], dict[int, list[str]] or dict[int, dict[str, float]]")

    # Select New Residue
    weights = None
    if isinstance(allowed_aa, dict):
        weights    = [float(w) for  w in allowed_aa.values()]
        allowed_aa = [ str(aa) for aa in allowed_aa.keys()]

    old_aa = seq[resi - 1]
    if force_change:
        weights = [w for aa, w in zip(allowed_aa, weights) if aa != old_aa] if weights is not None else None
        allowed_aa = [aa for aa in allowed_aa if aa != old_aa]

    new_aa = choices(allowed_aa, weights)[0] # NOTE: Relative weights are handled by this function!
    log.debug(f"Mutation selected: {old_aa}{resi}{new_aa}")
    return old_aa, resi, new_aa

def get_pdb_sequence(filename, unknown_accepted = False) -> str:
    """
    Returns the sequence of an input PDB from the residue name of the CA atoms found.
    Unknown residue name are marked with a 'X' if unknown_accepted is set to True.
    """
    lines = open(filename, "r").readlines()
    ca    = [line for line in lines if ' CA ' in line]
    resn  = [line[17:20] for line in ca]
    seq   = [ONE_LETTER_CODE[aa] if aa in ONE_LETTER_CODE else 'X' for aa in resn]

    if 'X' in seq and not unknown_accepted:
        unknowns = []
        for aa_one, aa_three in zip(seq, resn):
            if aa_one == 'X':
                unknowns.append(aa_three)
        
        raise ValueError(f"Unknown residue(s): {set(unknowns)}")
    
    return "".join(seq)

