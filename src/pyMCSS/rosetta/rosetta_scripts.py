from ..log import log

import subprocess
import pandas as pd
from pathlib import Path

from shutil import move
from os import remove

__all__ = [
    "MutateHomodimer",
    "RestrainedDocking",

    "call_xml",
    "read_rosetta_scores",
]

ROSETTA_SCRIPT_CMD = "rosetta_scripts.default.linuxgccrelease"
XML_DIR = Path(__file__).parent / "XML"

# "Default" Rosetta Protocols
MutateHomodimer   = XML_DIR / "MutateHomodimer.xml"
RestrainedDocking = XML_DIR / "RestrainedDocking.xml"

def call_xml(xml:str, pdb:str, options:str = None, sc_out:str = None, **kwargs) -> pd.DataFrame:
    cmd = f"{ROSETTA_SCRIPT_CMD} -parser:protocol {xml} -s {pdb}"
    if options is not None:
        cmd += f" @{options}"

    if len(kwargs) > 0:
        cmd += " -parser:script_vars"

    for var, val in kwargs.items():
        cmd += f" {var}={val}"

    log.debug(cmd)
    result = subprocess.run(cmd.split(), capture_output=True, text=True)

    if result.returncode != 0:
        raise ValueError("See ROSETTA_CRASH.log for details")

    # Cleaning:
    sc = read_rosetta_scores("score.sc")
    if sc_out is not None:
        move("score.sc", sc_out)
        log.debug("scores saved as: " + str(sc_out))

    else:
        remove("score.sc")

    return sc
        
        

def read_rosetta_scores(sc:str) -> pd.DataFrame:
    lines = open(sc, 'r').readlines()
    lines = [line.removeprefix("SCORE:") for line in lines if line.startswith("SCORE:")]

    cols = lines[0].split()    
    data = [line.split() for line in lines[1:]]

    df = pd.DataFrame(data, columns=cols)
    df = df.set_index("description")
    df = df.astype(float)
    return df
