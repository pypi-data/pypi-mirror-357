from pathlib import Path
import os
import labdesk
from shutil import copy


configs_path = Path(os.path.abspath(labdesk.__file__)).parent / "configs/config.py"


def init(project_root: Path):
    # find project root 
    labdesk_dir = project_root / ".labdesk"

    if labdesk_dir.exists() and not labdesk_dir.is_dir():
        raise FileExistsError(f"{labdesk_dir} already exists and is not a directory.")

    if not labdesk_dir.exists():
        labdesk_dir.mkdir()

    if not (labdesk_dir / 'config.py').exists():
        copy(configs_path, labdesk_dir / 'config.py')
