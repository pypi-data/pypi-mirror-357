"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.cycloidal._2804 import (
        CycloidalAssembly,
    )
    from mastapy._private.system_model.part_model.cycloidal._2805 import CycloidalDisc
    from mastapy._private.system_model.part_model.cycloidal._2806 import RingPins
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.cycloidal._2804": ["CycloidalAssembly"],
        "_private.system_model.part_model.cycloidal._2805": ["CycloidalDisc"],
        "_private.system_model.part_model.cycloidal._2806": ["RingPins"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CycloidalAssembly",
    "CycloidalDisc",
    "RingPins",
)
