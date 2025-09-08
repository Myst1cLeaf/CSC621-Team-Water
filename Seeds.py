import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
import argparse

# Store figures to display all at once after completion of processing
figures = []

def get_program_parameters():
    description = 'Read DICOM series data and perform 3D segmentation.'
    epilogue = '''
    Obtain and unzip DicomTestImages.zip.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('dirname', help='Directory containing DICOM files')
    args = parser.parse_args()
    return args.dirname

def read_dicom_series(directory):
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(directory)
    reader.SetFileNames(dicom_names)
    image = reader.Execute()
    return image

def edge_preserving_smoothing(image):
    # Use a Bilateral filter for edge-preserving smoothing
    smoothed_image = sitk.Bilateral(image, domainSigma=2.0, rangeSigma=50.0)
    return smoothed_image

def threshold_based_segmentation(image, lower_threshold, upper_threshold):
    binary_image = sitk.BinaryThreshold(image, lowerThreshold=lower_threshold,
                                        upperThreshold=upper_threshold, 
                                        insideValue=1, outsideValue=0)
    return binary_image

def region_growing_segmentation(image, seeds, threshold):
    # Use SimpleITK's ConnectedThreshold filter for region growing
    connector = sitk.ConnectedThresholdImageFilter()
    connector.SetLower(threshold[0])
    connector.SetUpper(threshold[1])
    
    for seed in seeds:
        connector.AddSeed(seed)
    
    return connector.Execute(image)

def store_image(image_slice, title):
    figures.append((image_slice, title))

def display_figures():
    for image_slice, title in figures:
        plt.figure(figsize=(6, 6))
        plt.imshow(image_slice, cmap='gray')
        plt.title(title)
        plt.axis('off')
        plt.savefig(f"{title}.png")  # Save the figure to a file
        plt.close()  # Close the figure to free up memory

def main():
    directory = get_program_parameters()

    # Read the DICOM series
    lung_image = read_dicom_series(directory)

    # Apply 3D edge-preserving smoothing to the entire volume
    smoothed_image = edge_preserving_smoothing(lung_image)

    # Store smoothed image for review
    smoothed_array = sitk.GetArrayFromImage(smoothed_image)
    store_image(smoothed_array[smoothed_array.shape[0] // 2], 'Smoothed Lung Image (Middle Slice)')

    # Apply threshold-based segmentation
    lower_threshold = 450
    upper_threshold = 1000
    binary_lungs = threshold_based_segmentation(smoothed_image, lower_threshold, upper_threshold)

    # Store binary image for review
    binary_array = sitk.GetArrayFromImage(binary_lungs)
    store_image(binary_array[binary_array.shape[0] // 2], 'Binary Lung Image (Middle Slice)')

    # Loop through each slice and apply region growing segmentation
    image_size = lung_image.GetSize()

    #3D region growing segmentation thresholds (modify as needed)
    region_lower_threshold = -600
    region_upper_threshold = -100
    #Image 17
    # uppert:-100 lowert:-600
    #Image 18
    # uppert:-300 lowert:-700
    #Image 19
    # uppert:-200 lowert:-700
    #Image 20
    # uppert:-100 lowert:-600
    #Image 21
    # uppert:-200 lowert:-600
    #Image 22
    # uppert:-200 lowert:-600
    #Image 23
    # uppert:-200 lowert:-600
    #Image 24
    # uppert:-200 lowert:-600
    #Image 25
    # uppert:5 lowert:-100
    #Image 26
    # uppert:5 lowert:-100
    #Image 27
    # uppert:-25 lowert:-140
    #Image 28
    # uppert:-3 lowert:-41
    #Image 29
    # uppert:55 lowert:21
    #Image 30
    # uppert:55 lowert:30


    for z in range(image_size[2]):  # Iterate through all slices (depth)
        # Define multiple seeds for each slice (example seeds)
        # Seed 1: (x1, y1, z) for one area of interest
        # Seed 2: (x2, y2, z) for another area of interest

        # List of seeds for images 17-30
        # Image 17 
        seed_1 = (192, 275, z) 
        seed_2 = (358, 216, z)
        #Image 18 
        #seed_1 = (192, 275, z) 
        #seed_2 = (358, 216, z)
        # Image 19
        #seed_1 = (192, 275, z) 
        #seed_2 = (358, 216, z)
        # Image 20 
        #seed_1 = (192, 275, z) 
        #seed_2 = (358, 212, z)
        # Image 21 
        #seed_1 = (103 , 280, z) 
        #seed_2 = (391, 225, z)
        # Image 22 
        #seed_1 = (103 , 280, z) 
        #seed_2 = (391, 225, z)
        # Image 23 
        #seed_1 = (103 , 280, z) 
        #seed_2 = (391, 225, z)
        # Image 24 
        #seed_1 = (103 , 280, z) 
        #seed_2 = (391, 225, z)
        # Image 25 
        #seed_1 = (111 , 192, z) 
        #seed_2 = (421, 242, z)
        # Image 26 
        #seed_1 = (111 , 192, z) 
        #seed_2 = (421, 242, z)
        # Image 27 
        #seed_1 = (159 , 234, z) 
        #seed_2 = (412, 254, z)
        # Image 28 
        #seed_1 = (113, 273, z) 
        #seed_2 = (393, 265, z)
        # Image 29 
        #seed_1 = (113 ,273 , z) 
        #seed_2 = (399, 270, z)
        # Image 30 
        #seed_1 = (117,268 , z) 
        #seed_2 = (345, 227, z)


        # Check if the seed points are valid
        seeds = []
        for seed in [seed_1, seed_2]:
            if (0 <= seed[0] < image_size[0] and 
                0 <= seed[1] < image_size[1] and 
                0 <= seed[2] < image_size[2]):
                seeds.append(seed)
                # Print the intensity values around the seed point for debugging
                seed_value = sitk.GetArrayFromImage(smoothed_image)[seed[2], seed[1], seed[0]]
                print(f"Slice {z}: Seed Point {seed} Value = {seed_value}")
            else:
                print(f"Invalid seed point for slice {z}: {seed}")

        if seeds:
            # Perform region growing segmentation with multiple seeds
            region_grown_lungs = region_growing_segmentation(smoothed_image, seeds, (region_lower_threshold, region_upper_threshold))
            
            # Store region grown image for review
            region_grown_array = sitk.GetArrayFromImage(region_grown_lungs)
            store_image(region_grown_array[z], f'Region Grown Lung Image (Slice {z})')

    # After all processing is done, display all figures
    display_figures()

if __name__ == '__main__':
    main()
