from dataclasses import dataclass, field
from typing import List, Optional

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
class Number:
    """
    :ivar value:
    """
    class Meta:
        name = "number"
        namespace = "http://datypic.com/prod"

    value: Optional[int] = field(
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
            required=True,
            min_inclusive=2.0,
            max_inclusive=18.0
        )
    )


@dataclass
class ProductType:
    """
    :ivar number:
    :ivar name:
    :ivar size:
    :ivar dept:
    """
    number: Optional[Number] = field(
        default=None,
        metadata=dict(
            type="Element",
            namespace="http://datypic.com/prod",
            required=True
        )
    )
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
            namespace="http://datypic.com/prod",
            required=True
        )
    )
    dept: Optional[str] = field(
        default=None,
        metadata=dict(
            type="Attribute"
        )
    )


@dataclass
class Product(ProductType):
    class Meta:
        name = "product"
        namespace = "http://datypic.com/prod"


@dataclass
class CatalogType:
    """
    :ivar product:
    """
    product: List[Product] = field(
        default_factory=list,
        metadata=dict(
            type="Element",
            namespace="http://datypic.com/prod",
            min_occurs=1,
            max_occurs=9223372036854775807
        )
    )


@dataclass
class Catalog(CatalogType):
    class Meta:
        name = "catalog"
        namespace = "http://datypic.com/prod"
