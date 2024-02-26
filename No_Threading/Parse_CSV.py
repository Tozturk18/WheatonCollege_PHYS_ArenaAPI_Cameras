import csv
from typing import NamedTuple, List
import sys

class CameraSettings(NamedTuple):
    cameras: List[str]
    exposure: float
    offset: int
    gain: float 

def load_camera_settings(filename: str):
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

    Returns:
        :return: A dictionary, where the keys are the column header names 
                and the values are lists of the values in that column.
    """

    # Open the csv file with read permission
    with open(filename, "r") as csvfile:
        # Using CSV module, create a reader
        reader = csv.reader(csvfile)
        header = next(reader)   # Read the head

        camera_sets: [CameraSettings] = []  # Initialize an array to hold the CameraSettings NamedTuple
        camera_amount: int = 0              # Initialize a variable to hold the number of cameras

        # Count the number of cameras
        for column in header:
            if "cam" in column:
                camera_amount = camera_amount + 1

        # Create temporary variables for creating the NamedTuples
        cameras: List[str]
        exposure: float
        offset: int
        gain: float

        # Itterate through each row of the CSV file
        for row in reader:
            cameras = row[:camera_amount]
            for index, column_name in enumerate(header[camera_amount:]):
                
                if (column_name == "exp"):
                    exposure = float(row[index + camera_amount])
                elif(column_name == "off"):
                    offset = int(row[index + camera_amount])
                elif(column_name == "gain"):
                    gain = float(row[index + camera_amount])
                else:
                    sys.exit(f"Error! {filename} was wrongly formatted. Please check column names!")

            camera_sets.append( CameraSettings(cameras, exposure, offset, gain) )

    return camera_sets