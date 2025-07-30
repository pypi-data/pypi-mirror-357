from pathlib import Path
import os
import tempfile
from pathlib import Path
from textutil.replace import patch_file
from android_fake.network import *


def patch_csc(efs_dir, csc):
    efs_dir = Path(efs_dir)
    mps_code = efs_dir / 'imei/mps_code.dat' # BOG
    omcnw_code = efs_dir / 'imei/omcnw_code.dat' # XEU
    prodcode = efs_dir / 'imei/prodcode.dat' # SM-G950FZVAHTS

    patch_file


