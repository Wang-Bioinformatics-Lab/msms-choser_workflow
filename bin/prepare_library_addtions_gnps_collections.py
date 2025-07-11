#!/usr/bin/python
import sys
import getopt
import os
import pandas as pd
import argparse

import ming_fileio_library
import ming_mass_spec_library
import ming_spectrum_library
import proteosafe


from collections import defaultdict
import mass_from_structure
import inchi_smile_converter
import yaml


# get taskid form task_params file
#def getTaskId(filename):
#    with open(filename, 'r') as file:
#        for line in file:
            # Check if the line starts with the specified prefix
#            if line.startswith("task:"):
                # Extract the part after ":" and return
#                return line.split(':', 1)[1].strip()

# get taskid from job_parameters.yaml file
def getTaskId(file_path):
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            # Check if 'task' field exists in the YAML data
            if 'task' in data:
                return data['task']
            else:
                return None
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None

def process_candidate_molecules(candidate_molecules, path_to_spectrum_files, taskid):
    #Grouping by filename
    structures_by_filename = defaultdict(list)

    for candidate_object in candidate_molecules:
        filename = candidate_object["filename"]
        structures_by_filename[filename].append(candidate_object)

    output_dict = defaultdict(list)

    for filename in structures_by_filename:
        # if param exists => proteosafe workflow => demangle fileName
        path_to_spectrum_file = os.path.join(path_to_spectrum_files, filename)
        displaying_filename = filename

        #loading file
        spectrum_list = []
        try:
            leave, extension = os.path.splitext(path_to_spectrum_file)
            if extension.lower() == '.mzxml':
                spectrum_list = ming_spectrum_library.load_mzxml_file(path_to_spectrum_file)
            if extension.lower() == '.mzml':
                spectrum_list = ming_spectrum_library.load_mzml_file(path_to_spectrum_file)
            #print("LOADING", path_to_spectrum_file, len(spectrum_list))
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("Could not load", path_to_spectrum_file)
            spectrum_list = []

        #structure_object is candidate from tsv, spectrum is the input features
        #print(structures_by_filename)
        for structure_object in structures_by_filename[filename]:
            highest_intensity = -1000
            best_spectrum = None
            ppm_threshold = candidate_object["ppm_threshold"]
            #print(structure_object, len(spectrum_list))
            #print("molecule mass","monoisotopic mass","ppm","filename","exact_mass","adduct")
            for spectrum in spectrum_list:
                if spectrum.ms_level == 1:
                    continue

                #evaluate candidate_object
                monoisotopic_mass = structure_object["monoisotopic_mass"]

                mz_delta = abs(spectrum.mz - monoisotopic_mass)
                ppm_delta = (mz_delta / monoisotopic_mass ) * 1000000
                if ppm_delta > ppm_threshold:
                    continue
                else:
                    if spectrum.get_total_spectrum_intensity() > highest_intensity:
                        #print(ppm_delta,ppm_threshold)
                        best_spectrum = spectrum
                        highest_intensity = max(spectrum.totIonCurrent, spectrum.get_total_spectrum_intensity())

            if best_spectrum != None and highest_intensity > candidate_object["min_precursor_int"]:
                #print(structure_object["monoisotopic_mass"],candidate_object["monoisotopic_mass"])
                #output_dict["FILENAME"].append(os.path.basename(filename))
                output_dict["FILENAME"].append(displaying_filename)
                #usi = "mzspec:GNPS2:TASK-" + taskid + path_to_spectrum_file + ":scan:"+ str(best_spectrum.scan) 
                output_dict["USI"].append("mzspec:GNPS2:TASK-" + taskid + "-" + path_to_spectrum_file + ":scan:"+ str(best_spectrum.scan))
                output_dict["SEQ"].append("*.*")
                output_dict["COMPOUND_NAME"].append(structure_object["name"])
                output_dict["MOLECULEMASS"].append(structure_object["monoisotopic_mass"])
                output_dict["INSTRUMENT"].append(structure_object["instrument"])
                output_dict["IONSOURCE"].append(structure_object["ionsource"])
                output_dict["EXTRACTSCAN"].append(best_spectrum.scan)
                output_dict["SMILES"].append(structure_object["smiles"])
                output_dict["INCHI"].append(structure_object["inchi"])
                output_dict["INCHIAUX"].append("N/A")
                output_dict["CHARGE"].append(structure_object["charge"])
                output_dict["IONMODE"].append(structure_object["ionmode"])
                output_dict["PUBMED"].append(structure_object["pubmed"])
                output_dict["ACQUISITION"].append(structure_object["acquisition"])
                output_dict["EXACTMASS"].append(structure_object["exact_mass"])
                output_dict["DATACOLLECTOR"].append(structure_object["datacollector"])
                output_dict["ADDUCT"].append(structure_object["adduct"])
                output_dict["INTEREST"].append("N/A")
                output_dict["LIBQUALITY"].append("1")
                output_dict["GENUS"].append("N/A")
                output_dict["SPECIES"].append("N/A")
                output_dict["STRAIN"].append("N/A")
                output_dict["CASNUMBER"].append(structure_object["casnumber"])
                output_dict["PI"].append(structure_object["pi"])
                
                #print(spectrum.mz, monoisotopic_mass, ppm_delta, filename, structure_object["exact_mass"],structure_object["adduct"])
                #print("Found ", structure_object["name"],structure_object["adduct"], highest_intensity)
            else:
                continue
                #print("Not Seen", structure_object["name"], structure_object["adduct"], highest_intensity)

    return output_dict


