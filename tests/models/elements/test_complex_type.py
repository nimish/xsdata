from unittest import TestCase

from xsdata.models.elements import ComplexContent
from xsdata.models.elements import ComplexType


class ComplexTypeTests(TestCase):
    def test_property_extends(self):
        obj = ComplexType.create()
        self.assertIsNone(obj.extends)

    def test_property_is_mixed(self):
        obj = ComplexType.create()

        self.assertFalse(obj.is_mixed)

        obj.complex_content = ComplexContent.create()
        self.assertFalse(obj.is_mixed)

        obj.complex_content.mixed = True
        self.assertTrue(obj.is_mixed)

        obj.complex_content.mixed = False
        obj.mixed = True
        self.assertTrue(obj.is_mixed)
