import os
import requests
import click


def download_python_file(river_def, step_content, session, code_dir):
    # Get the actual path from project.yaml
    if not os.path.isdir(code_dir):
        click.secho("Provided path is not a valid directory, please "
                    "change your project.yaml configuration with a valid folder",
                    err=True, fg='red')
        return

    river_id = river_def.get("_id")
    click.echo(f'Downloading python script for river: {river_id}',
               nl=True)
    file_id = step_content.get('file_cross_id')
    file_url_response = session.download_file(file_id)
    file_url = file_url_response.content

    # Download the actual file
    downloaded_file = requests.get(file_url)

    if not code_dir.endswith('/'):
        code_dir += '/'

    full_file_path = f'{code_dir}{river_id}.{file_id}.py'
    with open(full_file_path, "wb") as file:
        file.write(downloaded_file.content)