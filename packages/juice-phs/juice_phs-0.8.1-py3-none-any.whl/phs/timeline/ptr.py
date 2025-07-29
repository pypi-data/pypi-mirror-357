import xml.etree.ElementTree as ET
import csv
import sys
from collections import defaultdict
import xml.dom.minidom
from datetime import datetime, timedelta
import numpy as np

from phs.timeline.opl import parse_opl

def insert_target_comment(input_ptr_path,
                          output_ptr_path=False,
                          target='JUPITER',
                          verbose=True):
    """
    Insert a target comment into the metadata of each block in an XML file.

    This function reads an XML file and appends a comment indicating the specified target 
    into the metadata of each block element.

    Parameters:
    input_ptr_path (str): The path to the input XML file.
    output_ptr_path (str, optional): The path for the output XML file. 
                                      Defaults to the input file name with an added '.output' extension.
    target (str): The target name to insert into the comments. Defaults to 'JUPITER'.
    verbose (bool): If True, prints the modified XML. Defaults to True.

    Returns:
    str: The modified XML as a string.
    """
    
    if not output_ptr_path:
        output_ptr_path = input_ptr_path + '.output'

    # Read the XML content from the file
    with open(input_ptr_path, 'r') as file:
        xml_input = file.read()

    root = ET.fromstring(xml_input)

    # Iterate through all 'block' elements and check for the target
    for block in root.iter('block'):
        attitude = block.find('attitude')
        if attitude is not None:
            metadata = block.find('metadata')
            if metadata is not None:
                comment_element = ET.Element('comment')
                comment_element.text = f'TARGET={target}'
                metadata.append(comment_element)

    # Convert the modified XML back to string
    modified_xml = ET.tostring(root, encoding='unicode')
    # Write the modified XML to a new file
    with open(output_ptr_path, 'w') as file:
        file.write(modified_xml)

    if verbose:
        print(modified_xml)

    return modified_xml


def set_obs_id(input_ptr_path,
               output_ptr_path=False,
               verbose=False):
    """
    Set or update the OBS_ID in the metadata of OBS blocks in an XML file.

    This function reads an XML file, increments the OBS_ID for each OBS block, 
    and appends or updates the corresponding OBS_ID comment in the metadata.

    Parameters:
    input_ptr_path (str): The path to the input XML file.
    output_ptr_path (str, optional): The path for the output XML file. 
                                      Defaults to the input file name with an added '.output' extension.
    verbose (bool): If True, prints the modified XML. Defaults to False.

    Returns:
    str: The modified XML as a string.
    """
    
    obs_id = 0

    if not output_ptr_path:
        output_ptr_path = input_ptr_path + '.output'

    # Read the XML content from the file
    with open(input_ptr_path, 'r') as file:
        xml_input = file.read()

    root = ET.fromstring(xml_input)

    # Iterate through all 'block' elements and check for the target
    for block in root.iter('block'):
        if block.attrib.get('ref') == 'OBS':
            obs_id += 1
            metadata = block.find('metadata')
            if metadata is not None:
                obs_id_present = False
                # Iterate through existing comments to find and update OBS_ID
                for comment in metadata.findall(".//comment"):
                    if 'OBS_ID' in comment.text:
                        comment.text = f' OBS_ID={obs_id:03d} '
                        obs_id_present = True

                # If OBS_ID comment element is not present, add it
                if not obs_id_present:
                    comment_element = ET.Element('comment')
                    comment_element.text = f' OBS_ID={obs_id:03d} '
                    metadata.append(comment_element)

    #  <comment> Track Power Optimised Jupiter </comment>
    #  <comment> PRIME=UVS </comment>
    #  <comment> OBS_ID=002 </comment>
    #  <comment> OBS_NAME=UVS_JUP_AP_SCAN_MAP </comment>
    #  <comment> TARGET=JUPITER </comment>

    # Convert the modified XML back to string
    modified_xml = ET.tostring(root, encoding='unicode')
    # Write the modified XML to a new file
    with open(output_ptr_path, 'w') as file:
        file.write(modified_xml)

    if verbose:
        print(modified_xml)

    return modified_xml



