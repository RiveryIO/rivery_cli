import logging
import os

import click
import requests

from rivery_cli.rivery_session import RiverySession


def download_python_file(file_id: str, rivery_session: RiverySession, code_dir: str):
    # Get the actual path from project.yaml
    if not os.path.isdir(code_dir):
        click.secho("Provided path is not a valid directory, please "
                    "change your project.yaml configuration with a valid folder",
                    err=True, fg='red')
        return

    click.echo(f'Downloading python script: {file_id}', nl=True)
    try:
        file_url_response = rivery_session.download_file_by_file_id(file_id)
        file_url = file_url_response.content

        # Download the actual file
        downloaded_file = requests.get(file_url)

        if not code_dir.endswith('/'):
            code_dir += '/'

        full_file_path = f'{code_dir}/{file_id}.py'
        with open(full_file_path, "wb") as file:
            file.write(downloaded_file.content)
    except Exception as e:
        raise click.ClickException(f'Failed to download python script: {file_id} '
                                   f'to local path: {code_dir}. Error: {e}')


def upload_python_file(python_file_name: str, rivery_session: RiverySession, code_dir: str) -> str:
    response = rivery_session.get_file_presignedf_url(python_file_name)
    presigned_url = response.get('presigned_url')
    if not presigned_url:
        raise click.ClickException("Internal error. Please contact support.")

    full_file_path = os.path.join(code_dir, python_file_name)
    if not os.path.isfile(full_file_path) or not python_file_name.endswith(".py"):
        click.secho(f"Provided python script path: {full_file_path} is not a valid python file."
                    f"Please fix the path and try again.",
                    err=True, fg='red')
        return

    logging.debug(f"Uploading file: {full_file_path} to URL: {presigned_url}")
    try:
        file = open(full_file_path, 'rb').read()
        requests.put(presigned_url, files={python_file_name: file})
    except Exception as e:
        raise click.ClickException(f"Internal error while uploading python script. Please contact support. Error: {e}")

    cross_id = response.get('cross_id')
    return cross_id
