import requests
import config
import time
import argparse
import os
import io

from lib.common import logger

grobid_address = config.grobid['host']
grobid_path = config.grobid['path']
grobid_port = config.grobid['port']

UPLOAD_FOLDER = config.UPLOAD_FOLDER


def grobid(file_name, grobid_address, grobid_path, grobid_port):
    with open(file_name, "rb") as f:
        data = io.BytesIO(f.read())

    payload = {'input': data}
    data = {'consolidateHeader': '0',
            'consolidateCitations': '0'
            }

    try:
        endpoint = "http://{0}:{1}/api/processFulltextDocument".format(
            grobid_address,
            grobid_port
        )
        response = requests.post(endpoint,
                                 files=payload,
                                 data=data,
                                 timeout=1200)
        status_code = response.status_code

        if status_code == 503:
            time.sleep(1)
            return grobid(file_name, grobid_address, grobid_path, grobid_port)

        if status_code != 200:
            raise Exception("""
                            GROBID could not process document,
                            returned status code %r
                            """ % status_code)

        working_xml = response.content.decode("utf-8")
        return working_xml
    except requests.exceptions.ConnectionError as e:
        logger("GROBID connection error. Is it running?")
        raise e


def write_output(filename, data):
    xml_filename = filename + ".xml"
    with open(xml_filename, 'w') as f:
        f.write(data)


def process(filename, job_id):
    filename = str(filename)
    logger(f"Extracting text from {filename}.")
    try:
        xml = grobid(filename, grobid_address, grobid_path, grobid_port)
        write_output(filename, xml)
        return True
    except Exception as e:
        logger(f"Error processing file. Skipping. {str(e)}")
        return False
