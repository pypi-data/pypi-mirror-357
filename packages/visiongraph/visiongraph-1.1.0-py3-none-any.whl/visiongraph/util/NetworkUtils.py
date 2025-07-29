import logging
import os
import shutil
import sys
from typing import Any, Dict, Optional
from typing import Tuple

import requests
from tqdm import tqdm

import visiongraph.cache

HF_READ_ONLY_TOKEN = os.getenv("HF_TOKEN", "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")

# This is a read-only access token to the visiongraph repository on huggingface (https://huggingface.co/cansik/visiongraph/)
PUBLIC_DATA_HEADERS = {
    "Authorization": f"Bearer {HF_READ_ONLY_TOKEN}"
}

PUBLIC_DATA_URL = "https://huggingface.co/cansik/visiongraph/resolve/main/"


def handle_redirects(url: str, headers: Optional[Dict[str, Any]] = None) -> str:
    """
    Handles HTTP redirects manually to ensure headers are preserved.

    :param url: The initial URL to request.
    :param headers: Optional headers to include in the requests.
    :return: The final resolved URL after following redirects.
    """
    while True:
        response = requests.head(url, headers=headers, allow_redirects=False)
        if response.status_code in [301, 302, 303, 307, 308]:
            url = response.headers['Location']
        else:
            break
    return url


def download_file(url: str, path: str,
                  description: str = "download",
                  with_progress: bool = True,
                  headers: Optional[Dict[str, Any]] = None):
    """
    Downloads a file from the specified URL and saves it to the given path.

    :param url: The URL to download the file from.
    :param path: The local path where the file will be saved.
    :param description: A description for the download progress. Defaults to "download".
    :param with_progress: Indicates whether to show a progress bar. Defaults to True.
    :param headers: Optional header variable for authentication.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Resolve any redirects to ensure the final URL is used
    resolved_url = handle_redirects(url, headers)

    if not with_progress:
        with tqdm(total=1, desc=description) as pb:
            response = requests.get(resolved_url, headers=headers, stream=True)

            with open(path, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            pb.update()
        return

    # Perform a HEAD request to get the file size (if available)
    head_request = requests.head(resolved_url, headers=headers)

    if "Content-Length" in head_request.headers:
        filesize = int(head_request.headers["Content-Length"])
    else:
        filesize = 0

    dl_path = path
    chunk_size = 1024

    with requests.get(resolved_url, headers=headers, stream=True) as r, open(dl_path, "wb") as f, tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=filesize,
            file=sys.stdout,
            desc=description
    ) as progress:
        for chunk in r.iter_content(chunk_size=chunk_size):
            datasize = f.write(chunk)
            progress.update(datasize)


def prepare_openvino_model(model_name, url: str = None) -> Tuple[str, str]:
    """
    Prepares the OpenVINO model files by downloading the model and weights.

    :param model_name: The name of the model.
    :param url: Optional URL for downloading the model files. If None, defaults to the public data URL.

    :return: A tuple containing the paths to the model XML and weights BIN files.
    """
    model_path = prepare_data_file(f"{model_name}.xml", url)
    weights_path = prepare_data_file(f"{model_name}.bin", url)
    return model_path, weights_path


def prepare_data_file(file_name: str,
                      url: Optional[str] = None,
                      headers: Optional[Dict[str, Any]] = None) -> str:
    """
    Prepares a data file by downloading it if it does not already exist.

    :param file_name: The name of the file to prepare.
    :param url: Optional URL for downloading the file. If None, defaults to the public data URL.
    :param headers: Optional header variable for authentication.

    :return: The path to the prepared data file.
    """
    if url is None:
        url = f"{PUBLIC_DATA_URL}{file_name}"

    data_path = os.path.abspath(os.path.dirname(visiongraph.cache.__file__))
    if hasattr(sys, "_MEIPASS"):
        data_path = "./cache"

    file_path = os.path.join(data_path, file_name)

    os.makedirs(data_path, exist_ok=True)

    if os.path.exists(file_path):
        return file_path

    temp_file = os.path.join(data_path, f"{file_name}.tmp")

    if os.path.exists(temp_file):
        os.remove(temp_file)

    try:
        download_file(url, temp_file, f"Downloading {file_name}", headers=headers)
    except Exception as ex:
        logging.warning(f"Retry download because {file_name} could not be download: {ex}")
        download_file(url, temp_file, f"Downloading {file_name}", with_progress=False, headers=headers)

    # check if file has been downloaded correctly
    head = ""
    try:
        with open(temp_file, 'rb') as f:
            head = f.read(9).decode()
    except Exception as ex:
        logging.debug(ex)

    if head == "Not Found":
        raise Exception(f"Could not find file in repository: {file_name}")

    os.rename(temp_file, file_path)
    return file_path
