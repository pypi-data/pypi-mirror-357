import os

# ==============================================================================
#  PREDEFINED OVERLAYS FOR FAST OSVE DATAPACK CREATION:
# ==============================================================================
#
#  NOTE: All overlays shall be implemented as lists of overlay maps. In such
#        way the developer could directly extend its current datapack fields list
#        in one line.
#        
#         Example:
#
#         datapack = create_empty_datapack("blabla.csv", timeStep=10, precision=7)
#         datapack["fields"].extend(OSVE_OVERLAYS["ATT_QUAT"])
#         datapack["fields"].extend(OSVE_OVERLAYS["BODY_RATE"])
#         datapack["fields"].extend(OSVE_OVERLAYS["WMM_WHL_TORQUE"])
#
#         local_session_file_path = "ABSOLUTE PATH TO YOUR LOCAL OSVE SESSION FILE"
#         session = load_session_file(local_session_file_path)
#         session["sessionConfiguration"]["outputFiles"]["dataPacks"].append(datapack)
#         save_session_file(local_session_file_path, session)
#

OSVE_OVERLAYS = {

   "POWER":            [{ "type": "MAPPS", "overlayId": "TOTAL_POWER" },
                        { "type": "MAPPS", "overlayId": "EPS_SA_POWER" },
                        { "type": "MAPPS", "overlayId": "EPS_SA_AVAIL_POWER" },
                        { "type": "MAPPS", "overlayId": "EPS_SA_ANGLE" },
                        { "type": "MAPPS", "overlayId": "EPS_BATTERY_DOD" }],

   "ATT_QUAT":         [{ "type": "MAPPS", "overlayId": "ATT_QUAT_AXIS1" },
                        { "type": "MAPPS", "overlayId": "ATT_QUAT_AXIS2" },
                        { "type": "MAPPS", "overlayId": "ATT_QUAT_AXIS3" },
                        { "type": "MAPPS", "overlayId": "ATT_QUAT_VALUE" }],

    "BODY_RATE":       [{ "type": "MAPPS", "overlayId": "TOTAL_BODY_RATE" },
                        { "type": "MAPPS", "overlayId": "BODY_RATE_X" },
                        { "type": "MAPPS", "overlayId": "BODY_RATE_Y" },
                        { "type": "MAPPS", "overlayId": "BODY_RATE_Z" }],

    "WMM_WHL_TORQUE":  [{ "type": "MAPPS", "overlayId": "WMM_WHL_1_TORQUE" },
                        { "type": "MAPPS", "overlayId": "WMM_WHL_2_TORQUE" },
                        { "type": "MAPPS", "overlayId": "WMM_WHL_3_TORQUE" },
                        { "type": "MAPPS", "overlayId": "WMM_WHL_4_TORQUE" }]
}

# ==============================================================================
# ==============================================================================
#
#

# Returns a JSON with the whole files hierarchy including the ones
# referenced by "Include_file:" keyword in the EDFs or ITLs
def extract_files(file_path, basepath, is_recursive=False):

    file = open(file_path, "r")
    text = file.read()
    file.close()

    files = {}

    for line in text.splitlines():

        if line.startswith("#"):
            # Ignore comments
            continue

        tokens = line.split()

        if not len(tokens):
            # Ignore empty line
            continue
        

        if tokens[0] == "Include_file:":
            # Include_file: "JUICE/EDF_JUI_SPC_THERMAL.edf"

            incl_file_path = tokens[1].replace("\"", "")
            inc_files = extract_files(os.path.join(basepath, incl_file_path), basepath, is_recursive=True)
            files[os.path.join(basepath, incl_file_path)] = inc_files
    
    if not is_recursive:
        return {file_path: files}

    else:
        return files if len(files) else ""
    

# Returns a string with the contents of all the files including the ones
# referenced by "Include_file:" keyword in the EDFs or ITLs
def read_all_files(file_path, basepath):

    file = open(file_path, "r")
    text = file.read()
    file.close()

    all_text = ""

    for line in text.splitlines():
        
        all_text += line + "\r\n"

        if line.startswith("Include_file:"):
            # Include_file: "JUICE/EDF_JUI_SPC_THERMAL.edf"
            incl_file_path = line.split()[1].replace("\"", "")
            all_text += read_all_files(os.path.join(basepath, incl_file_path), basepath)

    return all_text


# Returns a JSON detailing the EPS Experiments model from an EDF file
def extract_modelling(edf_path, basepath):

    all_edfs_text = read_all_files(edf_path, basepath)

    model = {}

    experiment=None
    module=None

    for line in all_edfs_text.splitlines():

        if line.startswith("#"):
            # Ignore comments
            continue

        tokens = line.split()

        if not len(tokens):
            # Ignore empty line
            continue
        
        match tokens[0]:
            case "Experiment:":
                # Experiment: JUICE "JUICE Spacecraft"
                experiment = tokens[1]
                experiment_name = line.split("\"")[1] if "\"" in line else ""
                model[experiment] = { "id":   experiment,
                                    "name": experiment_name }

            case "Module:":
                # Module: RCT "RCT"
                module = tokens[1]
                module_name = line.split("\"")[1] if "\"" in line else ""
                if "modules" not in model[experiment]:
                    model[experiment]["modules"] = {}

                model[experiment]["modules"][module] = { "id":   module,
                                                        "name": module_name }
            case "Mode:":
                # Mode: OFF
                
                if "modes" not in model[experiment]:
                    model[experiment]["modes"] = []

                model[experiment]["modes"].append(tokens[1])
            
            case "Module_state:":
                # Module_state: OFF
                
                module_obj = model[experiment]["modules"][module]
                if "module_states" not in module_obj:
                    module_obj["module_states"] = []

                module_obj["module_states"].append(tokens[1])

    return model


# Prints in a formated way the files map returned by extract_files()
def print_files_map(files_map, indent="   ", carry_indent=""):
    for key in files_map:
        print(carry_indent + " - " + str(os.path.basename(key)))
        if not isinstance(files_map[key], str):
            print_files_map(files_map[key], indent=indent, carry_indent=(carry_indent + indent))
    
    print ("")


def create_empty_datapack(file_path, timeStep=30, precision=1):
    return { 
             "filePath": file_path,
             "timeStep": timeStep,
             "precision": precision,
             "fields": [{
                         "type": "time",
                         "format": "utc"
                         }]
            }


def get_exp_power_overlays(eps_modelling):

    overlays = []

    for exp_key in eps_modelling:
        experiment = eps_modelling[exp_key]

        exp_overlay = {
                        "type": "MAPPS",
                        "overlayId": "EXP_POWER",
                        "parameter1": exp_key
                      }
        overlays.append(exp_overlay)

        if "modules" in experiment:

            for module_key in experiment["modules"]:

                mod_overlay = {
                                 "type": "MAPPS",
                                 "overlayId": "EXP_POWER",
                                 "parameter1": exp_key,
                                 "parameter2": module_key
                              }
                overlays.append(mod_overlay)
    
    return overlays
