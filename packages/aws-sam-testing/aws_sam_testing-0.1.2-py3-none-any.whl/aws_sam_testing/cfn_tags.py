"""Implements support for CloudFormation's YAML tags.
Does not add these to the "safe" methods by default.
Call the mark_safe() method to add it to these methods.

Copyright 2018 iRobot Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__version__ = "1.1.0"

import itertools
import json
import re

import six
import yaml
from yaml.constructor import ConstructorError


class CloudFormationObject(object):
    SCALAR = "scalar"
    SEQUENCE = "sequence"
    SEQUENCE_OR_SCALAR = "sequence_scalar"
    MAPPING = "mapping"
    MAPPING_OR_SCALAR = "mapping_scalar"

    name = None
    tag = None
    type = None

    def __init__(self, data):
        self.data = data

    def to_json(self):
        """Return the JSON equivalent"""

        def convert(obj):
            return obj.to_json() if isinstance(obj, CloudFormationObject) else obj

        if isinstance(self.data, dict):
            data = {key: convert(value) for key, value in six.iteritems(self.data)}
        elif isinstance(self.data, (list, tuple)):
            data = [convert(value) for value in self.data]
        else:
            data = self.data

        name = self.name

        if name == "Fn::GetAtt" and isinstance(data, six.string_types):
            data = data.split(".")  # type: ignore[union-attr]
        elif name == "Ref" and "." in data:
            name = "Fn::GetAtt"
            data = data.split(".")  # type: ignore[union-attr]

        return {name: data}

    @classmethod
    def construct(cls, loader, node):
        if cls.type == cls.SCALAR:
            return cls(loader.construct_scalar(node))
        elif cls.type == cls.SEQUENCE:
            return cls(loader.construct_sequence(node))
        elif cls.type == cls.SEQUENCE_OR_SCALAR:
            try:
                return cls(loader.construct_sequence(node))
            except ConstructorError:
                return cls(loader.construct_scalar(node))
        elif cls.type == cls.MAPPING:
            return cls(loader.construct_mapping(node))
        elif cls.type == cls.MAPPING_OR_SCALAR:
            try:
                return cls(loader.construct_mapping(node))
            except ConstructorError:
                return cls(loader.construct_scalar(node))
        else:
            raise RuntimeError("Unknown type {}".format(cls.type))

    @classmethod
    def represent(cls, dumper, obj):
        data = obj.data
        if isinstance(data, list):
            return dumper.represent_sequence(obj.tag, data)
        elif isinstance(data, dict):
            return dumper.represent_mapping(obj.tag, data)
        else:
            return dumper.represent_scalar(obj.tag, data)

    def __str__(self):
        return "{} {}".format(self.tag, self.data)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.data))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.data == self.data


class JSONFromYAMLEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, CloudFormationObject):
            return o.to_json()
        return json.JSONEncoder.default(self, o)


# (name, tag, type)

ref = ("Ref", "Ref", CloudFormationObject.SCALAR)

functions = [
    ("Fn::And", "And", CloudFormationObject.SEQUENCE),
    ("Fn::Condition", "Condition", CloudFormationObject.SCALAR),
    ("Fn::Base64", "Base64", CloudFormationObject.SCALAR),
    ("Fn::Equals", "Equals", CloudFormationObject.SEQUENCE),
    ("Fn::FindInMap", "FindInMap", CloudFormationObject.SEQUENCE),
    ("Fn::GetAtt", "GetAtt", CloudFormationObject.SEQUENCE_OR_SCALAR),
    ("Fn::GetAZs", "GetAZs", CloudFormationObject.SCALAR),
    ("Fn::If", "If", CloudFormationObject.SEQUENCE),
    ("Fn::ImportValue", "ImportValue", CloudFormationObject.SCALAR),
    ("Fn::Join", "Join", CloudFormationObject.SEQUENCE),
    ("Fn::Not", "Not", CloudFormationObject.SEQUENCE),
    ("Fn::Or", "Or", CloudFormationObject.SEQUENCE),
    ("Fn::Select", "Select", CloudFormationObject.SEQUENCE),
    ("Fn::Split", "Split", CloudFormationObject.SEQUENCE),
    ("Fn::Sub", "Sub", CloudFormationObject.SEQUENCE_OR_SCALAR),
]

_object_classes = None


def inject(*args):
    global _object_classes
    _object_classes = []

    loaders = [arg for arg in args if issubclass(arg, yaml.SafeLoader)]
    dumpers = [arg for arg in args if issubclass(arg, yaml.SafeDumper)]

    for name_, tag_, type_ in itertools.chain(functions, [ref]):
        if not tag_.startswith("!"):
            tag_ = "!{}".format(tag_)
        tag_ = six.u(tag_)

        class Object(CloudFormationObject):
            name = name_
            tag = tag_
            type = type_

        obj_cls_name = re.search(r"\w+$", tag_).group(0)  # type: ignore[union-attr]
        if six.PY2:
            obj_cls_name = str(obj_cls_name)
        Object.__name__ = obj_cls_name

        _object_classes.append(Object)
        globals()[obj_cls_name] = Object

        # Register constructors for all loaders
        for loader in loaders:
            loader.add_constructor(tag_, Object.construct)

        # Register representers for all dumpers
        for dumper in dumpers:
            dumper.add_representer(Object, Object.represent)


class CloudFormationLoader(yaml.SafeLoader):
    """Custom YAML loader that supports CloudFormation tags."""

    pass


class CloudFormationDumper(yaml.SafeDumper):
    """Custom YAML dumper that supports CloudFormation tags."""

    pass


inject(CloudFormationLoader, CloudFormationDumper)
