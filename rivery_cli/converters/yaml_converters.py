import yaml
from rivery_cli.globals import global_keys
import pathlib
import os
from jsonschema_extended import validate, exceptions
from rivery_cli.converters import RiverConverter


class YamlConverterBase(object):
    converters = {
        "river": RiverConverter,
    }

    def __init__(self, yaml_path=None):
        """ Base class for every yaml converters"""
        if not yaml_path:
            raise ValueError('Missing: yaml path.')
        self.path = pathlib.Path(yaml_path)
        self.content = {}
        self.converter = None

    def create_converter(self):
        if not self.content:
            self.read_yaml()
        converter_cls = self.converters.get(self.entity_type)
        self.converter = converter_cls(**self.content).get_converter()

        return self.converter

    def make_absolute(self, path):
        """ Make an absolute path of the yaml definition """
        if not pathlib.Path(path).is_absolute():
            return pathlib.Path(self.path.parent, path).absolute()

    def read_yaml(self):
        """ Reading the yaml contnet, and populate the definition object """
        try:
            with open(self.path, 'r') as yml_f:
                content = yaml.safe_load(yml_f) or {}
            self.content = content.get(global_keys.YAML_BASE_KEY, {})
            if not self.content:
                raise KeyError('Invalid or empty Yaml provided.')
        except FileNotFoundError as e:
            raise FileExistsError('Yaml file does not exist')

    def make_convert(self):
        """ Convert the read yaml into a json definition that can be sent to the API"""
        if not self.content:
            self.read_yaml()
            # self.validate()

        self.create_converter()

        if self.converter:
            return self.converter.convert()
        else:
            raise ValueError('{} type is not supported'.format(self.entity_type))

    def validate(self):
        """ validate the gotten yaml(s) by the conevertor"""
        if not self.content:
            self.read_yaml()

        converter = self.converters.get(self.entity_type)
        with open(os.path.join(pathlib.Path(__file__).parent.absolute(),
                               converter.validation_schema_path), 'r') as sch:
            schema_ = yaml.load(sch)

        try:
            # Validate json schema
            return validate(self.definition, schema=schema_)
        except exceptions.ValidationError as e:
            raise exceptions.ValidationError(
                message=f'Definition Validation Error for entity {self.entity_type}: {str(e)}')

    def run(self):
        """ Run the process - read the yaml, make valuidation and run the convert """
        if not self.content:
            self.read_yaml()
            # print(self.validate())
        return self.make_convert()

    @property
    def entity_type(self):
        if not self.content.get(global_keys.ENTITY_TYPE):
            raise KeyError(f'Key not provided in {self.path}: type')
        return self.content.get(global_keys.ENTITY_TYPE)

    @property
    def definition(self):
        if not self.content.get(global_keys.DEFINITION):
            raise KeyError(f'Definition not provided for {self.entity_type}. Entity path: {self.path}')
        return self.content.get(global_keys.DEFINITION)

    def __repr__(self):
        return f"<YamlConverter path: {self.path}>"

    def __str__(self):
        return f"<YamlConverter path: {self.path}>"

