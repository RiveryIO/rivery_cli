import uuid
from rivery.entities.rivers import *
from rivery_cli.globals import global_keys, global_settings


class RiverConverter(object):
    """
    River yaml converter.
    convert the river from the

    """

    def __init__(self, content):
        self.content = content
        self.definition = self.content.get(global_keys.DEFINITION)

        self.cross_id = self.content.get('cross_id') or None
        self._id = self.content.get('cross_id') or None

        self.river_full_definition = {
            global_keys.RIVER_DEF : {
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


class LogicConverter(RiverConverter):
    """ Converting Logic yaml definition into a """
    validation_schema_path = '../schemas/rivers/logic.yaml'

    valid_steps = ['container', 'step']

    step_types = {
        "container": LogicContainer,
        "action": ActionStep,
        "river": RiverStep,
        "sql": SQLStep
    }

    task_type_id = "logic"
    datasource_id = "logic"

    def __init__(self, **kwargs):
        super(LogicConverter, self).__init__(**kwargs)
        self.vars = {}

    def valid_step(self, step_type):
        """ Check validation on step"""
        if step_type not in self.step_types:
            raise ValueError(f'Step {step_type} is not compatible in logic rivers')

    def steps_converter(self, steps: list):
        """
        converting yaml steps to the right calsses in cli sdk.
        :param steps: A list of yaml definition of steps. Validated by the self.validation_schema_path
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

                current_step[global_keys.STEP_NAME] = step.get('step_name') or step.get('name')
                current_step[global_keys.IS_ENABLED] = step.get('is_enabled') or step.get('isEnabled')
                current_step[global_keys.IS_PARALLEL] = step.get('is_parallel') or \
                                                        step.get('isParallel') or step.get('parallel')

                current_step[global_keys.NODES] = self.steps_converter(
                    steps=container_steps
                )
                #
                # TypeClass = self.step_types.get(type_)
                # all_steps.append(TypeClass(
                #     steps=self.steps_converter(steps=container_steps),
                #     name=step.get('step_name') or step.get('name'),
                #     is_parallel=step.get('is_parallel') or step.get('isParallel') or step.get('parallel'),
                #     is_enabled=step.get('is_enabled') or step.get('isEnabled'),
                # ))

                all_steps.append(current_step)

            elif type_ == 'step':
                # This is "low level" step. Means, it is not container in any kind.
                primary_type = step.pop('block_primary_type', 'sql')
                current_step[global_keys.BLOCK_PRIMARY_TYPE] = primary_type
                current_step[global_keys.BLOCK_TYPE] = primary_type

                # Import the right primary type from the self.step_types above. Use it as TypeClass after that, by
                # passing the right parameters with **kwargs
                # TypeClass = self.step_types.get(step_primary_type)
                # if step.get('variable_name'):
                #     var_cls = self.vars.get(step.get('variable_name'))
                #     if not var_cls:
                #         raise ValueError(f'Variable {step.get("variable_name")} '
                #                          f'is not defined in the global logic variables. '
                #                          'Please define it first.')
                #     step['variable'] = var_cls

                if primary_type == 'sql':
                    # If sql query is is reference, read the reference path
                    if isinstance(step.get('sql_query'), dict) and step.get('sql_query', {}).get('$ref'):
                        query_ref = step.pop('sql_query')
                        with open(query_ref.get('$ref'), 'r') as sql_f:
                            step['sql_query'] = sql_f.read()
                    # if isinstance(step.get('fields'), dict) and step.get('fields', {}).get('$entity'):
                    #
                # Make the step is enabled mandatory, and use the default of True if not exists
                step['is_enabled'] = step.get('is_enabled') or True
                step['step_name'] = step.get('step_name') or 'Step {}'.format(uuid.uuid4().hex[:4])
                # Create step type class
                all_steps.append(
                    **step
                )

        return all_steps

    def convert(self):
        """Get a river payload in dictionary, convert it to river definition dict """
        self.river_full_definition[global_keys.TASKS_DEF] = [{
            global_keys.TASK_TYPE_ID: self.task_type_id,
            global_keys.TASK_CONFIG: {},
            global_keys.SCHEDULING: self.definition.get(global_keys.SCHEDULING) or {"isEnabled": False}
        }]

        for prop in self.properties:
            assert prop.get('steps', []), 'Every logic river must have at least one step.'
            variables = prop.get('variables', [])
            steps = self.steps_converter(prop.get('steps', []))
            self.river_full_definition[global_keys.TASKS_DEF][0][global_keys.TASK_CONFIG].update(
                {"logic_steps": steps,
                 "datasource_id": self.datasource_id,
                 "fz_batched": False,
                 "variables": variables}
            )

        return self.river_full_definition

        # cls_ = Logic(
        #     entity_name=self.entity_id,
        #     name=self.river_name,
        #     description=self.description,
        #     steps=self.steps_converter(self.properties.get('steps', [])),
        #     cross_id=self.cross_id,
        #     _id=self._id
        # )
        #
        # return cls_.to_api_ref()
        #
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
            global_keys.SCHEDULING: {}
        }

        # Get the river definitions from the def_
        river_definition = def_.get(global_keys.RIVER_DEF, {})

        # Populate IDS, and globals from the river
        definition_.update({
            "name": river_definition.get(global_keys.RIVER_NAME),
            "description": river_definition.get(global_keys.RIVER_DESCRIPTION) or 'Imported by Rivery CLI',
            global_keys.ENTITY_TYPE: river_definition.get('river_type')
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
                definition_[global_keys.SCHEDULING] = {"cronExp": task.get(global_keys.SCHEDULING, {}).get("cronExp"),
                                                       "isEnabled": task.get(global_keys.SCHEDULING, {}).get(
                                                           'isEnabled'),
                                                       "startDate": task.get(global_keys.SCHEDULING, {}).get(
                                                           'startDate'),
                                                       "endDate": task.get(global_keys.SCHEDULING, {}).get('endDate')}

        final_response[global_keys.BASE][global_keys.DEFINITION] = definition_

        return final_response
