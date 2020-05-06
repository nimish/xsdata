from dataclasses import dataclass
from typing import List
from typing import Optional

from xsdata.formats.dataclass.parsers.config import ParserConfig
from xsdata.models.helpers import array_any_element
from xsdata.models.helpers import array_element
from xsdata.models.helpers import attribute
from xsdata.models.helpers import element
from xsdata.models.xsd import Schema


@dataclass
class Documentation:
    elements: List[object] = array_any_element()


@dataclass
class WsdlElement:
    name: Optional[str] = attribute()
    documentation: Optional[Documentation] = element()


@dataclass
class Types:
    schemas: List[Schema] = array_element(name="schema")
    documentation: Optional[Documentation] = element()


@dataclass
class Import:
    namespace: Optional[str] = attribute()
    location: Optional[str] = attribute()


@dataclass
class Message(WsdlElement):
    part: List["Message.Part"] = array_element()

    class Part:
        """
        <part name="nmtoken" element="qname"?

        type="qname"?/>
        """

        name: Optional[str] = attribute()
        type: Optional[str] = attribute()
        element: Optional[str] = element()


@dataclass
class PortTypeMessage(WsdlElement):
    message: Optional[str] = attribute()


@dataclass
class PortTypeOperation(WsdlElement):
    input: Optional[PortTypeMessage] = element()
    output: Optional[PortTypeMessage] = element()
    faults: List[PortTypeMessage] = array_element(name="fault")


@dataclass
class PortType(WsdlElement):
    operations: List[PortTypeOperation] = array_element()


@dataclass
class BindingMessage(WsdlElement):
    pass


@dataclass
class BindingOperation(WsdlElement):
    input: Optional[BindingMessage] = element()
    output: Optional[BindingMessage] = element()
    faults: List[BindingMessage] = array_element(name="fault")


@dataclass
class Binding(WsdlElement):
    type: Optional[str] = attribute()
    operations: List[BindingOperation] = array_element(name="operation")


@dataclass
class ServicePort(WsdlElement):
    binding: Optional[str] = attribute()


@dataclass
class Service(WsdlElement):
    ports: List[ServicePort] = array_element(name="port")


@dataclass
class Definitions(WsdlElement):
    class Meta:
        name = "definitions"
        namespace = "http://schemas.xmlsoap.org/wsdl/"

    target_namespace: Optional[str] = attribute(name="targetNamespace")

    types: Types = element()
    imports: List[Import] = array_element(name="import")
    messages: List[Message] = array_element(name="message")
    port_types: List[PortType] = array_element(name="portType")
    bindings: List[Binding] = array_element(name="binding")
    services: List[Service] = array_element(name="service")


if __name__ == "__main__":
    from pathlib import Path
    from xsdata.formats.dataclass.parsers import XmlParser

    parser = XmlParser(config=ParserConfig(fail_on_unknown_properties=False))
    air_path = Path(
        "/home/chris/projects/xsdata-samples/travelport/schemas/air_v48_0/Air.wsdl"
    )
    result = parser.from_path(air_path, Definitions)
    print(result)
