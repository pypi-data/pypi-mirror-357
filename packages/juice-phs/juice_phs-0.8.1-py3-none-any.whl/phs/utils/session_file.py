import os
import json
from shutil import move
from tempfile import mkstemp


def get_base_path(rel_path, root_path):
    return rel_path if os.path.isabs(root_path) \
                    else os.path.abspath(os.path.join(root_path, rel_path))


def write_local_session_file(relative_session_file, JUICE_PREOPS, KERNELS_JUICE):

    local_session_file = relative_session_file.replace(".json", "_local.json")

    replacements = {}
    replacements["JUICE_PREOPS"] = JUICE_PREOPS
    replacements["KERNELS_JUICE"] = KERNELS_JUICE

    with open(local_session_file, "w+") as f:

        # Items are replaced as per correspondence in between the replacements dictionary
        with open(relative_session_file, 'r') as t:
            for line in t:
                if '{' in line:
                    for k, v in replacements.items():
                        if '{' + k + '}' in line:
                            line = line.replace('{' + k + '}', v.replace("\\", "/"))

                f.write(line)

    print("Created OSVE local session file: " + os.path.abspath(local_session_file))
    print("Don't forget removing it when done.")

    return local_session_file


def load_session_file(session_file_path):
    with open(session_file_path) as f:
        return json.load(f)
    
    return None

def save_session_file(session_file_path, session):
    with open(session_file_path, 'w') as f:
        json.dump(session, f)


