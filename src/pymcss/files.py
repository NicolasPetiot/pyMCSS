from .params import logger as log

from pathlib import Path
from glob import glob

import os
from shutil import rmtree, copyfile, copytree

__all__ = ["rm", "cp"]

def rm(query:str|Path)-> None:
    """
    Used to remove file(s) / directory(ies)
    """

    if "*" in str(query):
        log.debug("rm in glob mode")
        names = glob(query)
        for name in names:
            remove(name)

    else:
        name = Path(query)
        remove(name)

def cp(src:str, dst:str) -> None:
    src = Path(src)
    if not src.exists():
        raise FileNotFoundError(f"{src} not found...")

    if src.is_dir():
        copytree(src, dst)
    
    else:
        copyfile(src, dst)

def remove(path:Path) -> None:
    """
    Used to remove a single file / directory
    """
    if not path.exists():
        raise FileNotFoundError(f"File/Directory {path} not found...")

    if path.is_dir():
        log.debug(f"Removing dir: {path}")
        rmtree(path)

    else:
        log.debug(f"Removing file: {path}")
        os.remove(path)
        
