import random
from pathlib import Path
from unittest import mock

from tests.factories import ClassFactory
from tests.factories import FactoryTestCase
from tests.factories import PackageFactory
from xsdata.formats.dataclass.generator import DataclassGenerator
from xsdata.resolver import DependenciesResolver


class DataclassGeneratorTests(FactoryTestCase):
    @mock.patch.object(DataclassGenerator, "render_package")
    @mock.patch.object(DataclassGenerator, "render_module")
    def test_render(
        self, mock_render_module, mock_render_package,
    ):
        classes = ClassFactory.list(3)

        mock_render_module.return_value = "module"
        mock_render_package.return_value = "package"

        iterator = DataclassGenerator().render(classes)

        actual = [out for out in iterator]
        self.assertEqual(2, len(actual))

        self.assertEqual(3, len(actual[0]))
        self.assertEqual("init", actual[0][1])
        self.assertEqual("foo/__init__.py", str(actual[0][0].relative_to(Path.cwd())))
        self.assertEqual(mock_render_package.return_value, actual[0][2])
        mock_render_package.assert_called_once_with(classes)

        self.assertEqual(3, len(actual[1]))
        self.assertIsInstance(actual[1][0], Path)
        self.assertTrue(actual[1][0].is_absolute())
        self.assertEqual("foo.tests", actual[1][1])
        self.assertEqual("foo/tests.py", str(actual[1][0].relative_to(Path.cwd())))
        self.assertEqual(mock_render_module.return_value, actual[1][2])
        mock_render_module.assert_called_once_with(mock.ANY, classes)

    def test_render_package(self):
        classes = ClassFactory.list(3)
        random.shuffle(classes)

        actual = DataclassGenerator().render_package(classes)
        expected = "\n".join(
            [
                "from foo.tests import ClassB",
                "from foo.tests import ClassC",
                "from foo.tests import ClassD",
                "",
            ]
        )
        self.assertEqual(expected, actual)

    def test_render_module(self):
        classes = [ClassFactory.enumeration(2), ClassFactory.elements(2)]
        resolver = DependenciesResolver()

        actual = DataclassGenerator().render_module(resolver, classes)
        expected = (
            "from enum import Enum\n"
            "from dataclasses import dataclass, field\n"
            "from typing import Optional\n\n"
            '__NAMESPACE__ = "xsdata"\n\n\n'
            "class ClassB(Enum):\n"
            '    """\n'
            "    :cvar NONE_VALUE:\n"
            '    """\n'
            "    NONE_VALUE = None\n\n\n"
            "@dataclass\n"
            "class ClassC:\n"
            '    """\n'
            "    :ivar attr_d:\n"
            "    :ivar attr_e:\n"
            '    """\n'
            "    class Meta:\n"
            '        name = "class_C"\n\n'
            "    attr_d: Optional[str] = field(\n"
            "        default=None,\n"
            "        metadata=dict(\n"
            '            name="attr_D",\n'
            '            type="Element"\n'
            "        )\n"
            "    )\n"
            "    attr_e: Optional[str] = field(\n"
            "        default=None,\n"
            "        metadata=dict(\n"
            '            name="attr_E",\n'
            '            type="Element"\n'
            "        )\n"
            "    )\n"
        )
        self.assertEqual(expected, actual)

    @mock.patch.object(DataclassGenerator, "process_import")
    def test_prepare_imports(self, mock_process_import):
        packages = [
            PackageFactory.create(name="foo", source="omg"),
            PackageFactory.create(name="bar", source="omg"),
            PackageFactory.create(name="thug", source="life"),
        ]
        processed = [
            PackageFactory.create(name="aaa", source="a"),
            PackageFactory.create(name="bbb", source="b"),
            PackageFactory.create(name="ccc", source="c"),
        ]

        mock_process_import.side_effect = processed

        expected = {"omg": processed[:2], "life": processed[2:]}

        actual = DataclassGenerator().prepare_imports(packages)
        self.assertEqual(expected, actual)

    def test_module_name(self):
        generator = DataclassGenerator()
        self.assertEqual("foo_bar", generator.module_name("fooBar"))
        self.assertEqual("foo_bar_wtf", generator.module_name("fooBar.wtf"))
        self.assertEqual("mod_1111", generator.module_name("1111"))
