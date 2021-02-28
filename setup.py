from setuptools import setup, find_packages

setup(
    name='rivery-cli',
    version='0.1',
include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    py_modules=[
        'rivery_cli'
    ],
    install_requires=[
        'Click',
        "requests",
        "PyYaml",
        "pymongo",
        "jsonschema",
        "jsonschema_extended"
    ],
    entry_points="""
        [console_scripts]
        rivery=rivery_cli.base:cli
    """
)