def check_obs_metadata(input_file):
    """
    Processes an XML file to validate the structure and metadata within each <OBS> block.
    
    This function checks the following for each <OBS> block in the XML file:
    1. The presence of the <observations> element.
    2. If the <observations> element contains at least one <observation> element.
    3. The existence of required fields (such as 'type', 'definition', 'target', etc.) in each <observation>.
    4. Ensures there is exactly one 'DESIGNER' observation and that the 'unit' attribute matches the 'designer' attribute in the <observations> element.
    
    The function prints warnings and errors for any mismatches or missing elements. If the <OBS> block passes all checks, it will be reported as correctly structured.
    
    Parameters:
    - input_file (str): The path to the XML file to be processed.

    Returns:
    - None: The function directly prints the results of the validation to the console.
    """
    
    # Logic to process the XML file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Function to check for unit and designer mismatches and ensure one DESIGNER observation
    def check_mismatch(block):
        observations = block.findall('.//observations/observation')
        mismatches = []

        # Check if <observations> exists in the block
        observations_element = block.find('.//observations')
        if observations_element is None:
            mismatches.append("Error: <observations> element is missing in the block.")
            return mismatches  # No further checks if <observations> is missing

        # Check if there are any <observation> elements inside <observations>
        if not observations:
            mismatches.append("Error: No <observation> elements found inside <observations>.")
            return mismatches  # Return immediately if no <observation> is found
    
        # Get the 'designer' attribute from the parent <observations> element
        designer = block.find('.//observations').attrib.get('designer', None)

        # Track how many DESIGNER observations exist
        designer_count = 0
        prime_count = 0
        prime_found = False

        # Loop over all observations within a block
        for observation in observations:
            # Check for required parameters in each <observation>
            required_elements = ['type', 'definition', 'target', 'unit', 'startDelta', 'endDelta']
            observation_type = observation.find('type').text if observation.find('type') is not None else 'Unknown'
            
            for param in required_elements:
                element = observation.find(param)
                if element is None or not element.text.strip():
                    mismatches.append(f"Warning: Missing or empty element '{param}' in observation with observation type '{observation_type}'")

            if observation_type == 'PRIME':
                prime_count += 1
                unit = observation.find('unit').text.strip() if observation.find('unit') is not None else None

                # If there's a mismatch between the unit and the designer
                if unit == designer:
                    if not prime_found:
                        prime_found = True

            if observation_type == 'DESIGNER':
                designer_count += 1
                unit = observation.find('unit').text.strip() if observation.find('unit') is not None else None
                
                # If there's a mismatch between the unit and the designer
                if unit != designer:
                    mismatches.append(f"Mismatch found: Designer attribute: {designer}, Unit value: {unit}")

        if not prime_found:
            mismatches = [
                "Error: There should be an <observation> with <type> PRIME in an <observations> block."]

        # Check if there is exactly one DESIGNER observation
        if designer_count > 0:
            mismatches = ["Error: There should not be any <observation> with <type> DESIGNER in an <observations> block."]
        
        return mismatches

    # Process all blocks and print output
    for idx, block in enumerate(root.findall('.//timeline//block'), start=1):
        block_type = block.attrib.get('ref', '')
        # Skip SLEW blocks
        if block_type == 'OBS':
            start_time = block.find('.//startTime')
            start_time = start_time.text if start_time is not None else 'N/A'
                        
            # Check for unit/designer mismatch and DESIGNER observation rule
            mismatches = check_mismatch(block)
            if mismatches:
                print(f"TO CHECK: <!-- Block ({idx}) -->")
                for mismatch in mismatches:
                    print(f"{mismatch}")
                print(f" ")


