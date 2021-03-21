import uuid
from rivery_cli.globals import global_keys, global_settings
from copy import deepcopy
import bson
import simplejson as json


class RiverConverter(object):
    """
    River yaml converter.
    convert the river from the

    """

    def __init__(self, content):
        self.content = content
        self.definition = self.content.get(global_keys.DEFINITION)

        self.river_full_definition = {
            global_keys.RIVER_DEF: {
                global_keys.SHARED_PARAMS: {

                },
                global_keys.RIVER_NAME: self.river_name,
                global_keys.RIVER_TYPE: self.river_type,
                global_keys.RIVER_DESCRIPTION: self.description,
                global_keys.IS_SCHEDULED: False,
                global_keys.SOURCE_TYPE: self.river_type
            },
            global_keys.TASKS_DEF: [{
                global_keys.TASK_CONFIG: {},
                global_keys.TASK_TYPE_ID: self.river_type
            }],
            global_keys.CROSS_ID: "",
        }

        self.notification_events = [
            "on_error", "on_warning"
        ]

    def get_sub_converter(self):
        """ Getting the converter class """
        converter_class = self.make_type_cls(type_=self.river_type)
        return converter_class(**self.definition)

    @classmethod
    def make_type_cls(cls, type_: str):
        """
        Initiate the river type class by the definition river type. Gets a self.river_type
        and make the initiation.
        """
        for _cls_ in cls.__subclasses__():
            if _cls_.__name__ == f'{type_.title()}Converter':
                return _cls_

    @property
    def river_type(self):
        """ Property of the river type read"""
        type_ = self.definition.get('type')
        return type_

    @property
    def river_name(self):
        return self.definition.get('name')

    @property
    def entity_id(self):
        return self.content.get('entity_name')

    @property
    def description(self):
        return self.definition.get('description') or ''

    @property
    def properties(self):
        return self.definition.get('properties') or {}

    @property
    def cross_id(self):
        return self.content.get('cross_id')

    @property
    def id(self):
        return self.content.get('cross_id')


