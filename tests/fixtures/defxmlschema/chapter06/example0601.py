from dataclasses import dataclass, field
from typing import Optional

__NAMESPACE__ = "http://datypic.com/prod"


@dataclass
class Name:
    """
    :ivar value:
    """
    class Meta:
        name = "name"
        namespace = "http://datypic.com/prod"

    value: Optional[str] = field(
        default=None,
        metadata=dict(
            required=True
        )
    )


@dataclass
class Size:
    """
    :ivar value:
    """
    class Meta:
        name = "size"
        namespace = "http://datypic.com/prod"

    value: Optional[int] = field(
        default=None,
        metadata=dict(
            required=True
        )
    )


@dataclass
class ProductType:
    """
    :ivar name:
    :ivar size:
    """
    name: Optional[Name] = field(
        default=None,
        metadata=dict(
            type="Element",
            namespace="http://datypic.com/prod",
            required=True
        )
    )
    size: Optional[Size] = field(
        default=None,
        metadata=dict(
            type="Element",
            namespace="http://datypic.com/prod"
        )
    )
