import pymcss as mc

import pandas as pd
from pathlib import Path
from os import mkdir

OUT = Path("TEST/")

# MCMC Parameters:
PDB = "GSTE3.pdb"
TEMP = 0.7
N_ITER = 1

# Rosetta Parameters:
INTERFACE_ANALYZER = "../XML/InterfaceAnalyzerMover.xml"
INTERFACE_ANALYZER_FMT="""# Rosetta Options
-overwrite
"""
MUTATE = "../XML/Mutate_homodimer+InterfaceAnalyzerMover.xml"
MUTATE_FMT = """# Rosetta Options:
-parser
    -script_vars resi={resi:d} new_res={resn:s}
-nstruct 10
-overwrite
"""  

ALLOWED_MUTATIONS={
    51: {
        "A": 1,
        "P": 30,
        "R": 4,
        "S": 1
    },
    52: {
        "E": 1,
        "F": 4,
        "L": 4,
        "M": 3,
        "Q": 23,
        "S": 1
    },
    63: {
        "A": 3,
        "E": 1,
        "F": 13,
        "H": 5,
        "K": 2,
        "L": 2,
        "N": 1,
        "P": 4,
        "S": 1,
        "T": 2,
        "Y": 2
    },
    65: {
        "I": 18,
        "L": 15,
        "V": 2,
        "Y": 1
    },
    66: {
        "A": 2,
        "C": 1,
        "G": 1,
        "H": 1,
        "I": 4,
        "S": 3,
        "T": 1,
        "V": 3,
        "W": 20
    },
    67: {
        "D": 14,
        "E": 21,
        "Q": 1
    },
    69: {
        "H": 14,
        "I": 2,
        "L": 4,
        "R": 11,
        "V": 5
    },
    70: {
        "A": 29,
        "I": 4,
        "S": 2,
        "V": 1
    },
    74: {
        "F": 2,
        "H": 2,
        "Y": 32
    },
    77: {
        "A": 3,
        "D": 6,
        "E": 17,
        "K": 1,
        "N": 1,
        "Q": 1,
        "R": 2,
        "S": 5
    },
    90: {
        "F": 1,
        "H": 2,
        "I": 2,
        "L": 13,
        "P": 15,
        "V": 2,
        "Y": 1
    },
    91: {
        "A": 2,
        "E": 3,
        "F": 1,
        "H": 1,
        "K": 5,
        "L": 11,
        "Q": 8,
        "R": 1,
        "V": 4
    },
    94: {
        "A": 31,
        "I": 1,
        "M": 1,
        "R": 1,
        "S": 2
    },
    98: {
        "A": 2,
        "E": 6,
        "H": 1,
        "I": 4,
        "N": 1,
        "Q": 21,
        "T": 1
    },
    101: {
        "A": 1,
        "D": 1,
        "E": 9,
        "F": 3,
        "H": 10,
        "L": 1,
        "Q": 1,
        "Y": 10
    },
    102: {
        "F": 22,
        "I": 1,
        "L": 2,
        "R": 4,
        "W": 4,
        "Y": 3
    },
    104: {
        "A": 2,
        "C": 4,
        "F": 3,
        "H": 3,
        "L": 4,
        "M": 9,
        "N": 1,
        "Q": 1,
        "S": 7,
        "T": 2
    },
    105: {
        "A": 2,
        "F": 1,
        "G": 20,
        "K": 1,
        "L": 1,
        "M": 1,
        "S": 9,
        "T": 1
    },
    144: {
        "A": 1,
        "C": 1,
        "E": 4,
        "F": 22,
        "I": 1,
        "L": 1,
        "V": 2,
        "W": 3,
        "Y": 1
    }
}

def main():
    mc.log.info("MCSS Initialization")
    if OUT.exists():
        mc.log.warning(f"{OUT} already exists. Will remove the old one.")
        mc.rm(OUT)
    mkdir(OUT)
    
    iter_infos  = []
    iter_scores = []
    pdb_ref = PDB
    
    # Initial Sequence
    seq = mc.get_pdb_sequence(pdb_ref)
    Nres = len(seq) // 2 # input PDB is an homodimer
    seq = seq[:Nres]
    mc.log.debug(f"Using a sequence of {len(seq)} residues")
    motif = "".join([seq[resi - 1] for resi in ALLOWED_MUTATIONS])
    
    # Initial Score
    score = mc.rosetta_scripts(xml=INTERFACE_ANALYZER, pdb_in=pdb_ref, option_str=INTERFACE_ANALYZER_FMT)
    iter_scores.append(score)

    dG = score["dG_separated"]
    mc.log.info(f"Initial dG: {dG:.3f} R.E.U.")

    # Cols: iter_, resi, old, new, dG, ddG, accepted, temp
    iter_infos.append([0, pd.NA, pd.NA, pd.NA, dG, pd.NA, True, TEMP, motif, seq])

    for iter_ in range(1, N_ITER+1):
        mc.log.info(f"Iteration {iter_}/{N_ITER}")

        #1- Sequence Perturbation
        old, resi, new = mc.select_mutation(seq, allowed_mutation=ALLOWED_MUTATIONS)

        #2- Perform Mutation & Scoring
        mutant = OUT / f"mutant_{str(iter_).zfill(4)}.pdb"
        score = mc.rosetta_scripts(
            xml=MUTATE, 
            pdb_in=pdb_ref, 
            option_str=MUTATE_FMT.format(resi = resi, resn = mc.THREE_LETTER_CODE[new]),
            pdb_out= mutant,
            sort_by="dG_separated"
        )
        iter_scores.append(score)

        new_seq = mc.get_pdb_sequence(mutant)[:Nres]
        new_motif = "".join([new_seq[resi - 1] for resi in ALLOWED_MUTATIONS])
        
        new_dG = score["dG_separated"]
        ddG = new_dG - dG
    
        mc.log.info(f"dG: {new_dG:.3f} R.E.U.")
        mc.log.info(f"ddG: {ddG:.3f} R.E.U.")

        #3- Metropolis Criterion:
        accepted = mc.metropolis_criterion(ddG, T = TEMP)
    
        #4- Process Acceptation:
        if accepted:
            dG = new_dG
            pdb_ref = str(mutant)
            seq = new_seq

        # Cols: iter_, resi, old, new, dG, ddG, accepted, temp
        iter_infos.append([iter_, resi, old, new, new_dG, ddG, accepted, TEMP, new_motif, new_seq])

    mc.log.info("End of MCSS loop!")
    iter_infos = pd.DataFrame(iter_infos, columns = ["iter_", "resi", "old", "new", "dG", "ddG", "accepted", "temp", "motif", "sequence"])
    iter_infos = iter_infos.set_index("iter_")
    iter_infos.to_csv(OUT / "MCSS.csv")
    mc.log.info(iter_infos.head())

    iter_scores = pd.DataFrame(iter_scores)
    idx = pd.Index(range(len(iter_scores)), name = "iter_")
    iter_scores.index = idx
    iter_scores.to_csv(OUT / "Rosetta-Scores.csv")
    mc.log.info(iter_scores.head())

if __name__ == '__main__':
    main()
