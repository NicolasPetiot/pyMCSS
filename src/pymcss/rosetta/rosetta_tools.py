from ..params import logger as log
from ..params import ROSETTA_SCRIPT_CMD
from ..files import rm, cp

import pandas as pd
import subprocess

__all__ = [
    "run_rosetta_scripts",
    "call_xml",
    "read_rosetta_scores",
]

def run_rosetta_scripts(xml:str, pdb_in:str, option_str:str = None, pdb_out:str = None, sc_out:str = None, options_out:str = None, sort_by:str = None, clear_pdbs = True) -> pd.Series:
    #1: Create option file (if needed)
    if option_str is not None:
        log.debug("Writing tmp.options")
        with open("tmp.options", "w") as file:
            file.write(option_str)

    #2: Run Rosetta Script:
    _ = call_xml(xml, pdb_in, options="tmp.options" if option_str is not None else None)
    scores = read_rosetta_scores("score.sc")
    if sort_by is not None:
        log.debug("Sorting scores by:" + sort_by)
        scores = scores.sort_values(sort_by)
    score = scores.iloc[0]

    #3: Saving:    
    if pdb_out is not None:
        best_decoy = f"{score.name}.pdb"
        cp(best_decoy, pdb_out)

    if sc_out is not None:
        cp("score.sc", sc_out)

    if options_out is not None:
        cp("tmp.options", options_out)

    #4: Clearing:
    rm("tmp.options")
    rm("score.sc")
    if clear_pdbs:
        for decoy in scores.index:
            rm(str(decoy) + ".pdb")

    return score

    

def call_xml(xml:str, pdb:str, options:str = None):
    cmd = f"{ROSETTA_SCRIPT_CMD} -parser:protocol {xml} -s {pdb}"
    if options is not None:
        cmd += f" @{options}"

    log.debug(cmd)

    result = subprocess.run(cmd.split(), capture_output=True, text=True)

    if result.returncode != 0:
        raise ValueError("See ROSETTA_CRASH.log for details")
    
    return result

def read_rosetta_scores(sc:str) -> pd.DataFrame:
    lines = open(sc, 'r').readlines()
    lines = [line.removeprefix("SCORE:") for line in lines if line.startswith("SCORE:")]

    cols = lines[0].split()    
    data = [line.split() for line in lines[1:]]

    df = pd.DataFrame(data, columns=cols)
    df = df.set_index("description")
    df = df.astype(float)
    return df
