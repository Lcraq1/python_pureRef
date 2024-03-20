import pprint

from PIL import Image
from pathlib import Path

def generatePixelArray(sample_count= 4,inset= .1,axis= "y",image_resolution= [1920,1080]):
    """
    Gerenate an array of pixel locations accorting to inset proportions of the image_resolution

    :param sample_count: How many pixels between the minimun 4 sample pixels
    :param inset: How deep do we want out sample like to be. .1 is %10 from the image edge
    :param axis: which axis to sample. y = Screen Left/Right
    :param image_resolution:
    :return:
    """

    # splitting image resoltion to get the inset proportion of x and y
    image_res_x = image_resolution[0]
    image_res_y = image_resolution[1]

    # Determining x coordinate max and minimum
    x_min = image_res_x * inset
    x_max = image_res_x - x_min

    # Determining x coordinate max and minimum
    y_min = image_res_y * inset
    y_max = image_res_y - y_min

    # delta is the proportionate spacing between pixel samples between out max and min
    delta_x = (x_max-x_min)/sample_count
    delta_y = (y_max-y_min)/sample_count

    pixel_list = []

    # For how many samples we need, produce the location
    for count in range(sample_count + 1):
        if axis == "y":
            i_value_y = y_min + (delta_y*count)

            # doubling the sample production and swapping between screen left and screen right
            for x in [x_min,x_max]:
                pixel_list.append((int(x),int(i_value_y)))

    return pixel_list

def samplePixelRGB(pixel_list,opened_image= Image.Image()):
    """
    Using the generate pixel list, we sample for the rgb value of each pixel xy location

    :param pixel_list: list from generatePixelArray
    :param opened_image:image opened in core function
    :return:
    """
    pixel_dic = {}

    # for each pixel xy location in the list, sample and add to dictionary
    for pixel in pixel_list:
        # getting rbg value
        rgb_value = opened_image.getpixel(pixel)

        # adding rbg value to dictionary with pixel xy location as the key
        pixel_dic[pixel] = rgb_value

        # debug function to show sample locations
        opened_image.putpixel(pixel, (255,0,0))

    # debug function to show sample locations
    opened_image.save("modified_image.jpg")

    return pixel_dic



def pixelCompare(image_pixel_dic, reference_pixel_dic, mismatch_threshhold = .3):
    """
    After sampling rgb value for the dictionary of pixels', compare to an older image_pixel_dic
    this is the reference_pixel_dic.

    :param image_pixel_dic: current image's sample pixel rgb's
    :param reference_pixel_dic: older image's image_pixel_dic
    :param mismatch_threshhold: Proportion of non-matching pixel colors until we keep the image
    :return: True or False: Image should be kept, True. Image should be discarded
    """
    # Creating a list of keys for use in loop
    pixel_xy_list =list(reference_pixel_dic)

    # List that will fill with True/False statements
    # True: pixels rgb matches, False: pixel rgb differs
    match_list = []

    # For each pixel location, compare rgb values between current and past image dictionaries
    for index,pixel_xy in enumerate(image_pixel_dic):

        # Extracting data from dictionary of processed image
        #Current
        pixel = image_pixel_dic[pixel_xy]
        #Old
        reference_pixel_rgb = reference_pixel_dic[pixel_xy]
        reference_pixel_xy = pixel_xy_list[index]

        # Pixel coordinates should always match
        # Todo: generate error if do not match
        """
        print("\npixel_xy_match: ", pixel_xy == reference_pixel_xy)

        
        print("pixel_rgb: " + str(pixel) )
        print("reference_pixel_rgb: " + str(reference_pixel_rgb))
        """

        # Do the rgb value match? add result to list
        rgb_match = (pixel == reference_pixel_rgb)
        match_list.append(rgb_match)

    # How many mismatches in rgb value are there, what is the portion to all samples?
    false_count = match_list.count(False)
    false_count_fraction = (false_count/len(match_list))

    # If we're over the failure threshold we'll consider the frame changed enough to keep it
    if false_count_fraction > mismatch_threshhold:
        # print("Allowed frame movement detected, keep")
        return True
    # Otherwise we don't need it
    elif false_count_fraction < mismatch_threshhold:
        # print("Frames match too closely, discard")
        return False

def filterShotFrames(shotframe_pathnames):
    """
    Removes frames that are too similar to the first to be useful in a contact sheet.
    Keeps frames that go over the determined threshold
    :param shotframe_pathnames: pathname list of one shot's frames. (provied from dictionary?)
    :return:
    """
    print("filtering frames:\n",shotframe_pathnames)
    # Generate a pixel coordination list, determined by size
    pixel_xy_list = generatePixelArray(sample_count=25)

    # Establish empty variables for looping through frame images
    # Referencing old dictionary of pixel rbg values
    reference_pixel_dic = {}

    # Image pathnames that make it through the filter
    filtered_pathnames = []


    for frame in shotframe_pathnames:
        frame_pathname = str(frame)
        # Opening image for use with PIL
        image = Image.open(frame_pathname)
        # If there is nothing in the reference_pixel_dic, we know this is the first frame and we should keep it
        if not reference_pixel_dic:

            # Sampling images for rgb values and declaring for use in 2nd loop
            reference_pixel_dic = samplePixelRGB(pixel_xy_list,opened_image=image)

            # Always keeping the first frame and adding it to the image_pathname_list
            filtered_pathnames.append(frame_pathname)
            """
            print("Keeping first image:",frame_pathname)

            
            pprint.pp(reference_pixel_dic)
            """

        # For second and third frames, compare to the prior pixel rgb dict ()
        else:
            # Sampling current image rgb values at the  pixel array location
            # Current image data
            image_pixel_dic = samplePixelRGB(pixel_xy_list,image)
            # Comparing current to old/referenced
            # If enough mismatches return (mismatches/total), we return False
            is_pixels_mismatch = pixelCompare(image_pixel_dic=image_pixel_dic,reference_pixel_dic=reference_pixel_dic,
                                           mismatch_threshhold=.3)
            # If our mismatch proportion his higher mismatch_threshhold, we keep the frame
            if is_pixels_mismatch:
                # print("kept image:\n",frame_pathname)
                filtered_pathnames.append(frame_pathname)

            # If our mismatch proportion his lower, there's not enough movement to keep the frame
            """
            elif not is_pixels_mismatch:
                print("discarding image:\n", frame_pathname)

            
            print("##### image_pixel_dic#####")
            print(jpg)
            pprint.pp(image_pixel_dic)
            print("#####                #####")
            """

            # Now that the mismatch check process is done, current "image_pixel_dic" becomes "reference_pixel_dic"
            # Ready for a new Loop
            reference_pixel_dic = image_pixel_dic

    print("filtered_pathnames:\n",filtered_pathnames,"\n")
    return filtered_pathnames

if __name__ == "__main__":
    # Call the function only when the file is executed directly
    test_path = r"C:\Users\lcraquelin\Pictures\sq_001_sh_001"
    shotframe_pathname_list = sorted([file.__str__() for file in Path(test_path).rglob("*.jpg")])
    print(shotframe_pathname_list)

    filterShotFrames(shotframe_pathname_list)