def show_report(session_file_path, root_scenario_path):
    with open(session_file_path) as f:
        config = json.load(f)

        agm_config = None
        eps_config = None
        input_config = None
        modelling_config = None

        if "sessionConfiguration" in config:

            sessionConfiguration = config["sessionConfiguration"]

            if "attitudeSimulationConfiguration" in sessionConfiguration:
                agm_config = sessionConfiguration["attitudeSimulationConfiguration"]

            if "instrumentSimulationConfiguration" in sessionConfiguration:
                eps_config = sessionConfiguration["instrumentSimulationConfiguration"]

            if "inputFiles" in sessionConfiguration:
                input_config = sessionConfiguration["inputFiles"]

                if "modellingConfiguration" in input_config:
                    modelling_config = input_config["modellingConfiguration"]

        print("")
        print("SESSION FILE REPORT:")

        if agm_config is not None:

            if "baselineRelPath" in agm_config:
                agm_base_path = get_base_path(agm_config["baselineRelPath"], root_scenario_path)
            else:
                print(" + No baselineRelPath found at attitudeSimulationConfiguration.")

            print("")
            print("- AGM:")

            if "ageConfigFileName" in agm_config:
                print(" + AGM configuration file: " + os.path.join(root_scenario_path, agm_base_path, agm_config["ageConfigFileName"]))
            else:
                print(" + No ageConfigFileName found at attitudeSimulationConfiguration.")

            if "fixedDefinitionsFile" in agm_config:
                print(" + AGM fixed definitions file: " + os.path.join(root_scenario_path, agm_base_path, agm_config["fixedDefinitionsFile"]))
            else:
                print(" + No fixedDefinitionsFile found at attitudeSimulationConfiguration.")

            if "predefinedBlockFile" in agm_config:
                print(" + AGM predefined block file: " + os.path.join(root_scenario_path, agm_base_path, agm_config["predefinedBlockFile"]))
            else:
                print(" + No predefinedBlockFile found at attitudeSimulationConfiguration.")

            if "eventDefinitionsFile" in agm_config:
                print(" + AGM event definitions file: " + os.path.join(root_scenario_path, agm_base_path, agm_config["eventDefinitionsFile"]))
            else:
                print(" + No eventDefinitionsFile found at attitudeSimulationConfiguration.")

            print("")
            print("- SPICE Kernels:")
            if "kernelsList" in agm_config:

                if "baselineRelPath" in agm_config["kernelsList"]:
                    kernels_base_path = get_base_path(agm_config["kernelsList"]["baselineRelPath"], root_scenario_path)
                else:
                    print(" + No baselineRelPath found at kernelsList.")

                if "fileList" in agm_config["kernelsList"]:
                    for kernel in agm_config["kernelsList"]["fileList"]:
                        if "fileRelPath" in kernel:
                            print(" + " + os.path.join(root_scenario_path, kernels_base_path, kernel["fileRelPath"]))
                        else:
                            print(" + No Kernel file relative path (fileRelPath) found.")
                else:
                    print(" + No fileList found at kernelsList.")
            else:
                print(" + No kernelsList found at attitudeSimulationConfiguration.")

        else:
            print("")
            print("- No AGM configuration found.")

        if eps_config is not None:
            eps_base_path = get_base_path(eps_config["baselineRelPath"], root_scenario_path)

            print("")
            print("- EPS:")

            if "unitFileName" in eps_config:
                print(" + EPS Units definition file: " + os.path.join(root_scenario_path, eps_base_path, eps_config["unitFileName"]))
            else:
                print(" + No EPS Units definition file (unitFileName) found.")

            if "configFileName" in eps_config:
                print(" + EPS Configuration file: " + os.path.join(root_scenario_path, eps_base_path, eps_config["configFileName"]))
            else:
                print(" + No EPS Configuration file (configFileName) found.")

            if "eventDefFileName" in eps_config:
                print(" + EPS Events definition file: " + os.path.join(root_scenario_path, eps_base_path, eps_config["eventDefFileName"]))
            else:
                print(" + No EPS Events definition file (eventDefFileName) found.")

            if modelling_config is not None:
                modelling_base_path = get_base_path(modelling_config["baselineRelPath"], root_scenario_path)

                if "edfFileName" in modelling_config:
                    print(" + EPS Experiments definition file (EDF): " + os.path.join(root_scenario_path, modelling_base_path, modelling_config["edfFileName"]))
                else:
                    print(" + No EPS Experiments definition file (edfFileName) found.")

                if "observationDefFileName" in modelling_config:
                    print(" + EPS Observations definition file: " + os.path.join(root_scenario_path, modelling_base_path, modelling_config["observationDefFileName"]))
                else:
                    print(" + No EPS Observations definition file (observationDefFileName) found.")

            else:
                print("")
                print("- No EPS Modelling configuration found.")
        else:
            print("")
            print("- No EPS configuration found.")

        if input_config is not None:
            input_base_path = get_base_path(input_config["baselineRelPath"], root_scenario_path)

            print("")
            print("- Input files: " + input_base_path)

            if "xmlPtrPath" in input_config:
                print(" + AGM PTR File: " + os.path.join(root_scenario_path, input_base_path, input_config["xmlPtrPath"]))
            else:
                print(" + No AGM PTR (xmlPtrPath) found.")

            if "segmentTimelineFilePath" in input_config:
                print(" + EPS ITL File: " + os.path.join(root_scenario_path, input_base_path, input_config["segmentTimelineFilePath"]))
            else:
                print(" + No EPS ITL (segmentTimelineFilePath) found.")

            if "eventTimelineFilePath" in input_config:
                print(" + EPS EVENT File: " + os.path.join(root_scenario_path, input_base_path, input_config["eventTimelineFilePath"]))
            else:
                print(" + No EPS EVENT (eventTimelineFilePath) found.")

        else:
            print("")
            print("- No input files configuration found.")

        print("")


