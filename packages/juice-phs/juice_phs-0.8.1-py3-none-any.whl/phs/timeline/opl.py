import xml.etree.ElementTree as ET
import csv
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np
import os


# Function to parse the OPL CSV file and return observations as a list of dictionaries
def parse_opl(opl_file, timeformat = 'datetime'):
    """
    TODO: Doc to be written
    """
    observations = []
    count = defaultdict(int)
    with open(opl_file, "r") as csvfile:
        reader = csv.reader(csvfile)
        unique_rows = set(tuple(row) for row in reader)  # Remove duplicate rows
        for row in unique_rows:
            if len(row) != 5:
                continue  # Skip rows with incorrect format

            # Parse start and end time based on requested format
            if timeformat == 'np.datetime64':
                if 'Z' in row[1]:
                    start_time = np.datetime64(row[1].split('Z')[0])
                else:
                    start_time = np.datetime64(row[1])


                if 'Z' in row[2]:
                    end_time = np.datetime64(row[2].split('Z')[0])
                else:
                    end_time = np.datetime64(row[2])
            else:
                try:
                    start_time = datetime.strptime(row[1], "%Y-%m-%dT%H:%M:%S.%fZ")  # Try with fractional seconds and Z
                except ValueError:
                    start_time = datetime.strptime(row[1], "%Y-%m-%dT%H:%M:%S")  # Fallback to naive datetime

                try:
                    end_time = datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%S.%fZ")  # Try with fractional seconds and Z
                except ValueError:
                    end_time = datetime.strptime(row[2], "%Y-%m-%dT%H:%M:%S")  # Fallback to naive datetime

            unit = row[4]
            count[unit] += 1

            # Put parsed information in dictionary
            # generic
            if "GENERIC" in row[4]:
                observation = {
                    "type": 'GENERIC',
                    "start_time": start_time,
                    "end_time": end_time,
                    "name": row[0], 
                    "unit": 'SOC',
                    "count": count[unit]
                }
            # instruments
            elif "OBSERVATION" in row[0]:
                observation = {
                    "type": row[0].split("_")[1],
                    "start_time": start_time,
                    "end_time": end_time,
                    "name": row[3], 
                    "unit": row[4],
                    "count": count[unit]
                }
            else: #segmentation
                observation = {
                    "type": "PRIME",
                    "start_time": start_time,
                    "end_time": end_time,
                    "name": row[0],
                    "unit": 'SOC',
                    "count": count[unit]
                }

            observations.append(observation)

    return observations


def dict2opl(observations, opl_fname):
    """
    Writes a list of observation dictionaries to a CSV file in OPL format.

    Parameters
    ----------
    observations (list of dict): A list of dictionaries, each representing an observation. 
                                 Each dictionary must contain the keys 'type', 'start_time', 'end_time', 'name', and 'unit'.
    opl_fname (str): The file name (including path) where the CSV file will be written.

    Returns
    -------
    None
    
    """

    opl_handle = open(opl_fname, mode='w', newline='')
    opl_writer = csv.writer(opl_handle)

    required_keys = ['type', 'start_time', 'end_time', 'name', 'unit']

    for observation in observations:
        observation_local = observation.copy()
        if all(key in observation for key in required_keys):
            if observation['type'] == 'OBSERVATION':
                observation_local['type'] = f'{observation["unit"]}_OBSERVATION'
            else: 
                observation_local['type'] = f'{observation["unit"]}_{observation["type"]}_OBSERVATION'


            opl_writer.writerow([observation_local[key] for key in required_keys])

        else:
            print(f"Some required fields are missing. Skipping observation {observation}")

    opl_handle.close()


def merge_opls(opl_folder, scenario_id, iteration='SXXPYY', units = ['3GM', 'GAL', 'JAN', 'MAG', 'MAJ', 'NAV', 'PEH', 'PEL', 'RAD', 'RIM', 'RPW', 'SWI', 'UVS']):
    """
    Merges OPL files from different units into a single list of observations.

    Parameters
    ----------
    opl_folder (str): The folder containing the OPL files.
    scenario_id (str): The scenario identifier.
    iteration (str, optional): The iteration identifier, default is 'SXXPYY'.
    units (list of str, optional): A list of unit identifiers to include in the merge, default includes all specified units.

    Returns
    -------
    list of dict: A list of merged observation dictionaries, sorted chronologically by 'start_time'.

    """

    # Include generic segments from segmentation
    opl_soc_init = f'{opl_folder}/OPL_SOC_{scenario_id}_S01P00.csv' 

    merged_observations = parse_opl(opl_soc_init, timeformat='np.datetime64')

    for unit in units:
        opl_fname = f'{opl_folder}/{unit}/OPL_{unit}_{scenario_id}_{iteration}.csv'

        if os.path.isfile(opl_fname):
            observations = parse_opl(opl_fname, timeformat='np.datetime64')
            merged_observations.extend(observations)
        else:
            print(f'{opl_fname} does not exist')

    # Sort chronologically
    merged_observations_sorted = sorted(merged_observations, key=lambda x: x['start_time'])

    return merged_observations_sorted