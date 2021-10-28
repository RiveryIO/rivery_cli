import os
import requests
import click


def download_python_file(step_content, session, code_dir):
    # Get the actual path from project.yaml
    if not os.path.isdir(code_dir):
        click.secho("Provided path is not a valid directory, please "
                    "change your project.yaml configuration with a valid folder",
                    err=True, fg='red')
        return
    file_id = step_content.get('file_cross_id')

    click.echo(f'Downloading python script: {file_id}',
               nl=True)
    try:
        file_url_response = session.download_file_by_file_id(file_id)
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
