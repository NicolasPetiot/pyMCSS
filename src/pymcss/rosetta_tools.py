from .params import logger as log
from .params import ROSETTA_SCRIPT_CMD

import subprocess

def rosetta_script(xml:str, pdb:str, options:str = None):
    cmd = f"{ROSETTA_SCRIPT_CMD} -parser:protocol ${xml} -s {pdb}"
    if options is not None:
        cmd += f" @{options}"

    log.info(cmd)

    result = subprocess.run(cmd.split(), capture_output=True, text=True)

    if result.returncode != 0:
        raise ValueError("See ROSETTA-CRASH.log for details")
    
    return result