from src import pymcss as mc

# MCMC Parameters:
PDB = "GSTE3-Dimerization_Interface/GSTE3.pdb"
TEMP = 0.7
N_ITER = 1500

INTERFACE_ANALYZER = "XML/InterfaceAnalyzerMover.xml"

MUTATE = "XML/Mutate_homodimer+InterfaceAnalyzerMover.xml"

MUTATE_FMT = """# Rosetta Options:
-parser
    -script_vars resi=%d new_res=%s
-overwrite
"""

def main():
    mc.log.info("Initialization")
    iter_scores = []

    mc.rosetta_script(xml=INTERFACE_ANALYZER, pdb=PDB)
    score = mc.read_rosetta_scores("score.sc")
    dG = score["dG_separated"]

    mc.log.info(f"Initial dG: {dG:.3f}")

    seq = mc.get_pdb_sequence(PDB)



if __name__ == '__main__':
    main()