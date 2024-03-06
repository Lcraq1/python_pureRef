from typing import List
import os
from .items import PurImage, PurGraphicsTextItem

########################################################################################################################
# The class this whole project is about
# Build an interpreter for this class to make your own PureRef converter to/from
# any file format without having to decipher the hex bytes like I had to
########################################################################################################################


class PurFile:

    # A class holding all the images (which include their own transforms),
    # text and anything else that would be in a .pur file
    # Can be exported to a .pur file, can be imported from a .pur file and can be generated from images to later export
    def __init__(self):
        self.canvas = [-10000.0, -10000.0, 10000.0, 10000.0]  # Canvas width and height
        self.zoom = 1.0  # View zoom level
        self.xCanvas, self.yCanvas = 0, 0  # View location
        self.folderLocation = os.getcwd()
        self.images: List[PurImage] = []  # image list
        self.text: List[PurGraphicsTextItem] = []  # text list

    # Import a .pur file into this object
    def read(self, file: str):
        from purformat.read import read_pur_file
        read_pur_file(self, file)

    # Export this object to a .pur file
    def write(self, file: str):
        from purformat.write import write_pur_file
        write_pur_file(self, file)

    def count_image_items(self):
        # Count the amount of image transforms and assign their IDs
        count = 0
        for image in self.images:
            for transform in image.transforms:
                transform.id = count
                count += 1
        return count

    def count_text_items(self, id_offset: int):  # Text IDs start after image IDs (offset)
        # Count the amount of text transforms and assign their IDs
        count = 0

        def count_children(text_item: PurGraphicsTextItem):
            nonlocal count

            text_item.id = count + id_offset
            count += 1
            list(map(count_children, text_item.textChildren))

        list(map(count_children, self.text))

        return len(self.text)  # the header only wants to know direct children
