import purformat.items as items
from purformat import purformat
from PIL import Image, ImageDraw, ImageFont
import os
import re
from io import BytesIO

from pathlib import Path


"""
    
    PZ_PureRefGen - PurRef Tool
    
Version: 0.12 
Author: Luc Craquelin

credit: https://github.com/FyorDev/PureRef-format.git

"""

####################################################################################################
# This function will create a neatly organized .pur (PureRef) file from a folder with PNG or JPG images
# It is used in pureref_gen_script.py to create .pur files from all folders in Artists/
####################################################################################################

def filterImageMovement():
    """
    Detecting a different between frames by comparing RBG difference in a  pixel array.
    :return:
    """


def generate(read_folder, write_file,sequence):

    # Natural sort https://stackoverflow.com/a/341745
    # For example: 0.jpg, 2.jpg, 10.jpg, 100.jpg
    # Instead of: 0.jpg, 10.jpg, 100.jpg, 2.jpg
    def textOverlayoOnImage(opened_image=None, text_input=None, text_location=(10, 20), text_color=(255, 255, 255)):
        """
        Opens image_pathname and adds text to image

        :param image_pathname:
        :return:
        """

        print("Editing Image")

        # Open image
        image = opened_image

        # Create a drawing context
        draw = ImageDraw.Draw(image)

        # Get the image's filename (without the extension)

        # Choose a font (you need to provide the path to a TrueType font file)
        font = ImageFont.truetype("arial.ttf", size=120)

        # Specify the text color
        text_col = text_color  # default: (255, 255, 255) is white

        # Position to place the text
        text_loc = text_location  # default: (10, 20) is top left

        # Add the text to the image
        draw.text(text_loc, text_input, fill=text_color, font=font)

        # Save the modified image with the name

        # Close the image

        return image

    def natural_keys(text):
        return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]

    def process_image(path):
        if not (path.endswith(".jpg") or path.endswith(".jpeg") or path.endswith(".png")):
            print("Skipping processing, not a valid image: " + path)
            return None

        print("Processing: " + path)


        image_name = str(path).split("\\")[-1]
        image_name = image_name.split(".jpg")[0]
        shot_nameframe = image_name.split("_")[-1]

        print("shot_nameframe: " + shot_nameframe)

        image = Image.open(path).convert(mode="RGB")
        image_PILed = textOverlayoOnImage(image,shot_nameframe)
        pur_image = items.PurImage()

        with BytesIO() as f:
            image_PILed.save(f, format="PNG", compress_level=7)  # TODO: research why PureRef saves PNG differently sometimes
            pur_image.pngBinary = f.getvalue()
            # bytes are used instead of PIL because the pngBinary can also be a reference to another image's transform
            # (duplicate images) this is the easiest way to handle it TODO: make PurFile work with PIL images

        pur_transform = items.PurGraphicsImageItem()
        pur_transform.reset_crop(image.width, image.height)
        pur_transform.name = path.replace(".jpg", "")
        pur_transform.source = path
        pur_image.transforms = [pur_transform]  # the first transform is the original, rest are duplicates

        return pur_image

    # Initialize an empty .pur file which will hold objects for images with transforms(1, n), and text
    pur_file = purformat.PurFile()

    # Add all images in read_folder to pur_file
    # The images will be sorted using natural sort, number them to control order
    files = sorted(os.listdir(read_folder), key=natural_keys)

    file_dic = {}

    for file in Path(read_folder).rglob("*.jpg"):
        file = str(file)
        if "setup" not in file:
            file_name = file.split("\\")[-1]
            file_dic[file_name] = file


    s_folder = "S"+ read_folder[1:]

    files_s = sorted([file.__str__() for file in Path(s_folder).rglob("*.jpg") if "setup" not in file.__str__()])

    for file in files_s:
        file = str(file)
        if file not in file_dic and "setup" not in file:
            file_name = file.split("\\")[-1]
            file_dic[file_name] = file

    Keys = list(file_dic.keys())
    Keys.sort()
    file_dic = {i: file_dic[i] for i in Keys}

    sq_files = []

    for shot_name in file_dic:
        if sequence in shot_name:
            sq_files.append(file_dic[shot_name])

    #import pprint
    #pprint.pprint(sq_files)


    pur_file.images = [process_image(os.path.join(read_folder, file)) for file in sq_files]
    pur_file.images = [image for image in pur_file.images if image is not None]  # remove None values

    if not pur_file.images:
        print("Skipping, no valid images found in " + read_folder)
        return

    # Start transforming images to automatically order
    transforms = [transform for image in pur_file.images for transform in image.transforms]

    [transform.scale_to_height(1000) for transform in transforms]  # normalize all images to height 1000

    total_width = sum([transform.width for transform in transforms])

    all_rows = [transforms]

    rows = []

    import math
    total_rows = math.ceil(len(transforms)/3)

    # Start index for slicing
    start_index = 0

    while len(rows) < total_rows:
        # Slice the next set of elements from all_transforms
        subset = transforms[start_index:start_index + 3]

        # Append the subset to rows
        rows.append(subset)

        # Update the start index for the next iteration
        start_index += 3

        # Break the loop if start_index exceeds the length of all_transforms
        if start_index >= len(transforms):
            break

    # Normalize row widths and actually place images, this makes everything line up perfectly.
    placement_y = 0

    # if not empty
    for row in [row for row in rows if row]:  # deals with empty rows
        row_width = sum([transform.width for transform in row])
        scale_factor = 1000/row_width  # the entire row is normalized to 1000 width

        placement_x = 0
        for transform in row:
            transform.scale(scale_factor)

            transform.x = placement_x + transform.width / 2
            placement_x += transform.width
            transform.y = placement_y + transform.height / 2

        placement_y += 1000 * scale_factor  # images are 1000 height and scaled to row width

    pur_file.write(write_file)
    print("Done! File created")

