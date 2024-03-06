import os
import pureref_gen
import PZ_PureRefGen
import sys

"""

    PZ_PurerefInterface - PurRef Tool
    
Version: 0.01 
Author: Luc Craquelin

credit: https://github.com/FyorDev/PureRef-format.git

This Script should take in the "02_anim_screenshot" folder and output a pureRef

Current Goals:

1. output a .pur per sequence
2. add images in a row per shot
3. Add text

"""
purfolder_path = os.getcwd() + "/Purs"  # default output

# This is where PureRef files come out
if not os.path.exists(purfolder_path):
    os.mkdir(purfolder_path)

def getFolderInput():
    folder_path = input("Please Paste '02_anim_screenshot' dir here :")
    while "02_anim_screenshot" not in folder_path:
        print('!#############################################!')
        print("Incorrect '02_anim_screenshot' folder path")
        print('Example: ')
        print(r'Q:\BA_S04\04_production\03_outputs\sr_004\ep_002\02_anim_screenshot')
        folderpath = input('Try Again :')

    folders = next(os.walk(folder_path))[1]  # get all subfolders in imagefolder_path
    print("Starting Process")

    pur_name = folder_path.split("\\")[-1]

    PZ_PureRefGen.generate(folder_path,purfolder_path + pur_name + ".pur")
    #puref_gen.generate (_old)
    print("Finished Process. Output Location,:",purfolder_path)








if __name__ == "__main__":
    # Call the function only when the file is executed directly
    getFolderInput()