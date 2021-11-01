import logging
import os

import requests

from rivery_cli.rivery_session import RiverySession


def download_python_file(file_id: str, rivery_session: RiverySession, code_dir: str, file_name: str):
    # Get the actual path from project.yaml
    if not os.path.isdir(code_dir):
        raise Exception("Provided path is not a valid directory, please "
                        "change your project.yaml configuration with a valid folder")

    logging.debug(f'Downloading python script: {file_name}')
    try:
        file_url_response = rivery_session.download_file_by_file_id(file_id)
        file_url = file_url_response.content

        # Download the actual file
        downloaded_file = requests.get(file_url)

        if not code_dir.endswith('/'):
            code_dir += '/'

        full_file_path = f'{code_dir}/{file_name}'
        with open(full_file_path, "wb") as file:
            file.write(downloaded_file.content)
    except Exception as e:
        raise Exception(f'Failed to download python script: {file_name} '
                        f'to local path: {code_dir}. Error: {e}')


def verify_and_get_file_path_to_upload(python_file_name: str, code_dir: str) -> str:
    full_file_path = os.path.join(code_dir, python_file_name)
    if not os.path.isfile(full_file_path) or not python_file_name.endswith(".py"):
        raise Exception(f"Provided python script path: {full_file_path} is not a valid python file."
                        "Please fix the path and try again.")
    return full_file_path
