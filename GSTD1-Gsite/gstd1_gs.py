import pymcss as mc
from pymcss.rosetta import RestrainedDocking, MutateRestrainedDocking

import pandas as pd
from pathlib import Path
from os import mkdir

OUT = Path("TEST/")

# MCMC Parameters:
PDB = "GSTD1+GSH.pdb"
TEMP = 0.1
N_ITER = 1

# Rosetta Parameters:
DOCKING = RestrainedDocking
DOCKING_FMT="""# Rosetta Options
#the packing options allow Rosetta to sample additional rotamers for
#protein sidechain angles chi 1 (ex1) and chi 2 (ex2) 
#no_optH false tells Rosetta to optimize hydrogen placements
#flip_HNQ tells Rosetta to consider HIS,ASN,GLN hydrogen flips
#ignore_ligand_chi prevents Roseta from adding additional ligand rotamer
-packing
    -ex1
    -ex2
    -no_optH false
    -flip_HNQ true
    -ignore_ligand_chi true

#Ligand docking is not yet benchmarked with the updated scoring function
#This flag restores certain parameters to previously published values
-mistakes
    -restore_pre_talaris_2013_behavior true 

-parser
    -script_vars constraint=GSH-Ser10_constraint.cst
"""

MUTATE = MutateRestrainedDocking
MUTATE_FMT = """# Rosetta Options:
-parser
    -script_vars resi={resi:d} new_res={resn:s}


""" + DOCKING_FMT.copy()

ALLOWED_MUTATIONS = [12, 34, 39, 51, 52, 53, 54, 65, 66, 67, 102]

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

    score = mc.rosetta_scripts(xml=DOCKING, pdb_in=pdb_ref, option_str=DOCKING_FMT)
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