def get_kernels_to_load(session_file_path, root_scenario_path):
    kernels_to_load = []

    with open(session_file_path) as f:
        config = json.load(f)

        if "sessionConfiguration" in config:
            sessionConfiguration = config["sessionConfiguration"]

            if "attitudeSimulationConfiguration" in sessionConfiguration:
                agm_config = sessionConfiguration["attitudeSimulationConfiguration"]

        if agm_config is not None:
            if "kernelsList" in agm_config:
                if "baselineRelPath" in agm_config["kernelsList"]:
                    kernels_base_path = get_base_path(agm_config["kernelsList"]["baselineRelPath"], root_scenario_path)
                else:
                    raise "No baselineRelPath found at kernelsList."

                if "fileList" in agm_config["kernelsList"]:
                    for kernel in agm_config["kernelsList"]["fileList"]:
                        if "fileRelPath" in kernel:
                            kernels_to_load.append(os.path.abspath(os.path.join(kernels_base_path, kernel["fileRelPath"])))
                        else:
                            raise "No Kernel file relative path (fileRelPath) found."
                else:
                    raise "No fileList found at kernelsList."
            else:
                raise "No kernelsList found at attitudeSimulationConfiguration."

        else:
            raise "No AGM configuration found."

    return kernels_to_load    


def write_local_mk(mk_path, kernels_path):
    replaced = False

    local_mk_path = mk_path.split('.')[0] + '_local.tm'

    if not os.path.exists(local_mk_path):
        # Create temp file
        fh, abs_path = mkstemp()
        with os.fdopen(fh, 'w') as new_file:
            with open(mk_path) as old_file:
                for line in old_file:

                    updated_line = line.replace("'..'","'" + kernels_path + "'")
                    new_file.write(updated_line)
                    # flag for replacing having happened
                    if updated_line != line:
                        replaced = True

        if replaced:
            # Update the permissions
            os.chmod(abs_path, 0o644)

            # Move new file

            move(abs_path, local_mk_path)

            print ("Created local SPICE Meta-Kernel: " + str(local_mk_path))

            return True, local_mk_path

    return False, ""

def remove_local_session_file(local_session_file):
    if os.path.exists(local_session_file):
        os.remove(local_session_file)
        print(f"OSVE local session file removed: {local_session_file}")
    else:
        print(f"OSVE local session file not present {local_session_file}")


def get_path_from_session_file(file_key, session_file_path, root_scenario_path):
    with open(session_file_path) as f:
        config = json.load(f)

        agm_config = None
        eps_config = None
        input_config = None
        modelling_config = None

        if "sessionConfiguration" in config:

            sessionConfiguration = config["sessionConfiguration"]

            if "attitudeSimulationConfiguration" in sessionConfiguration:
                agm_config = sessionConfiguration["attitudeSimulationConfiguration"]

            if "instrumentSimulationConfiguration" in sessionConfiguration:
                eps_config = sessionConfiguration["instrumentSimulationConfiguration"]

            if "inputFiles" in sessionConfiguration:
                input_config = sessionConfiguration["inputFiles"]

                if "modellingConfiguration" in input_config:
                    modelling_config = input_config["modellingConfiguration"]

        if agm_config is not None:

            if "baselineRelPath" in agm_config:
                agm_base_path = get_base_path(agm_config["baselineRelPath"], root_scenario_path)

            if file_key in agm_config:
                agm_base_path = os.path.join(root_scenario_path, agm_base_path)
                return os.path.join(agm_base_path, agm_config["ageConfigFileName"]), agm_base_path

        if eps_config is not None:
            eps_base_path = get_base_path(eps_config["baselineRelPath"], root_scenario_path)

            if file_key in eps_config:
                eps_base_path = os.path.join(root_scenario_path, eps_base_path)
                return os.path.join(eps_base_path, eps_config[file_key]), eps_base_path
            
            if modelling_config is not None:
                modelling_base_path = get_base_path(modelling_config["baselineRelPath"], root_scenario_path)

                if file_key in modelling_config:
                    modelling_base_path = os.path.join(root_scenario_path, modelling_base_path)
                    return os.path.join(modelling_base_path, modelling_config[file_key]), modelling_base_path

        if input_config is not None:
            input_base_path = get_base_path(input_config["baselineRelPath"], root_scenario_path)

            if file_key in input_config:
                input_base_path = os.path.join(root_scenario_path, input_base_path)
                return os.path.join(input_base_path, input_config[file_key]), input_base_path
    
    return None
