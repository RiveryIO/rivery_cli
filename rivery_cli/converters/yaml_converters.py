import yaml
from rivery_cli.globals import global_keys
import pathlib
from rivery_cli.utils import yaml_loaders
from bson import ObjectId
import simplejson as json
import datetime
import yaql


class YamlConverterBase(object):
    """ Yaml reader Base for entities in Rivery CLI"""

    def __init__(self, path):
        """ Base class for every yaml converters"""
        self.content = {}
        self.path = pathlib.Path(str(path))
        self.converter = None
        self.full_yaml = {}

        self.loader = yaml_loaders.get_loader()

        # Read the yaml file into the memory,
        # Raising error if the file isn't found
        self.read_yaml()

    def read_yaml(self):
        """ Reading the yaml contnet, and populate the definition object """
        try:
            with open(self.path, 'r') as yml_f:
                self.full_yaml = yaml.load(yml_f, Loader=self.loader) or {}
            if self.full_yaml:
                self.content = json.loads(json.dumps(
                    self.full_yaml.get(global_keys.YAML_BASE_KEY, {}), default=self.obj_default))
            if not self.content:
                raise KeyError(f'Invalid or empty Yaml provided in path: {self.path}')
            return self.content
        except FileNotFoundError as e:
            raise FileExistsError('Yaml file does not exist')

    @staticmethod
    def obj_default(val):
        """ Object hook after reading the yaml -
         parse some specifications + special objects (like ObjectId) on the self.content using object hook and
         remove not relevant keys
        """
        if isinstance(val, ObjectId):
            return str(val)
        if isinstance(val, datetime.datetime):
            return int(val.timestamp())

    # def validate(self):
    #     """ validate the gotten yaml(s) by the conevertor"""
    #     if not self.content:
    #         self.read_yaml()
    #
    #     converter = self.converters.get(self.entity_type)
    #     with open(os.path.join(pathlib.Path(__file__).parent.absolute(),
    #                            converter.validation_schema_path), 'r') as sch:
    #         schema_ = yaml.load(sch)
    #
    #     try:
    #         # Validate json schema
    #         return validate(self.definition, schema=schema_)
    #     except exceptions.ValidationError as e:
    #         raise exceptions.ValidationError(
    #             message=f'Definition Validation Error for entity {self.entity_type}: {str(e)}')

    @staticmethod
    def write_yaml(path, content, **dumpskw):
        """ Write a yaml by path and content """
        try:
            # Write yaml safe - mean that if the dump doesn't works
            yaml_data = yaml.safe_dump(content, **dumpskw)
            with open(path, 'w') as yml_:
                yml_.write(yaml_data)

        except Exception as e:
            raise IOError(f'Problem on writing into yaml file in {path}. Error: {str(e)}')

    @property
    def entity_type(self):
        return self.content.get(global_keys.ENTITY_TYPE) or 'river'

    @property
    def definition(self):
        if not self.content.get(global_keys.DEFINITION):
            raise KeyError(f'Definition not provided for {self.entity_type}. Entity path: {self.path}')
        return self.content.get(global_keys.DEFINITION, {})

    @property
    def entity_name(self):
        if not self.content.get(global_keys.ENTITY_NAME):
            raise KeyError(f'Missing Entity Name for entity definition in {self.path}')
        return self.content.get(global_keys.ENTITY_NAME)

    def __repr__(self):
        return f"<YamlConverter EntityName: {self.entity_name}>"

    def __str__(self):
        return f"<YamlConverter EntityName: {self.entity_name}>"

