"""SpringDamperHalfSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.system_deflections import _2969

_SPRING_DAMPER_HALF_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "SpringDamperHalfSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2890, _2892, _2896
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7882,
        _7884,
        _7885,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4401
    from mastapy._private.system_model.analyses_and_results.static_loads import _7823
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2954,
        _3023,
        _3026,
    )
    from mastapy._private.system_model.part_model.couplings import _2845

    Self = TypeVar("Self", bound="SpringDamperHalfSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="SpringDamperHalfSystemDeflection._Cast_SpringDamperHalfSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("SpringDamperHalfSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SpringDamperHalfSystemDeflection:
    """Special nested class for casting SpringDamperHalfSystemDeflection to subclasses."""

    __parent__: "SpringDamperHalfSystemDeflection"

    @property
    def coupling_half_system_deflection(
        self: "CastSelf",
    ) -> "_2969.CouplingHalfSystemDeflection":
        return self.__parent__._cast(_2969.CouplingHalfSystemDeflection)

    @property
    def mountable_component_system_deflection(
        self: "CastSelf",
    ) -> "_3023.MountableComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3023,
        )

        return self.__parent__._cast(_3023.MountableComponentSystemDeflection)

    @property
    def component_system_deflection(
        self: "CastSelf",
    ) -> "_2954.ComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2954,
        )

        return self.__parent__._cast(_2954.ComponentSystemDeflection)

    @property
    def part_system_deflection(self: "CastSelf") -> "_3026.PartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3026,
        )

        return self.__parent__._cast(_3026.PartSystemDeflection)

    @property
    def part_fe_analysis(self: "CastSelf") -> "_7884.PartFEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7884,
        )

        return self.__parent__._cast(_7884.PartFEAnalysis)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7885.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7885,
        )

        return self.__parent__._cast(_7885.PartStaticLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7882.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7882,
        )

        return self.__parent__._cast(_7882.PartAnalysisCase)

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
    def spring_damper_half_system_deflection(
        self: "CastSelf",
    ) -> "SpringDamperHalfSystemDeflection":
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
class SpringDamperHalfSystemDeflection(_2969.CouplingHalfSystemDeflection):
    """SpringDamperHalfSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPRING_DAMPER_HALF_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2845.SpringDamperHalf":
        """mastapy.system_model.part_model.couplings.SpringDamperHalf

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def component_load_case(self: "Self") -> "_7823.SpringDamperHalfLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.SpringDamperHalfLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def power_flow_results(self: "Self") -> "_4401.SpringDamperHalfPowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.SpringDamperHalfPowerFlow

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerFlowResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_SpringDamperHalfSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_SpringDamperHalfSystemDeflection
        """
        return _Cast_SpringDamperHalfSystemDeflection(self)