def convert_ptr_to_opl(ptr_fname, output_opl_path=None, timeline_filter=None, unit_filter=None, designer_filter=False):
    """
    Extracts the observations from a PTR file and writes them to an OPL file.

    Parameters
    ----------
    ptr_fname (str): The path to the PTR file.
    output_opl_path (str): The path to the output OPL file.
    timeline_filter (str): The timeline filter to apply. Can be 'prime' or 'designer'.
    unit_filter (str): The unit filter to apply. Can be 'SWI', 'MAJIS', 'JANUS', 'PEPHI', 'PEPLO', 'UVS'.

    Returns
    -------
    None
    """

    # Read the XML content from the file
    tree = ET.parse(ptr_fname)
    root = tree.getroot()

    # Determine whether to output separately or all together
    #separate_files = output_split  

    prime_opl = output_opl_path
    prime_opl_handle = open(prime_opl, mode='w', newline='')
    opl_writer = csv.writer(prime_opl_handle)

    list_units = ['SWI', 'MAJIS', 'JANUS', 'PEPHI', 'PEPLO', 'UVS']
    list_timelines = ['PRIME', 'DESIGNER']

    if (timeline_filter is not None) and (timeline_filter not in list_timelines):
        print("WARNING: Filter not recognised. No OPL produced.")
        sys.exit()

    if (unit_filter is not None) and (unit_filter not in list_units):
        print("WARNING: Unit not recognised. No OPL produced.")
        sys.exit()

    count = defaultdict(int)

    for block in root.findall('.//block'):

        if block.items()[0][1] == 'OBS':
            start_time = block.find('startTime')
            end_time = block.find('endTime')

            if start_time is not None and end_time is not None: #if resolved
                start_time = start_time.text.strip()
                end_time = end_time.text.strip()
        
                attitude = block.find('attitude')
                metadata = block.find('metadata')

                if metadata is None:
                    print("WARNING: No metadata found in the PTR for startTime " + start_time)

                elif metadata.find('planning') is None:
                    print("WARNING: No planning element found metadata in the PTR for startTime " + start_time)

                else:
                    planning = metadata.find('planning')
                    observations_element = planning.find('observations')

                    if observations_element is None:
                        print("WARNING: No observations found in the PTR for startTime " + start_time)

                    else:
                        if designer_filter is True:
                            designer = observations_element.items()[0][1]

                            count[designer] += 1

                            obs_type_output = designer.upper() + '_DESIGNER_OBSERVATION'
                            start_time_output = start_time + 'Z' if start_time is not None else "UNKNOWN"
                            end_time_output = end_time + 'Z' if end_time is not None else "UNKNOWN"
                            definition = designer.upper() + ' DESIGNER_' + str(count[designer])
                            unit = designer

                            # Write to the corresponding writer
                            opl_writer.writerow([
                                obs_type_output,
                                start_time_output,
                                end_time_output,
                                definition,
                                unit
                            ])
                        else:
                            observation_list = observations_element.findall('observation')

                            for observation in observation_list:
                                obs_type = observation.find('type')

                                if (timeline_filter is None) or (obs_type.text == timeline_filter):
                                        unit = observation.find('unit')

                                        if (unit_filter is None) or (unit.text == unit_filter):
                                            definition = observation.find('definition')
                                            
                                            target = observation.find('target')
                                            start_time_obs = observation.find('startTime')
                                            end_time_obs = observation.find('endTime')                            

                                            if None in [obs_type, definition, unit, target, start_time_obs, end_time_obs]:
                                                print("WARNING: One or more fields are missing in an observation.")

                                            obs_type_upper = obs_type.text.strip().upper() if obs_type is not None else "UNKNOWN"
                                            definition = definition.text.strip() if definition is not None else "UNKNOWN"
                                            unit = unit.text.strip() if unit is not None else "UNKNOWN"
                                            target = target.text.strip() if target is not None else "UNKNOWN"
                                            start_time_obs = start_time_obs.text.strip() + 'Z' if start_time_obs is not None else "UNKNOWN"
                                            end_time_obs = end_time_obs.text.strip() + 'Z' if end_time_obs is not None else "UNKNOWN"
                                            obs_type_output = f"{unit}_{obs_type_upper}_OBSERVATION"
                                            
                                            if np.datetime64(start_time_obs.split('Z')[0]) > np.datetime64(end_time_obs.split('Z')[0]):
                                                print(f"WARNING: {definition} startTime {start_time_obs} is after endTime in observation. Not included in OPL.")

                                            else:
                                                # Write to the corresponding writer
                                                opl_writer.writerow([
                                                    obs_type_output,
                                                    start_time_obs,
                                                    end_time_obs,
                                                    definition,
                                                    unit
                                                ])



# Function to prettify XML without extra empty lines
def prettify(element):
    rough_string = ET.tostring(element, encoding="utf-8")
    parsed = xml.dom.minidom.parseString(rough_string)
    pretty_xml = parsed.toprettyxml(indent="  ")
    lines = [line for line in pretty_xml.splitlines() if line.strip()]  # Remove empty lines
    return "\n".join(lines)

# Function to format delta time in (+/-)hh:mm:ss format
def format_delta(delta_seconds):
    delta = timedelta(seconds=abs(delta_seconds))
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    sign = "+" if delta_seconds >= 0 else "-"
    return f"{sign}{hours:02}:{minutes:02}:{seconds:02}"

