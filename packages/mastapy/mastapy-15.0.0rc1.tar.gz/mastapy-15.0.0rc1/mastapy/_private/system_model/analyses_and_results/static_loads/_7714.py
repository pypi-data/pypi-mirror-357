"""ConnectorLoadCase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.static_loads import _7790

_CONNECTOR_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads", "ConnectorLoadCase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2890, _2892, _2896
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7683,
        _7701,
        _7792,
        _7794,
        _7815,
    )
    from mastapy._private.system_model.part_model import _2672

    Self = TypeVar("Self", bound="ConnectorLoadCase")
    CastSelf = TypeVar("CastSelf", bound="ConnectorLoadCase._Cast_ConnectorLoadCase")


__docformat__ = "restructuredtext en"
__all__ = ("ConnectorLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectorLoadCase:
    """Special nested class for casting ConnectorLoadCase to subclasses."""

    __parent__: "ConnectorLoadCase"

    @property
    def mountable_component_load_case(
        self: "CastSelf",
    ) -> "_7790.MountableComponentLoadCase":
        return self.__parent__._cast(_7790.MountableComponentLoadCase)

    @property
    def component_load_case(self: "CastSelf") -> "_7701.ComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7701,
        )

        return self.__parent__._cast(_7701.ComponentLoadCase)

    @property
    def part_load_case(self: "CastSelf") -> "_7794.PartLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7794,
        )

        return self.__parent__._cast(_7794.PartLoadCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2896.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2896

        return self.__parent__._cast(_2896.PartAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2892.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2892

        return self.__parent__._cast(_2892.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2890.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2890

        return self.__parent__._cast(_2890.DesignEntityAnalysis)

    @property
    def bearing_load_case(self: "CastSelf") -> "_7683.BearingLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7683,
        )

        return self.__parent__._cast(_7683.BearingLoadCase)

    @property
    def oil_seal_load_case(self: "CastSelf") -> "_7792.OilSealLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7792,
        )

        return self.__parent__._cast(_7792.OilSealLoadCase)

    @property
    def shaft_hub_connection_load_case(
        self: "CastSelf",
    ) -> "_7815.ShaftHubConnectionLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7815,
        )

        return self.__parent__._cast(_7815.ShaftHubConnectionLoadCase)

    @property
    def connector_load_case(self: "CastSelf") -> "ConnectorLoadCase":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class ConnectorLoadCase(_7790.MountableComponentLoadCase):
    """ConnectorLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTOR_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2672.Connector":
        """mastapy.system_model.part_model.Connector

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConnectorLoadCase":
        """Cast to another type.

        Returns:
            _Cast_ConnectorLoadCase
        """
        return _Cast_ConnectorLoadCase(self)
