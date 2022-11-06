import io
import os
import base64
# import tempfile

import logging
from pprint import pformat

# Imports the Google Cloud client library
from google.cloud import vision

from PyPDF2 import PdfReader, PdfWriter

def encode_image_file(image_path):
    with open(image_path, "rb") as f:
        image_content = f.read()
        return base64.b64encode(image_content)


def pdf_to_txt_for(infile_path = "", outfile_path = ""):
    # Force Data Manipulation on EU Servers
    client_options = {"api_endpoint": "eu-vision.googleapis.com"}
    # Instantiates a client
    client = vision.ImageAnnotatorClient(client_options=client_options)

    # Read PDF pages and create requests list
    requests = list()
    mime_type = "application/pdf"
    with io.open(infile_path, "rb") as f:
        content = f.read()
    input_config = {"mime_type": mime_type, "content": content}
    features = [{"type_": vision.Feature.Type.DOCUMENT_TEXT_DETECTION}]
    pages = [1, 2, 3, 4]
    request = {
        "input_config": input_config,
        "features": features,
        "pages": pages
    }
    requests.append(request)


    # Prepare query json.
    query = {"requests": requests}

    # Performs label detection on the image file
    logging.info(f"Detect text in {infile_path}.")
    response = client.batch_annotate_files(requests=requests)
    # logging.info(pformat(response))
    # print(response)

    for image_response in response.responses[0].responses:
        # logging.info(image_response.full_text_annotation.text)
        with io.open(outfile_path, "a") as f:
            f.write(u"{}".format(image_response.full_text_annotation.text))


