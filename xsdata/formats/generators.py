import math
import re
from abc import ABC
from abc import abstractmethod
from base64 import urlsafe_b64encode
from decimal import Decimal
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from xml.sax.saxutils import quoteattr

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template
from lxml.etree import QName

from xsdata.formats.converters import to_python
from xsdata.formats.dataclass.models.constants import XmlType
from xsdata.formats.dataclass.utils import safe_snake
from xsdata.models.codegen import Attr
from xsdata.models.codegen import AttrType
from xsdata.models.codegen import Class
from xsdata.models.codegen import Extension
from xsdata.models.codegen import Package
from xsdata.models.enums import DataType
from xsdata.models.enums import Tag
from xsdata.utils import text


class AbstractGenerator(ABC):
    templates_dir: Optional[Path] = None

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)), autoescape=False
        )

    def template(self, name: str) -> Template:
        return self.env.get_template("{}.jinja2".format(name))

    @abstractmethod
    def render(self, classes: List[Class]) -> Iterator[Tuple[Path, str, str]]:
        pass

    @classmethod
    def module_name(cls, name: str) -> str:
        return name

    @classmethod
    def package_name(cls, name: str) -> str:
        return name


class PythonAbstractGenerator(AbstractGenerator, ABC):

    xml_type_map = {
        Tag.ELEMENT: XmlType.ELEMENT,
        Tag.ANY: XmlType.WILDCARD,
        Tag.ANY_ATTRIBUTE: XmlType.ATTRIBUTES,
        Tag.ATTRIBUTE: XmlType.ATTRIBUTE,
        None: XmlType.TEXT,
    }

    @classmethod
    def process_class(cls, obj: Class, parents: List[str] = None) -> Class:
        """Normalize all class instance fields, extends, name and the inner
        classes recursively."""
        parents = parents or []
        obj.name = cls.class_name(obj.name)

        curr_parents = parents + [obj.name]
        for inner in obj.inner:
            cls.process_class(inner, curr_parents)

        if obj.is_enumeration:
            cls.process_enumerations(obj)
        else:
            cls.process_attributes(obj, curr_parents)

        for extension in obj.extensions:
            cls.process_extension(extension)

        return obj

    @classmethod
    def process_enumerations(cls, obj: Class):
        attr_types = {ext.type.name: ext.type for ext in obj.extensions}
        attrs = {str(attr.default): attr for attr in obj.attrs}
        obj.attrs = sorted(attrs.values(), key=lambda x: str(x.default))

        names = set()
        for attr in obj.attrs:
            attr.types.extend(attr_types.values())
            attr.default = cls.attribute_default(attr, obj.ns_map)
            attr.name = cls.enumeration_name(str(attr.default).strip("\"'"))
            names.add(attr.name)

        if len(names) != len(obj.attrs):
            for attr in obj.attrs:
                safe_name = urlsafe_b64encode(str(attr.default).encode()).decode()
                attr.name = cls.enumeration_name(safe_name)

    @classmethod
    def process_attributes(cls, obj: Class, parents_list: List[str]):
        """Process class attributes and prevent duplicate attribute names."""
        for attr in obj.attrs:
            cls.process_attribute(obj, attr, parents_list)

        if cls.has_duplicate_attrs(obj):
            cls.sanitize_attribute_names(obj)

        if cls.has_duplicate_attrs(obj):
            cls.hash_attributes_names(obj)

        cls.unset_attributes_local_names(obj)

    @classmethod
    def sanitize_attribute_names(cls, obj: Class):
        """
        Append xml type to attribute name if it's not unique in the list.

        Prefer keeping intact element attributes.
        """
        for attr in obj.attrs:
            dup = next(
                (dup for dup in obj.attrs if dup is not attr and dup.name == attr.name),
                None,
            )
            if not dup:
                continue
            if attr.xml_type == XmlType.ELEMENT:
                dup.name = cls.attribute_name(f"{dup.name}_{dup.xml_type}")
            else:
                attr.name = cls.attribute_name(f"{attr.name}_{attr.xml_type}")

    @classmethod
    def hash_attributes_names(cls, obj: Class):
        """
        Replace attribute names with b64 hash of the local name.

        This is a last resort to create unique class attribute names.
        """
        for attr in obj.attrs:
            safe_name = urlsafe_b64encode(str(attr.local_name).encode()).decode()
            attr.name = cls.attribute_name(safe_name)

    @classmethod
    def has_duplicate_attrs(cls, obj: Class) -> bool:
        """Check if given class includes duplicate attribute names."""
        names = set([attr.name for attr in obj.attrs])
        return len(names) < len(obj.attrs)

    @classmethod
    def unset_attributes_local_names(cls, obj: Class):
        """
        Unset attribute local name when it's not necessary.

        Examples:
            - xs:any
            - xs:anyAttribute
            - field name is equal to local name
        """
        for attr in obj.attrs:
            if (
                attr.xml_type in (XmlType.ATTRIBUTES, XmlType.WILDCARD, None)
                or attr.name == attr.local_name
            ):
                attr.local_name = None

    @classmethod
    def process_extension(cls, extension: Extension):
        extension.type.name = cls.type_name(extension.type)

    @classmethod
    def process_attribute(cls, target: Class, attr: Attr, parents: List[str]):
        """Normalize attribute properties."""
        attr.name = cls.attribute_name(attr.name)
        attr.display_type = cls.attribute_display_type(attr, parents)
        attr.default = cls.attribute_default(attr, target.ns_map)
        attr.xml_type = cls.xml_type_map.get(attr.tag)

        if attr.local_name:
            attr.local_name = text.suffix(attr.local_name)

    @classmethod
    def process_import(cls, package: Package) -> Package:
        """Normalize import package properties."""
        package.name = cls.class_name(package.name)
        if package.alias:
            package.alias = cls.class_name(package.alias)

        return package

    @classmethod
    def module_name(cls, name: str) -> str:
        return text.snake_case(safe_snake(name, default="mod"))

    @classmethod
    def package_name(cls, name: str) -> str:
        return ".".join(
            map(
                lambda x: text.snake_case(safe_snake(x, default="pkg")), name.split(".")
            )
        )

    @classmethod
    def class_name(cls, name: str) -> str:
        """Convert class names to pascal case."""
        return text.pascal_case(safe_snake(name, "type"))

    @classmethod
    def type_name(cls, attr_type: AttrType) -> str:
        """Convert xsd types to python or apply class name conventions after
        stripping any reference prefix."""

        return attr_type.native_name or cls.class_name(text.suffix(attr_type.name))

    @classmethod
    def attribute_name(cls, name: str) -> str:
        """
        Strip reference prefix and turn to snake case.

        If the name is one of the python reserved words append the
        prefix _value
        """
        local_name = text.suffix(name)
        return text.snake_case(safe_snake(local_name))

    @classmethod
    def enumeration_name(cls, name: str) -> str:
        """
        Strip reference prefix and turn to snake case.

        If the name is one of the python reserved words append the
        prefix _value
        """
        return text.snake_case(safe_snake(name)).upper()

    @classmethod
    def attribute_display_type(cls, attr: Attr, parents: List[str]) -> str:
        """
        Normalize attribute type.

        Steps:
            * If type alias is present use class name normalization
            * Otherwise use the type name normalization
            * Prepend outer class names and quote result for forward references
            * Wrap the result with List if the field accepts a list of values
            * Wrap the result with Optional if the field default value is None
        """

        type_names: List[str] = []
        for attr_type in attr.types:
            type_name = (
                cls.class_name(attr_type.alias)
                if attr_type.alias
                else cls.type_name(attr_type)
            )
            if attr_type.forward_ref:
                outer_str = ".".join(parents)
                type_name = f'"{outer_str}.{type_name}"'
            elif attr_type.self_ref:
                type_name = f'"{type_name}"'

            if type_name not in type_names:
                type_names.append(type_name)

        result = ", ".join(type_names)
        if len(type_names) > 1:
            result = f"Union[{result}]"

        if attr.is_list:
            result = f"List[{result}]"
        elif attr.is_map:
            result = f"Dict[{result}]"
        elif attr.default is None and "Dict" not in result:
            result = f"Optional[{result}]"

        return result

    @classmethod
    def attribute_default(cls, attr: Attr, ns_map: Optional[Dict] = None) -> Any:
        """Normalize default value/factory by the attribute type."""
        if attr.is_list:
            return "list"
        if attr.is_map:
            return "dict"
        if not isinstance(attr.default, str):
            return attr.default

        data_types = {
            attr_type.native_code: attr_type.native_type
            for attr_type in attr.types
            if attr_type.native
        }

        local_types = list(set(data_types.values()))
        default_value = to_python(local_types, attr.default, ns_map, in_order=False)

        if isinstance(default_value, str):
            if DataType.NMTOKENS.code in data_types:
                default_value = " ".join(
                    filter(None, map(str.strip, re.split(r"\s+", default_value)))
                )

            default_value = quoteattr(default_value)
        elif isinstance(default_value, float) and math.isinf(default_value):
            default_value = f"float('{default_value}')"
        elif isinstance(default_value, Decimal):
            default_value = repr(default_value)
        elif isinstance(default_value, QName):
            default_value = (
                f'QName("{default_value.namespace}", "{default_value.localname}")'
            )
        return default_value
