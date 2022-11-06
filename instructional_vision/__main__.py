from PyPDF2 import PdfReader, PdfWriter

import logging
import os
import shutil
import csv
import pandas as pd
import sys

import random
import string

from .pdf_preparation import crop_textregions_from, crop_metadataregion_from
from .gc_handwriting_detection import pdf_to_txt_for

# Configuration
infile_base_directory = "./input/"
outfile_base_directory = "./output/"

def prepare_csv(nrows = 10000):
    # Check if csv file already exists.
    if os.path.isfile(infile_base_directory + "Postulat2022.csv"):
        raise NameError("CSV file already exists.")

    id_set = set()
    while ( len(id_set) < nrows ):
        length = 6
        # Generate random ID with given length.
        random.seed(a = 2022)
        id_set.add(
            ''.join([random.choice(string.ascii_uppercase) for _ in range(length)])
        )
    ids = list(id_set)
    ids = sorted(ids)
    ids = pd.DataFrame(ids, columns = ["ZuordnungsID"])
    ids["Quelle_Schule"] = ""
    ids["Quelle_Jahr"] = ""
    ids["Quelle_Datei"] = ""
    ids["Kandidatennummer"] = ""
    ids["Note_Gesamt"] = ""
    ids["Note_Abzug_Inhalt"] = ""
    ids["Note_Abzug_Stil"] = ""
    ids["Note_Abzug_GrOrIp"] = ""
    ids["ThemaNr"] = ""
    ids["Titel"] = ""
    ids["Pilot_Sample"] = ""

    ids.to_csv(outfile_base_directory + "Postulat2022.csv", index = False, sep = ";")

def crop_pdfs():
    # Set logging level.
    logging.basicConfig(level=logging.INFO)

    # Get CSV Databes for filenaming
    csv_data = pd.read_csv(outfile_base_directory + "Postulat2022.csv", sep = ";")

    # Get IDs without entry
    csv_free_ids = csv_data[csv_data["Quelle_Datei"].isnull()]
    csv_free_ids = list(csv_free_ids.ZuordnungsID.index)
    csv_free_ids.reverse()

    for school in ["Sargans", "Wil", "Wattwil"]:
        for year in range(2012, 2023):
            infile_directory = infile_base_directory + school + "/" + str(year) + "/"
            outfile_directory = outfile_base_directory + school + "/" + str(year) + "/"

            if not os.path.isdir(infile_directory):
                logging.info(f"No data found in {infile_directory}.")
                # Skip iteration
                continue
            if os.path.isdir(outfile_directory):
                logging.info(f"Output directory already exists. Skipping {infile_directory}.")
                # Skip iteration
                continue

            logging.info(f"Cropping all *.pdf in {infile_directory}.")
            for file in os.listdir(infile_directory):
                infile_name = os.fsdecode(file)
                infile_path = infile_directory + infile_name

                if infile_path.endswith(".pdf"):
                    outfile_id = csv_free_ids.pop()
                    outfile_name = outfile_directory + str(csv_data.at[outfile_id, 'ZuordnungsID']) + ".pdf"
                    csv_data.at[outfile_id, 'Quelle_Schule'] = school
                    csv_data.at[outfile_id, 'Quelle_Jahr'] = year
                    csv_data.at[outfile_id, 'Quelle_Datei'] = infile_name
                    crop_textregions_from(
                        infile_path,
                        essay_source = "Postulat2022",
                        page_size = "a3",
                        outfile_path = outfile_name
                    )
                    crop_metadataregion_from(
                        infile_path,
                        essay_source = "Postulat2022",
                        page_size = "a3",
                        outfile_path = outfile_name.replace(".pdf", "_metadata.pdf")
                    )
    csv_data.to_csv(outfile_base_directory + "Postulat2022_updated.csv", index = False, sep = ";")

def choose_sample():
    # Set logging level.
    logging.basicConfig(level=logging.INFO)

    # Get CSV Databes for filenaming
    csv_texts = pd.read_csv(infile_base_directory + "Postulat2022_updated_v9.csv", sep = ";")
    csv_subjects = pd.read_csv(infile_base_directory + "Postulat2022_updated_v9_Themenwahl.csv", sep = ";")

    for index, row in csv_subjects.iterrows():
        sample = csv_texts.query("Quelle_Jahr == {0} & ThemaNr == {1}".format(row["Jahr"], row["Thema"]))
        for school in ["Sargans", "Wil", "Wattwil"]:
            school_sample = sample.query("Quelle_Schule == '{0}'".format(school))
            if len(school_sample) > 35:
                school_sample = school_sample.sample(n=35, random_state=2022)

            logging.info(f"Sampling {len(school_sample)} texts from {row['Jahr']} {school}.")
            for sample_index, sample_row in school_sample.iterrows():
                ## Prepare input path (source pdf file)
                in_path = outfile_base_directory + school + "/" + str(row["Jahr"]) + "/"
                in_path = in_path + sample_row["ZuordnungsID"] + ".pdf"

                ## Prepare output location
                out_path = "./sample/" + str(row["Jahr"]) + "/" + school + "/"
                os.makedirs(out_path, exist_ok = True)
                out_path = out_path + sample_row["ZuordnungsID"] + ".pdf"

                ## Copy PDF files
                shutil.copyfile(in_path, out_path)

                ## Mark sample rows in original CSV file.
                csv_texts.loc[
                    (csv_texts.ZuordnungsID == sample_row['ZuordnungsID']),
                    "Zufall"
                ] = 1

    csv_texts.to_csv(outfile_base_directory + "Postulat2022_sampled.csv", index = False, sep = ";")


if __name__ == '__main__':
    cmd_arg = sys.argv[1]

    if cmd_arg == "prepare_csv":
        nrows = sys.argv[2]
        prepare_csv(nrows)

    if cmd_arg == "crop_pdfs":
        crop_pdfs()

    if cmd_arg == "sample":
        choose_sample()

    if cmd_arg == "ocr":
        print("Not implemendet yet.")

    if cmd_arg == "help":
        help_message = """
        InstructionalVISION commands:

        prepare_csv: Generate an empty CSV file with randomly generated IDs
        and prepared column names. Second argument sets number of rows to create.

        crop_pdfs: Crop and rename scanned PDF files (DinA3 scans with two pages).

        sample: Randomly choose sample of PDF files and mark them in CSV file.

        ocr: *Not implemendet yet*

        help: Print this help message.
        """
        print(help_message)
