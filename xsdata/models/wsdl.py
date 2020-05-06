from dataclasses import dataclass
from typing import List
from typing import Optional

from xsdata.models.enums import Namespace
from xsdata.models.helpers import array_any_element
from xsdata.models.helpers import array_element
from xsdata.models.helpers import attribute
from xsdata.models.helpers import element
from xsdata.models.soap import Soap11Address
from xsdata.models.soap import Soap11Binding
from xsdata.models.soap import Soap11Body
from xsdata.models.soap import Soap11Fault
from xsdata.models.soap import Soap11Header
from xsdata.models.soap import Soap11HeaderFault
from xsdata.models.soap import Soap11Operation
from xsdata.models.soap import Soap12Address
from xsdata.models.soap import Soap12Binding
from xsdata.models.soap import Soap12Body
from xsdata.models.soap import Soap12Fault
from xsdata.models.soap import Soap12Header
from xsdata.models.soap import Soap12HeaderFault
from xsdata.models.soap import Soap12Operation
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
class Input(BindingMessage):
    soap_header_11: Optional[Soap11Header] = element(
        name="header", namespace=Namespace.SOAP11.uri
    )
    soap_header_fault_11: Optional[Soap11HeaderFault] = element(
        name="headerfault", namespace=Namespace.SOAP11.uri
    )
    soap_body_11: Optional[Soap11Body] = element(
        name="body", namespace=Namespace.SOAP11.uri
    )

    soap_header_12: Optional[Soap12Header] = element(
        name="header", namespace=Namespace.SOAP12.uri
    )
    soap_header_fault_12: Optional[Soap12HeaderFault] = element(
        name="headerfault", namespace=Namespace.SOAP12.uri
    )
    soap_body_12: Optional[Soap12Body] = element(
        name="body", namespace=Namespace.SOAP12.uri
    )


@dataclass
class Output(BindingMessage):
    soap_header_11: Optional[Soap11Header] = element(
        name="header", namespace=Namespace.SOAP11.uri
    )
    soap_header_fault_11: Optional[Soap11HeaderFault] = element(
        name="headerfault", namespace=Namespace.SOAP11.uri
    )
    soap_body_11: Optional[Soap11Body] = element(
        name="body", namespace=Namespace.SOAP11.uri
    )

    soap_header_12: Optional[Soap12Header] = element(
        name="header", namespace=Namespace.SOAP12.uri
    )
    soap_header_fault_12: Optional[Soap12HeaderFault] = element(
        name="headerfault", namespace=Namespace.SOAP12.uri
    )
    soap_body_12: Optional[Soap12Body] = element(
        name="body", namespace=Namespace.SOAP12.uri
    )


@dataclass
class Fault(BindingMessage):
    soap_fault_11: Optional[Soap11Fault] = element(
        name="fault", namespace=Namespace.SOAP11.uri
    )
    soap_fault_12: Optional[Soap12Fault] = element(
        name="fault", namespace=Namespace.SOAP12.uri
    )


@dataclass
class BindingOperation(WsdlElement):
    input: Optional[Input] = element()
    output: Optional[Output] = element()
    faults: List[Fault] = array_element(name="fault")

    soap_operation_11: Optional[Soap11Operation] = element(
        name="operation", namespace=Namespace.SOAP11.uri
    )
    soap_operation_12: Optional[Soap12Operation] = element(
        name="operation", namespace=Namespace.SOAP12.uri
    )


@dataclass
class Binding(WsdlElement):
    type: Optional[str] = attribute()
    operations: List[BindingOperation] = array_element(name="operation")

    soap_binding_11: Optional[Soap11Binding] = element(
        name="binding", namespace=Namespace.SOAP11.uri
    )
    soap_binding_12: Optional[Soap12Binding] = element(
        name="binding", namespace=Namespace.SOAP12.uri
    )


@dataclass
class ServicePort(WsdlElement):
    binding: Optional[str] = attribute()
    soap_address_11: Optional[Soap11Address] = element(
        name="address", namespace=Namespace.SOAP11.uri
    )
    soap_address_12: Optional[Soap12Address] = element(
        name="address", namespace=Namespace.SOAP12.uri
    )


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

    parser = XmlParser()
    air_path = Path(
        "/home/chris/projects/xsdata-samples/travelport/schemas/air_v48_0/Air.wsdl"
    )
    result = parser.from_path(air_path, Definitions)
    print(result)