def main():
    parser = argparse.ArgumentParser(description='Annotate spectra')
    parser.add_argument("input_annotations")
    parser.add_argument("path_to_spectra")
    parser.add_argument("output_batch")
    #parser.add_argument("task")
    parser.add_argument("--ppm_tolerance", type=float, default=10.0)
    parser.add_argument("--task_params")
    #parser.add_argument("task")

    args = parser.parse_args()

    taskid = getTaskId(args.task_params)
    #taskid = args.task

    # accepts both now
    annotations_df = pd.read_csv(args.input_annotations, sep=None)
        
    annotation_records = annotations_df.to_dict(orient="records")
    candidate_molecules = []
    for annotation in annotation_records:
        filename = annotation["FILENAME"]

        try:
            # filling in smiles and inchi if any is missing
            smiles = ""
            inchi = ""
            
            if "SMILES" in annotation:
                smiles = str(annotation["SMILES"])
            if "INCHI" in annotation:
                inchi = str(annotation["INCHI"])

            if len(inchi) > 4 and len(smiles) < 4:
                smiles = inchi_smile_converter.inchi2smiles(inchi)
            if len(smiles) > 4 and len(inchi) < 4:
                inchi = inchi_smile_converter.smiles2inchi(smiles)
            
            exact_mass = mass_from_structure.mass_from_smiles(smiles)

            if exact_mass <= 0:
                continue
        except KeyboardInterrupt:
            raise
        except:
            print("Error Entry")
            continue

        # replace exact_mass by querying from the webapi
        ionmode = annotation["IONMODE"]
        ionsource = annotation["IONSOURCE"]
        acquisition = annotation["ACQUISITION"]
        instrument = annotation["INSTRUMENT"]
        casnumber = annotation["CASNUMBER"]
        pi = annotation["PI"]
        intensity_threshold = 10
        compound_name = annotation["COMPOUND_NAME"]
        pubmed = annotation["PUBMED"]
        datacollector = annotation["DATACOLLECTOR"]

        adduct_list = []
        #why charge set to be 1?
        #charge = 1
        #print(ionmode)
        if ionmode == "Positive":
            adduct_list = ["M", "M+H", "M-H2O+H", "2M+Na", "M+Na", "M-2H2O+H", "2M+H", "M+K", "2M+K"]
        else:
            adduct_list = ["M-H", "2M-H","2M-2H+Na"]

        for adduct in adduct_list:
            monoisotopic_mass, charge = ming_mass_spec_library.get_adduct_mass(exact_mass, adduct)

            candidate_object = {}
            candidate_object["name"] = compound_name
            # if arg.param is set (workflow mode), demangle file name
            candidate_object["filename"] = filename
            candidate_object["charge"] = charge
            candidate_object["ionmode"] = ionmode
            candidate_object["smiles"] = smiles
            candidate_object["inchi"] = inchi
            candidate_object["monoisotopic_mass"] = monoisotopic_mass
            candidate_object["exact_mass"] = exact_mass
            candidate_object["min_precursor_int"] = intensity_threshold
            candidate_object["instrument"] = instrument
            candidate_object["adduct"] = adduct
            candidate_object["casnumber"] = casnumber
            candidate_object["acquisition"] = acquisition
            candidate_object["pi"] = pi
            candidate_object["pubmed"] = pubmed
            candidate_object["charge"] = charge
            candidate_object["ionsource"] = ionsource
            candidate_object["datacollector"] = datacollector
            candidate_object["ppm_threshold"] = args.ppm_tolerance

            candidate_molecules.append(candidate_object)

    #output_dict = process_candidate_molecules(candidate_molecules, args.path_to_spectra)
    output_dict = process_candidate_molecules(candidate_molecules, args.path_to_spectra, taskid)
    header_list = ["USI", "FILENAME", "SEQ", "COMPOUND_NAME", "MOLECULEMASS", "INSTRUMENT", "IONSOURCE", "EXTRACTSCAN", "SMILES", "INCHI", "INCHIAUX"]
    header_list += ["CHARGE", "IONMODE", "PUBMED", "ACQUISITION", "EXACTMASS", "DATACOLLECTOR", "ADDUCT", "INTEREST", "LIBQUALITY", "GENUS", "SPECIES", "STRAIN", "CASNUMBER", "PI"]

    df = pd.DataFrame(output_dict)

    if len(output_dict) == 0:
        print("No Data Found")
        exit(1)
    
    df.to_csv(args.output_batch, sep="\t", columns=header_list, index=False)



if __name__ == "__main__":
    main()
