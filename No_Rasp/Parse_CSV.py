import csv
from typing import NamedTuple, List
import sys
import itertools

# Define a NamedTuple to hold the camera settings
class CameraSettings(NamedTuple):
    cameras: List[str]  # The list of camera names
    exposure: float     # The exposure time
    offset: int         # The offset value
    gain: float         # The gain value
    number: int         # The number of iterations

def load_camera_settings(filename: str, cameras: List[str] = ['r', 'g', 'b'], offset: int = 0, gain: float = 0, number: int = 1, exposure: float = 1):
    """ 
    Reads a CSV file containing settings for the cameras.
    Converts the CSV file into a NamedTuple.
    Joins the first 3 columns into 1 array

    The CSV file format:
    cam1, cam2, cam3, exp, off, gain
    (Note: the header names has to be as given above)
    
    Args:
        :param csv_file: The path to the CSV file containing 
                camera settings (type: string).

        :param cameras: The list of camera names (type: list of strings, default value: ['r', 'g', 'b']).

        :param offset: The offset value (type: int, default value: 1).

        :param gain: The gain value (type: float, default value: 0.0).

        :param number: The number of iterations (type: int, default value: 1).

        :param exposure: The exposure time (type: float, default value: 1.0).

    Returns:
        :return: A dictionary, where the keys are the column header names 
                and the values are lists of the values in that column.
    """

    # Open the csv file with read permission
    with open(filename, "r") as csvfile:
        # Using CSV module, create a reader
        reader = csv.reader(csvfile)
        header = next(reader)   # Read the head

        camera_sets: List[CameraSettings] = []  # Initialize an array to hold the CameraSettings NamedTuple
        camera_amount: int = 0                  # Initialize a variable to hold the number of cameras

        # Count the number of cameras
        for column in header:
            if "cam" in column:
                camera_amount = camera_amount + 1

        # Check if the format of the CSV file
        if (camera_amount != 0):
            # If the user defined the cameras, then read the settings for the cameras from the CSV file

            # Iterate through each row of the CSV file
            for row in reader:

                # Ignore lines that start with #
                if row[0].startswith("#"):
                    continue

                # Get the camera names
                cameras = row[:camera_amount]

                # Get the settings for the cameras
                for index, column_name in enumerate(header[camera_amount:]):

                    if ("exp" in column_name):
                        exposure = float(row[index + camera_amount])
                    elif("off" in column_name):
                        offset = int(row[index + camera_amount])
                    elif("gain" in column_name):
                        gain = float(row[index + camera_amount])
                    elif("n_img" in column_name):
                        number = int(row[index + camera_amount])
                    else:
                        # If the column name is not any of the above, then the CSV file is wrongly formatted
                        sys.exit(f"Error! {filename} was wrongly formatted. Please check column names!")

                # Create a CameraSettings NamedTuple and append it to the camera_sets array
                camera_sets.append( CameraSettings(cameras, exposure, offset, gain, number) )
        else:
            # If there are no cameras given, then create permutations of the setting for the 3 cameras
            # Using the given offset, gain, number and exposure

            exposures : List[float] = []    # Initialize an array to hold the exposure settings
            offsets : List[int] = []        # Initialize an array to hold the offset settings
            gains : List[float] = []        # Initialize an array to hold the gain settings
            numbers : List[int] = []        # Initialize an array to hold the number of iterations settings

            # Iterate through each row of the CSV file
            for row in reader:

                # Ignore lines that start with #
                if row[0].startswith("#"):
                    continue

                # Get the settings for the cameras
                for index, column_name in enumerate(header):
                        
                        if ("exp" in column_name):
                            # If the exposure setting is not empty, then append it to the exposures array
                            if row[index] != "":
                                exposures.append(float(row[index]))
                        elif("off" in column_name):
                            # If the offset setting is not empty, then append it to the offsets array
                            if row[index] != "":
                                offsets.append(int(row[index]))
                        elif("gain" in column_name):
                            # If the gain setting is not empty, then append it to the gains array
                            if row[index] != "":
                                gains.append(float(row[index]))
                        elif("n_img" in column_name):
                            # If the number of iterations setting is not empty, then append it to the numbers array
                            if row[index] != "":
                                numbers.append(int(row[index]))
                        else:
                            # If the column name is not any of the above, then the CSV file is wrongly formatted
                            sys.exit(f"Error! {filename} was wrongly formatted. Please check column names!")

            # If the arrays are empty, then use the default values
            if ( len(exposures) == 0 ):
                exposures.append(exposure)
            if ( len(offsets) == 0 ):
                offsets.append(offset)
            if ( len(gains) == 0 ):
                gains.append(gain)
            if ( len(numbers) == 0 ):
                numbers.append(number)

            # Create permutations of the settings
            permutations = list(itertools.product(exposures, offsets, gains, numbers))

            # Create a CameraSettings NamedTuple for each permutation and append it to the camera_sets array
            for perm in permutations:
                camera_sets.append( CameraSettings(cameras, perm[0], perm[1], perm[2], perm[3]) )

    # Return the camera settings
    return camera_sets

'''
def entry_point():

    # Load the camera settings
    settings = load_camera_settings("test2.csv")

    # Display the camera settings on a table
    print("\n| camera 1 | camera 2 | camera 3 | Offset | Gain | Repeat | Offset |")
    for setting in settings:
        print("| ", setting.cameras[0], " | ", setting.cameras[1], " | ", setting.cameras[2], " | ", setting.offset, " | ", setting.gain, " | ", setting.number, " | ", setting.exposure, " |")
    
    # Start the code
if __name__ == "__main__":
	entry_point()
'''