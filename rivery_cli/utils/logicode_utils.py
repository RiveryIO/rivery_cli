import os


def get_file_to_download(file_id: str, code_dir: str, file_name: str):
    if not os.path.isdir(code_dir):
        raise Exception("Provided path is not a valid directory, please "
                        "change your project.yaml configuration with a valid folder")

    if not code_dir.endswith('/'):
        code_dir += '/'

    full_file_path = os.path.join(code_dir, file_name)
    return {file_id: full_file_path}


def verify_and_get_file_path_to_upload(python_file_name: str, code_dir: str) -> str:
    full_file_path = os.path.join(code_dir, python_file_name)
    if not os.path.isfile(full_file_path) or not python_file_name.endswith(".py"):
        raise Exception(f"Provided python script path: {full_file_path} is not a valid python file."
                        "Please fix the path and try again.")
    return full_file_path
