from setuptools import setup, find_packages
from os import path
from rivery_cli import __version__

with open('requirements.txt', 'r') as req:
    install_requires = req.readlines()

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='rivery-cli',
    author='Rivery',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=__version__,
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    py_modules=[
        'rivery_cli'
    ],
    install_requires=install_requires,
    entry_points="""
        [console_scripts]
        rivery=rivery_cli.cli.base:cli
    """
)
