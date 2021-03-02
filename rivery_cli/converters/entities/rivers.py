from bson import ObjectId
import uuid
from rivery.entities.rivers import *


class RiverConverter(object):

    def __init__(self, **kwargs):
        self.definition = kwargs.get('definition')
        self.type = self.definition.get('type')

    def get_converter(self):
        """ Getting the converter class """
        converter_class = self.make_type_cls(type_=self.type)
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
        type_ = self.type
        return type_

    @property
    def river_name(self):
        return self.definition.get('name')

    @property
    def entity_id(self):
        return self.definition.get('entity_id') or uuid.uuid4().hex

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

    def __init__(self, **kwargs):
        super(LogicConverter, self).__init__(type='logic',
                                             definition=kwargs)
        self.vars = {}

    def steps_converter(self, steps: list):
        """
        converting yaml steps to the right calsses in rivery sdk.
        :param steps: A list of yaml definition of steps. Validated by the self.validation_schema_path
        """
        all_steps = []
        for step in steps:
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
                TypeClass = self.step_types.get(type_)
                all_steps.append(TypeClass(
                    steps=self.steps_converter(steps=container_steps),
                    name=step.get('step_name') or step.get('name'),
                    is_parallel=step.get('is_parallel') or step.get('isParallel') or step.get('parallel'),
                    is_enabled=step.get('is_enabled') or step.get('isEnabled'),

                ))

            elif type_ == 'step':
                # This is "low level" step. Means, it is not container in any kind.
                step_primary_type = step.get('block_primary_type', 'sql')
                # Import the right primary type from the self.step_types above. Use it as TypeClass after that, by
                # passing the right parameters with **kwargs
                TypeClass = self.step_types.get(step_primary_type)
                if step.get('variable_name'):
                    var_cls = self.vars.get(step.get('variable_name'))
                    if not var_cls:
                        raise ValueError(f'Variable {step.get("variable_name")} '
                                         f'is not defined in the global logic variables. '
                                         'Please define it first.')
                    step['variable'] = var_cls

                if step.get('block_primary_type') == 'sql':
                    # If sql query is is reference, read the reference path
                    if isinstance(step.get('sql_query'), dict) and step.get('sql_query', {}).get('$ref'):
                        query_ref = step.pop('sql_query')
                        with open(query_ref.get('$ref'), 'r') as sql_f:
                            step['sql_query'] = sql_f.read()
                # Make the step is enabled mandatory, and use the default of True if not exists
                step['is_enabled'] = step.get('is_enabled') or True
                # Create step type class
                all_steps.append(TypeClass(
                    step_name=step.get('step_name') or 'Step {}'.format(uuid.uuid4().hex[:4]),
                    **step
                ))

        return all_steps

    def convert(self):
        """Get a river payload in dictionary, convert it to river definition dict """
        cls_ = Logic(
            entity_name=self.entity_id,
            name=self.river_name,
            description=self.description,
            steps=self.steps_converter(self.properties.get('steps', []))
        )

        return cls_
