from setuptools import setup, find_packages

with open('requirements.txt', 'r') as req:
    install_requires = req.readlines()

setup(
    name='rivery-cli',
    version='0.1',
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
