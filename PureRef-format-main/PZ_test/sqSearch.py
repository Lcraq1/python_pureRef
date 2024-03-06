"""
test goals:

return images owned by 1 sequence

"""

from PIL import Image
import os
import re
from pathlib import Path
from io import BytesIO


def natural_keys(text):
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]


test_folder = r'Q:\BA_S04\04_production\03_outputs\sr_004\ep_002\02_anim_screenshot'
files_gen = sorted(os.listdir(test_folder), key=natural_keys)

files_LC = [file.__str__() for file in Path(test_folder).rglob("*.jpg") if "setup" not in file.__str__() ]

folders = next(os.walk(test_folder))[1]

sq_dic = {}
for folder in folders:
    if "setup" in folder:
        continue
    sequence = folder.split("_sh")[0]
    shot = folder

    if sequence not in sq_dic:
        sq_dic[sequence] = []

    if shot not in sq_dic[sequence]:
        sq_dic[sequence].append(folder)

sq_list = []

for folder in folders:
    if "setup" in folder:
        continue
    sequence = folder.split("_sh")[0]

    if sequence not in sq_list:
        sq_list.append(sequence)


import pprint

pprint.pprint(sq_list)

