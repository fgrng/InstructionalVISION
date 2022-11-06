# Import Libraries
from PyPDF2 import PdfReader, PdfWriter, Transformation
from PyPDF2.generic import NameObject, NumberObject
from copy import copy
import os

def crop_textregions_from(infile_path, essay_source = "", page_size = "", outfile_path = ""):
    """Extracts areas from PDF file, which should contain handwritten essay parts.

    Area extraction is predefined for the following pdf types:
    * To scan the two-sided A3 Scans from Kantonsschule Burggraben:
      page_size = "a3", source = "Postulat2022"
    * To scan the prepared A4 Scans (typically four pages) from Kantonsschule Burggraben:
      page_size = "a4", source = "Postulat2022"
    """
    # Check if predefined crop spectifications exists.
    if not ( page_size in ["a4", "a3"] ):
        raise TypeError("No valid page_size given.")
    if not( essay_source in [
            "Postulat2022"
    ]):
        raise TypeError("Unknown essay_source given.")

    # Select predefined cropping function.
    if ( essay_source == "Postulat2022"):
        _crop_postulat2022(infile_path, page_size, outfile_path)

def crop_metadataregion_from(infile_path, essay_source = "", page_size = "", outfile_path = ""):
    """Extracts area from PDF file, which should contain essay evaluation data.

    Area extraction is predefined for the following pdf types:
    * To scan the two-sided A3 scans from Kantonsschulen in Switzerland:
      page_size = "a3", source = "Postulat2022"
    * To scan prepared A4 scans (typically four pages) from Kantonsschulen:
      page_size = "a4", source = "Postulat2022"
    """
    # Check if predefined crop specifications exists.
    if not ( page_size in ["a4", "a3"] ):
        raise TypeError("No valid page_size given.")
    if not( essay_source in [
            "Postulat2022"
    ]):
        raise TypeError("Unknown essay_source given.")

    # Select predefined cropping function.
    if ( essay_source == "Postulat2022"):
        _meta_postulat2022(infile_path, page_size, outfile_path)

def _meta_postulat2022(infile_path, page_size, outfile_path):
    reader = PdfReader(infile_path)
    writer = PdfWriter()

    if ( page_size == "a3"):
        p1 = copy(reader.pages[0])
        p1.transfer_rotation_to_content()
        # Meta data area
        p1.mediabox.lower_left = (
            float(p1.mediabox.right) * 0.5,
            float(p1.mediabox.top) * 0.5,
        )
        # Add page to pdf.
        writer.add_page(p1)

        os.makedirs(os.path.dirname(outfile_path), exist_ok=True)
        with open(outfile_path, "wb") as outfile:
            writer.write(outfile)

def _crop_postulat2022(infile_path, page_size, outfile_path):
    reader = PdfReader(infile_path)
    writer = PdfWriter()

    if ( page_size == "a3"):
        # First part is on page 1, bottom right;
        # Second part is on page 2, left-hand side;
        # Third part is on page 3, right-hand side;
        # Fourth part is on page 1, left-hand side
        p1 = copy(reader.pages[0])
        p2 = copy(reader.pages[1])
        p3 = copy(reader.pages[1])
        p4 = copy(reader.pages[0])

        # apply VISUAL rotation to actual page content (mediabox, …)
        # sets visual rotation to 0.
        # See: https://pypdf2.readthedocs.io/en/latest/modules/PageObject.html#PyPDF2._page.PageObject.transfer_rotation_to_content
        p1.transfer_rotation_to_content()
        p2.transfer_rotation_to_content()
        p3.transfer_rotation_to_content()
        p4.transfer_rotation_to_content()

        # Firt part
        p1.mediabox.lower_left = (
            float(p1.mediabox.right) * 0.5,
            float(p1.mediabox.bottom),
        )
        p1.mediabox.upper_right = (
            float(p1.mediabox.right),
            float(p1.mediabox.top) * 0.65
        )

        # Second part
        p2.mediabox.upper_right = (
            float(p2.mediabox.right) * 0.5,
            float(p2.mediabox.top),
        )

        # Third part
        p3.mediabox.lower_left = (
            float(p3.mediabox.right) * 0.5,
            float(p3.mediabox.bottom),
        )

        # Fourth part
        p4.mediabox.upper_right = (
            float(p4.mediabox.right) * 0.5,
            float(p4.mediabox.top),
       )

        # Combine new PDF
        writer.add_page(p1)
        writer.add_page(p2)
        writer.add_page(p3)
        writer.add_page(p4)

        os.makedirs(os.path.dirname(outfile_path), exist_ok=True)
        with open(outfile_path, "wb") as outfile:
            writer.write(outfile)

