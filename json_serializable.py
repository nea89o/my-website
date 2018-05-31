import json
from datetime import datetime
from enum import Enum
from typing import Dict, Type, List


def from_json(data, cls: Type):
    if issubclass(cls, List):
        list_type: Type = cls.__args__[0] if hasattr(cls, '__args__') else type(data[0])
        instance = list()
        for value in data:
            instance.append(from_json(value, list_type))
        return instance
    if issubclass(cls, Dict):
        item = data.copy().popitem() if len(data) > 0 else None
        key_type: Type = cls.__args__[0] if hasattr(cls, '__args__') else type(item[0])
        value_type: Type = cls.__args__[1] if hasattr(cls, '__args__') else type(item[0])
        instance = dict()
        for key, value in data.items():
            instance[from_json(key, key_type)] = from_json(value, value_type)
        return instance
    if issubclass(cls, Enum):
        return getattr(cls, data)
    if issubclass(cls, datetime):
        return datetime.fromtimestamp(data)
    if issubclass(cls, JsonSerializable):
        instance = cls()
        annotations: dict = cls.__annotations__ if hasattr(cls, '__annotations__') else {}
        for key, value in data.items():
            value_type = annotations[key] if key in annotations.keys() else type(value)
            setattr(instance, key, from_json(value, value_type))
        return instance
    return data


def prepare_json(obj):
    if isinstance(obj, JsonSerializable):
        return prepare_json(obj.__dict__)
    if isinstance(obj, Enum):
        return obj.name
    if isinstance(obj, datetime):
        return obj.timestamp()
    if any(isinstance(obj, cls) for cls in [list, set, frozenset]):
        return [prepare_json(data) for data in obj]
    if isinstance(obj, dict):
        return {key: prepare_json(value) for key, value in obj.items()}
    return obj


class JsonSerializable(object):
    @classmethod
    def load(cls, data):
        if isinstance(data, str):
            data = json.loads(data)
        return from_json(data, cls)

    @classmethod
    def load_from_file(cls, filename):
        filename = str(filename)
        with open(filename) as handle:
            return cls.load(handle.read())

    def dump_to_file(self, filename):
        filename = str(filename)
        with open(filename, 'w') as handle:
            handle.write(self.dump())

    def dump(self):
        return json.dumps(prepare_json(self))

    def __repr__(self):
        return self.dump()
