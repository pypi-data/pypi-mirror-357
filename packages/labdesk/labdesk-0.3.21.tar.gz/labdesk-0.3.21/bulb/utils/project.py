import os
from pathlib import Path
from shutil import copy
from typing import Literal

import bulb

project_labdesk_dir = None
global_labdesk_dir = None
git_dir = None
project_root = None

_configs_path = Path(os.path.abspath(bulb.__file__)).parent / "configs/config_commented.py"

def load_paths(create=False):
    global git_dir, project_root, project_labdesk_dir, global_labdesk_dir

    global_labdesk_dir = check_labdesk_dir(Path.home() / '.labdesk', True)

    git_dir = find_root("git")

    if git_dir is not None:
        project_root = git_dir.parent
        project_labdesk_dir = check_labdesk_dir(project_root / '.labdesk', create)
    

def check_labdesk_dir(labdesk_dir:Path, create):
    if labdesk_dir.exists() and not labdesk_dir.is_dir():
        raise FileExistsError(f"{labdesk_dir} already exists and is not a directory.")

    if not create:
        return labdesk_dir if (labdesk_dir / 'config.py').exists() else None

    if not labdesk_dir.exists():
        labdesk_dir.mkdir()

    if not (labdesk_dir / 'config.py').exists():
        copy(_configs_path, labdesk_dir / 'config.py')

    return labdesk_dir


def find_root(type:Literal["git", "labdesk"]) -> Path:
    """
    Find the project root directory by looking for a .git directory.
    """
    current_dir = Path.cwd()

    i = 0
    while current_dir != Path("/"):
        if (current_dir / f".{type}").is_dir():
            return current_dir / f".{type}"
        
        if current_dir == Path("/") or i > 10:
            return

        current_dir = current_dir.parent
        i += 1