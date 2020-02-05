from dataclasses import dataclass
from dataclasses import Field
from dataclasses import field
from dataclasses import fields
from dataclasses import is_dataclass
from dataclasses import MISSING
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import get_type_hints
from typing import Iterator
from typing import Optional
from typing import Tuple
from typing import Type

from lxml.etree import QName

from xsdata.models.enums import TagType


class Tag(Enum):
    TEXT = 1
    ATTRIBUTE = 2
    ELEMENT = 3
    ROOT = 4

    @classmethod
    def from_metadata_type(cls, meta_type):
        if meta_type == TagType.ATTRIBUTE:
            return cls.ATTRIBUTE
        elif meta_type == TagType.ELEMENT:
            return cls.ELEMENT
        else:
            return cls.TEXT


@dataclass(frozen=True)
class ClassVar:
    name: str
    qname: QName
    type: Any
    tag: Tag
    is_nillable: bool = False
    is_list: bool = False
    is_dataclass: bool = False
    default: Any = None

    @property
    def is_attribute(self):
        return self.tag == Tag.ATTRIBUTE

    @property
    def is_text(self):
        return self.tag == Tag.TEXT

    @property
    def is_element(self):
        return self.tag == Tag.ELEMENT

    @property
    def namespace(self):
        return self.qname.namespace


@dataclass(frozen=True)
class ClassMeta:
    name: str
    qname: QName
    mixed: bool
    vars: Dict[QName, ClassVar]

    @property
    def namespace(self):
        return self.qname.namespace


@dataclass
class ModelInspect:
    name: Callable = field(default=lambda x: x)
    cache: Dict[Type, ClassMeta] = field(default_factory=dict)

    def class_meta(self, clazz: Type, parent_ns: Optional[str] = None) -> ClassMeta:
        if clazz not in self.cache:
            if not is_dataclass(clazz):
                raise TypeError(f"Object {clazz} is not a dataclass.")

            meta = getattr(clazz, "Meta", None)
            name = getattr(meta, "name", self.name(clazz.__name__))
            mixed = getattr(meta, "mixed", False)
            namespace = getattr(meta, "namespace", parent_ns)

            self.cache[clazz] = ClassMeta(
                name=name,
                qname=QName(namespace, name),
                mixed=mixed,
                vars={arg.qname: arg for arg in self.get_type_hints(clazz, namespace)},
            )
        return self.cache[clazz]

    def get_type_hints(self, clazz, parent_ns: Optional[str]) -> Iterator[ClassVar]:
        type_hints = get_type_hints(clazz)

        for var in fields(clazz):
            type_hint = type_hints[var.name]
            is_list, type_hint = self.real_type(type_hint)

            tag = Tag.from_metadata_type(var.metadata.get("type"))
            namespace = self.real_namespace(var, tag, parent_ns)
            local_name = var.metadata.get("name") or self.name(var.name)

            yield ClassVar(
                name=var.name,
                qname=QName(namespace or None, local_name),
                tag=tag,
                is_list=is_list,
                is_nillable=var.metadata.get("nillable") is True,
                is_dataclass=is_dataclass(type_hint),
                type=type_hint,
                default=self.default_value(var),
            )

    @staticmethod
    def real_namespace(var: Field, tag: Tag, parent_ns: Optional[str]) -> Optional[str]:
        namespace = var.metadata.get("namespace")
        if tag == Tag.ELEMENT:
            return namespace if namespace is not None else parent_ns
        else:
            return namespace

    @staticmethod
    def default_value(var: Field) -> Any:
        if var.default_factory is not MISSING:  # type: ignore
            return var.default_factory  # type: ignore
        elif var.default is not MISSING:
            return var.default
        else:
            return None

    @staticmethod
    def real_type(type_hint) -> Tuple[bool, Type]:
        is_list = False
        if hasattr(type_hint, "__origin__"):
            is_list = type_hint.__origin__ is list
            type_hint = type_hint.__args__[0]

        return is_list, type_hint
