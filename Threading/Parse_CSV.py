import csv

def loadSettings(filename):
    """ Reads a CSV file containing settings for the cameras.
        Converts the CSV file into a dictionary.
        Joins the first 3 columns into 1 array

        The CSV file format:
        cam1, cam2, cam3, exposure, offset, gain
    
    Args:
        csv_file: The path to the CSV file.

    Returns:
        A dictionary, where the keys are the column header names 
            and the values are lists of the values in that column.
    """

    with open(filename, "r") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        data = {}
        camNum = 0
        for column in header:
            if "cam" in column:
                camNum = camNum + 1
        for row in reader:
            data.setdefault("cams", []).append(row[:camNum])
            for i, column_name in enumerate(header[camNum:]):
                data.setdefault(column_name, []).append(row[i + camNum])

    return data