class LogicConverter(RiverConverter):
    """ Converting Logic yaml definition into a """
    validation_schema_path = '../schemas/river/logic.yaml'

    valid_steps = {'container', 'step'}

    step_types = {"container", "action", "river", "sql"}

    task_type_id = "logic"
    datasource_id = "logic"

    step_bson_converter = ['river_id', 'action_id', 'gConnection',"connection_id", "fzConnection"]

    def __init__(self, **kwargs):
        super(LogicConverter, self).__init__(**kwargs)
        self.vars = {}

    def bson_converter(self, dct):
        """ Convert specific keys to objectId"""
        newdct = {}
        for k, v  in dct.items():
            if k in self.step_bson_converter and v:
                newdct[k] = bson.ObjectId(v)
            else:
                newdct[k] = v
        return newdct

    def valid_step(self, step_type):
        """ Check validation on step"""
        if step_type not in self.step_types:
            raise ValueError(f'Step {step_type} is not compatible in logic rivers')

    def steps_converter(self, steps: list) -> list:
        """
        converting yaml steps to the right API definition of the steps.
        :param steps: A list of yaml definition of steps.
                      Validated by the self.validation_schema_path
        """
        all_steps = []

        for step in steps:
            # Init the current step
            current_step = {}

            # Get the type of every step, and check if it's valid or not.
            type_ = step.pop('type', 'step') or 'step'
            assert type_ in self.valid_steps, \
                f'Invalid step type: {type_}. Valid types: {",".join(self.valid_steps)}'

            if type_ == 'container':
                # Pop the steps definitions from the container, in order to use it in the container class
                container_steps = step.pop('steps', [])
                # This is a container. Make the LogicContainer class initiation,
                # and use the steps converter
                assert container_steps, 'Container must include at least one step'

                current_step[global_keys.CONTAINER_RUNNING] = step.pop(global_keys.CONTAINER_RUNNING, 'run_once')
                current_step.update(step)
                current_step[global_keys.STEP_NAME] = step.get('step_name') or step.get('name')
                current_step[global_keys.IS_ENABLED] = step.get('is_enabled') or step.get('isEnabled')
                current_step[global_keys.IS_PARALLEL] = step.get('is_parallel') or \
                                                        step.get('isParallel') or step.get('parallel')

                current_step[global_keys.NODES] = self.steps_converter(
                    steps=container_steps
                )

                all_steps.append(current_step)

            elif type_ == 'step':
                # This is "low level" step. Means, it is not container in any kind.
                content = {}
                primary_type = step.pop('block_primary_type', 'sql')
                block_db_type = step.pop('block_db_type', primary_type)
                content[global_keys.BLOCK_PRIMARY_TYPE] = primary_type
                content[global_keys.BLOCK_TYPE] = block_db_type
                content[global_keys.BLOCK_DB_TYPE] = block_db_type

                # Make the step is enabled mandatory, and use the default of True if not exists
                current_step[global_keys.IS_ENABLED] = step.pop('is_enabled', True) or True
                current_step[global_keys.STEP_NAME] = step.pop('step_name', 'Step {}'.format(uuid.uuid4().hex[:4]))
                current_step[global_keys.CONTAINER_RUNNING] = 'run_once'

                if step.get('connection_id') or step.get('gConnection'):
                    content['gConnection'] = step.pop('connection_id') or step.pop('gConnection')

                if step.get(global_keys.TARGET_TYPE) == global_keys.VARIABLE and step.get(global_keys.VARIABLE):
                    if not step.get(global_keys.VARIABLE) in self.vars:
                        # The target variable doesn't exist under the vars list of the logic.
                        # Raise an error about that.
                        raise KeyError(f"Step target type is variable, "
                                       f"but the target variable doesn't exist in the logic definition. "
                                       f"Please set the variable under `variables` key in the logic entity definition."
                                       )
                content.update(step)

                current_step[global_keys.CONTNET] = content
                current_step[global_keys.NODES] = []

                all_steps.append(current_step)

        return all_steps

    def convert(self) -> dict:
        """Get a river payload in dictionary, convert it to river definition dict """

        # Make the global definitions under the river def
        self.river_full_definition[global_keys.CROSS_ID] = self.cross_id
        if self.definition.get(global_keys.SCHEDULING, {}).get('isEnabled'):
            self.river_full_definition[global_keys.RIVER_DEF][global_keys.IS_SCHEDULED] = True

        self.river_full_definition[global_keys.RIVER_DEF][
            global_keys.SHARED_PARAMS][global_keys.NOTIFICATIONS] = self.definition.get(global_keys.NOTIFICATIONS, {})

        # Make the basic river task definition on config
        # Logic has only 1 task under the task definition
        self.river_full_definition[global_keys.TASKS_DEF] = [
            {
                global_keys.TASK_TYPE_ID: self.task_type_id,
                global_keys.TASK_CONFIG: {},
                global_keys.SCHEDULING: self.definition.get(
                    global_keys.SCHEDULING) or {"isEnabled": False},
                global_keys.RIVER_ID: self.cross_id
            }
        ]

        # Run over the properties and then make some validations + conversion to the API river definition.
        # Check if there's a "steps" key under the properties
        # TODO: move to parameters validator or another validator class.
        assert self.properties.get(global_keys.STEPS, []), 'Every logic river must have at least one step.'
        # Populate the variables key
        self.vars = self.properties.get('variables', {})
        # Convert the steps to river definitions
        steps = self.steps_converter(self.properties.get('steps', []))

        # steps = json.loads(json.dumps(steps), object_hook=self.bson_converter)

        # Make the full definition of the logic under the tasks definitions [0]
        self.river_full_definition[global_keys.TASKS_DEF][0][
            global_keys.TASK_CONFIG].update(
            {"logic_steps": steps,
             "datasource_id": self.datasource_id,
             "fz_batched": False,
             "variables": self.vars}
        )

        self.river_full_definition = json.loads(json.dumps(self.river_full_definition), object_hook=self.bson_converter)

        return self.river_full_definition

    @staticmethod
    def content_loader(content: dict) -> dict:
        """ ObjectHook like to convert the content into more "reliable" content """
        new_content = {}
        primary_type = content.get('block_primary_type')
        new_content['block_primary_type'] = primary_type
        new_content['block_type'] = content.get('block_type')

        if primary_type == 'river':
            new_content['block_primary_type'] = primary_type
            new_content['river_id'] = str(content.get('river_id'))
        else:
            new_content.update(content)
            if new_content.get('connection_id') or new_content.get('gConnection'):
                new_content['connection_id'] = str(content.pop('gConnection', content.get('connection_id')))
                new_content.pop('gConnection', None)
        return new_content

    @classmethod
    def step_importer(cls, steps: list) -> list:
        """ Convert the steps to the right keys in the yaml file """
        # Make the steps list
        all_steps = []
        for step in steps:
            current_step = {}
            current_step["type"] = "step" if step.get('content', []) else "container"
            current_step["isEnabled"] = step.pop("isEnabled", True)
            current_step["step_name"] = step.pop("step_name", "Logic Step")
            if current_step.get('type') == "step":
                # Update the step definition as it exists in the content
                current_step.update(cls.content_loader(step.pop("content", {})))
                if step.get('condition', {}):
                    current_step['condition'] = step.get('condition')
                # In order to "purge" any "Type" key comes from the river
                current_step['type'] = 'step'
            else:
                # Update the CONTAINER definition
                current_step["isParallel"] = step.pop('isParallel', False) or False
                current_step["container_running"] = step.pop("container_running", "run_once")
                current_step["loop_over_value"] = step.pop("loop_over_value", "")
                current_step["loop_over_variable_name"] = step.pop("loop_over_variable_name", [])
                current_step["steps"] = cls.step_importer(
                    steps=step.pop('nodes', [])
                )

            all_steps.append(current_step)

        return all_steps

    @classmethod
    def _import(cls, def_: dict) -> dict:
        """Import a river into a yaml definition """
        # Set the basics dictionary stucture
        final_response = {
            global_keys.BASE: {
                global_keys.ENTITY_NAME: f"river-{str(def_.get(global_keys.CROSS_ID))}",
                global_keys.VERSION: global_settings.__version__,
                global_keys.ENTITY_TYPE: "river",
                global_keys.CROSS_ID: str(def_.get(global_keys.CROSS_ID)),
                global_keys.DEFINITION: {}
            }
        }

        definition_ = {
            global_keys.PROPERTIES: {},
            global_keys.SCHEDULING: {},
            global_keys.NOTIFICATIONS: {}
        }

        # Get the river definitions from the def_
        river_definition = def_.get(global_keys.RIVER_DEF, {})

        # Populate IDS, and globals from the river
        definition_.update({
            "name": river_definition.get(global_keys.RIVER_NAME),
            "description": river_definition.get(global_keys.RIVER_DESCRIPTION) or 'Imported by Rivery CLI',
            global_keys.ENTITY_TYPE: river_definition.get('river_type'),
            global_keys.NOTIFICATIONS: river_definition.get(
                global_keys.SHARED_PARAMS, {}).get(global_keys.NOTIFICATIONS, {})
        })

        # Run on the tasks definitions, and set it out
        tasks_def = def_.get(global_keys.TASKS_DEF, [])
        for task in tasks_def:
            task_config = task.get(global_keys.TASK_CONFIG, {})
            # Run on each task, and set the right keys to the structure
            definition_[global_keys.PROPERTIES]["steps"] = cls.step_importer(
                steps=task_config.get("logic_steps", []))

            # Update the variables for the logic
            definition_[global_keys.PROPERTIES]["variables"] = task_config.get('variables', {})

            if task.get(global_keys.SCHEDULING, {}).get('isEnabled'):
                definition_[global_keys.SCHEDULING] = {"cronExp": task.get(global_keys.SCHEDULING, {}
                                                                           ).get("cronExp", ""),
                                                       "isEnabled": task.get(global_keys.SCHEDULING, {}).get(
                                                           'isEnabled', False),
                                                       "startDate": task.get(global_keys.SCHEDULING, {}).get(
                                                           'startDate', None),
                                                       "endDate": task.get(global_keys.SCHEDULING, {}
                                                                           ).get('endDate', None)}

        final_response[global_keys.BASE][global_keys.DEFINITION] = definition_

        return final_response