# Function to update PTR XML with observations from the OPL
def update_ptr_with_opl(ptr_file, opl_file, output_file):
    # Parse the OPL file
    opl_observations = parse_opl(opl_file)

    # Parse the PTR XML file
    tree = ET.parse(ptr_file)
    root = tree.getroot()

    # Iterate over PTR blocks and add observations
    for block in root.findall(".//block"):
        block_ref = block.get("ref")  # Get the reference of the block
        if block_ref != "OBS":  # Skip blocks that are not OBS
            continue

        block_start_time = block.find("startTime").text
        block_end_time = block.find("endTime").text
        try:
            block_attitude = block.find("attitude")
            if block_attitude is not None:
                block_target_element = block_attitude.find("target")
                if block_target_element is not None:
                    block_target = block_target_element.get("ref")  # Get the attribute 'ref'
                else:
                    block_target = None
            else:
                block_target = None
        except:
            block_target = None

        # Parse block start and end times with both possible formats
        try:
            block_start = datetime.strptime(block_start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            block_start = datetime.strptime(block_start_time, "%Y-%m-%dT%H:%M:%S")

        try:
            block_end = datetime.strptime(block_end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            block_end = datetime.strptime(block_end_time, "%Y-%m-%dT%H:%M:%S")

        # Determine the designer for this block
        designer_instrument = "SOC"  # Default to SOC
        for obs in opl_observations:
            if obs["type"] == "DESIGNER" and block_start <= obs["start_time"] < block_end:
                designer_instrument = obs["unit"]
                break

        # Clean up existing metadata
        metadata = block.find("metadata")
        if metadata is not None:
            # Remove <comment> elements
            for comment in metadata.findall("comment"):
                metadata.remove(comment)

            # Remove <planning> elements
            planning = metadata.find("planning")
            if planning is not None:
                metadata.remove(planning)

        # Create the <observations> element
        planning = ET.SubElement(metadata, "planning")
        observations_element = ET.SubElement(planning, "observations", designer=designer_instrument)

        # Add PRIME and RIDER observations to the timeline
        for obs in opl_observations:
            obs_start = obs["start_time"]
            obs_end = obs["end_time"]

            # Check observation inclusion rules
            if obs_end == block_start or obs_start == block_end:
                continue  # Skip observations ending at block start or starting at block end

            # Include only DESIGNER, PRIME, and RIDER observations in the timeline
            if obs["type"] not in ["PRIME", "RIDER", "DESIGNER"]:
                continue

            if block_start <= obs_start < block_end or block_start < obs_end <= block_end or (obs_start <= block_start and obs_end >= block_end):
                observation_element = ET.SubElement(observations_element, "observation")

                ET.SubElement(observation_element, "type").text = obs["type"]
                ET.SubElement(observation_element, "definition").text = obs["name"]
                ET.SubElement(observation_element, "unit").text = obs["unit"]
                if block_target: ET.SubElement(observation_element, "target").text = block_target

                # Calculate startDelta and endDelta based on block boundaries
                start_delta = max(0, (obs_start - block_start).total_seconds())
                end_delta = min((obs_end - block_end).total_seconds(), 0)

                ET.SubElement(observation_element, "startDelta").text = format_delta(start_delta)
                ET.SubElement(observation_element, "endDelta").text = format_delta(end_delta)
                ET.SubElement(observation_element, "startTime").text = obs_start.strftime("%Y-%m-%dT%H:%M:%S")
                ET.SubElement(observation_element, "endTime").text = obs_end.strftime("%Y-%m-%dT%H:%M:%S")

    # Prettify and write the updated PTR back to a new file
    with open(output_file, "w", encoding="utf-8") as output:
        output.write(prettify(root))


convert_ptr_to_opl('/Users/marc.costa/JUICE_PREOPS/PLANNING/SCENARIOS/S008_01_ORB17_321219_330108/POINTING/PTR_SOC_S008_01_SXXPYY.ptx', output_opl_path=f'/Users/marc.costa/JUICE_PREOPS/PLANNING/SCENARIOS/S008_01_ORB17_321219_330108/TIMELINE/OPL_PRI_S008_01_SXXPYY.csv', timeline_filter=None, designer_filter=False)
convert_ptr_to_opl('/Users/marc.costa/JUICE_PREOPS/PLANNING/SCENARIOS/S008_01_ORB17_321219_330108/POINTING/PTR_SOC_S008_01_SXXPYY.ptx', output_opl_path=f'/Users/marc.costa/JUICE_PREOPS/PLANNING/SCENARIOS/S008_01_ORB17_321219_330108/TIMELINE/OPL_DES_S008_01_SXXPYY.csv', timeline_filter=None, designer_filter=True)

for unit in ['SWI', 'MAJIS', 'JANUS', 'PEPHI', 'PEPLO', 'UVS']:
    convert_ptr_to_opl('/Users/marc.costa/JUICE_PREOPS/PLANNING/SCENARIOS/S008_01_ORB17_321219_330108/POINTING/PTR_SOC_S008_01_SXXPYY.ptx', output_opl_path=f'/Users/marc.costa/JUICE_PREOPS/PLANNING/SCENARIOS/S008_01_ORB17_321219_330108/TIMELINE/OPL_{unit}_S008_01_SXXPYY.csv', timeline_filter=None, unit_filter=unit, designer_filter=False)