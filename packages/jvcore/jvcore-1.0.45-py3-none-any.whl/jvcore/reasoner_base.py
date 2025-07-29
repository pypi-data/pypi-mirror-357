from abc import ABC, abstractmethod
from enum import Enum
from typing import TypedDict
from jsonschema import validate

class ActionType(Enum):
    Command = 'Command'
    Query = 'Query'

class ActionParameters(TypedDict):
    actionType: ActionType
    actionName: str
    parameters: dict[str,any]

class ParameterDescription(TypedDict):
    description: str
    type: str | dict[str, 'ParameterDescription']

class ActionDescription(TypedDict):
    actionType: ActionType
    description: str
    parameters: dict[str, ParameterDescription]
    
class Reasoner(ABC):
    @abstractmethod
    def selectSkill(self, commandsAndQueries: dict[str, ActionDescription], utterance: str) -> ActionParameters | None:
        '''Selects requested skill/query based on utterance and list of available skills/queries.'''
        pass

class ReasonerResponseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

responseSchema = {
    'type': 'object',
    'properties': {
        'actionType': {
            'type': 'string', 
            'pattern': '^(Command|Query)$'
        },
        'actionName': {
            'type': 'number'
        },
        'parameters': {
            'type': 'object',
            'additionalProperties': True
        }
    },
    'required': ['actionType', 'actionName', 'parameters']
}