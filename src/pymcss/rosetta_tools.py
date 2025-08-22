from .params import logger as log
from .params import ROSETTA_SCRIPT_CMD

import pandas as pd
import subprocess

from shutil import copyfile
from os import remove
from glob import glob

def rosetta_scripts(xml:str, pdb_in:str, option_str:str = None, pdb_out:str = None, sc_out:str = None, options_out:str = None, sort_by:str = None, clear_pdbs = True) -> pd.DataFrame|pd.Series:
    #1: Create option file (if needed)
    if option_str is not None:
        with open("tmp.options", "w") as file:
            file.write(option_str)

    #2: Run Rosetta Script:
    _ = call_xml(xml, pdb_in, options="tmp.options" if option_str is not None else None)
    scores = read_rosetta_scores("score.sc")
    if sort_by is not None:
        scores = scores.sort_values(sort_by)

    #3: Saving:    
    if pdb_out is not None:
        scores = scores.iloc[0]
        best_decoy = scores.name
        copyfile(best_decoy + ".pdb", pdb_out)

    if sc_out is not None:
        copyfile("score.sc", sc_out)

    if options_out is not None:
        copyfile("tmp.options", options_out)

    #4: Clearing:
    remove("tmp.options")
    if clear_pdbs:
        decoys = f"{pdb_in.removeprefix(".pdb")}_*.pdb"
        decoys = glob(decoys)
        for decoy in decoys:
            remove(decoy)

    return scores 

    

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
