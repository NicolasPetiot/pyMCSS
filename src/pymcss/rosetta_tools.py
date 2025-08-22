from .params import logger as log
from .params import ROSETTA_SCRIPT_CMD

import pandas as pd
import subprocess

def rosetta_script(xml:str, pdb:str, options:str = None):
    cmd = f"{ROSETTA_SCRIPT_CMD} -parser:protocol {xml} -s {pdb}"
    if options is not None:
        cmd += f" @{options}"

    log.debug(cmd)

    result = subprocess.run(cmd.split(), capture_output=True, text=True)

    if result.returncode != 0:
        raise ValueError("See ROSETTA-CRASH.log for details")
    
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
