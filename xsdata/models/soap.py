from dataclasses import dataclass
from typing import Optional

from xsdata.models.enums import BindingStyle
from xsdata.models.enums import UseChoice
from xsdata.models.helpers import attribute


@dataclass
class Soap11Operation:
    soap_action: Optional[str] = attribute(name="soapAction")
    style: Optional[str] = attribute(default=BindingStyle.DOCUMENT)
    transport: Optional[str] = attribute()


@dataclass
class Soap12Operation:
    soap_action: Optional[str] = attribute(name="soapAction")
    style: Optional[str] = attribute(default=BindingStyle.DOCUMENT)
    soap_action_required: bool = attribute(name="soapActionRequired", default=True)


@dataclass
class Soap11Body:
    use: Optional[UseChoice] = attribute(default=UseChoice.LITERAL)
    parts: Optional[str] = attribute()
    namespace: Optional[str] = attribute()
    encoding_style: Optional[str] = attribute(name="encodingStyle")


@dataclass
class Soap12Body(Soap11Body):
    pass


@dataclass
class Soap11Header:
    use: Optional[UseChoice] = attribute(default=UseChoice.LITERAL)
    part: Optional[str] = attribute()
    message: Optional[str] = attribute()
    namespace: Optional[str] = attribute()
    encoding_style: Optional[str] = attribute(name="encodingStyle")


@dataclass
class Soap12Header(Soap11Header):
    pass


@dataclass
class Soap11Fault:
    use: Optional[UseChoice] = attribute(default=UseChoice.LITERAL)
    name: Optional[str] = attribute()
    namespace: Optional[str] = attribute()
    encoding_style: Optional[str] = attribute(name="encodingStyle")


@dataclass
class Soap12Fault(Soap11Fault):
    pass


@dataclass
class Soap11HeaderFault:
    use: Optional[UseChoice] = attribute(default=UseChoice.LITERAL)
    name: Optional[str] = attribute()
    part: Optional[str] = attribute()
    namespace: Optional[str] = attribute()
    encoding_style: Optional[str] = attribute(name="encodingStyle")


@dataclass
class Soap12HeaderFault(Soap11HeaderFault):
    pass


@dataclass
class Soap11Binding:
    style: Optional[BindingStyle] = attribute(default=BindingStyle.DOCUMENT)
    transport: Optional[str] = attribute()


@dataclass
class Soap12Binding:
    style: Optional[BindingStyle] = attribute(default=BindingStyle.DOCUMENT)
    transport: Optional[str] = attribute()


@dataclass
class Soap11Address:
    location: Optional[str] = attribute()


@dataclass
class Soap12Address(Soap11Address):
    pass
