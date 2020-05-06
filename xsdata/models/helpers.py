import sys
from dataclasses import field
from typing import Any as Anything
from typing import Dict
from typing import Union as UnionType

from xsdata.formats.dataclass.models.constants import XmlType
from xsdata.models.enums import NamespaceType


def attribute(default: Anything = None, init: bool = True, **kwargs: str) -> Anything:
    kwargs.update(type=XmlType.ATTRIBUTE)
    return field(init=init, default=default, metadata=kwargs)


def element(init: bool = True, **kwargs: str) -> Anything:
    kwargs.update(type=XmlType.ELEMENT)
    return field(init=init, default=None, metadata=kwargs)


def any_element(init: bool = True, **kwargs: str) -> Anything:
    kwargs.update(type=XmlType.WILDCARD, namespace=NamespaceType.ANY.value)
    return field(init=init, default=None, metadata=kwargs)


def array_element(init: bool = True, **kwargs: str) -> Anything:
    kwargs.update(type=XmlType.ELEMENT)
    return field(init=init, default_factory=list, metadata=kwargs)


def array_any_element(init: bool = True, **kwargs: str) -> Anything:
    kwargs.update(type=XmlType.WILDCARD, namespace=NamespaceType.ANY.value)
    return field(init=init, default_factory=list, metadata=kwargs)


def occurrences(min_value: int, max_value: UnionType[int, str]) -> Dict[str, int]:
    max_value = sys.maxsize if max_value == "unbounded" else int(max_value)
    return dict(min_occurs=min_value, max_occurs=max_value)
