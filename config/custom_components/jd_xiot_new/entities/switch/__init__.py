"""Switch Entities for JingDong XIoT integration."""

from .jd._jdzn1kg01lf.jdzn1kg01lf_entity import DeviceJdzn1kg01lfEntity
from .jd._jdzn1kg04lf.jdzn1kg04lf_entity import DeviceJdzn1kg04lfEntity
from .jd._jdzn2kg02lf.jdzn2kg02lf_entity import (
    DeviceJdzn2kg02lfEntity1,
    DeviceJdzn2kg02lfEntity2,
)
from .jd._jdzn2kg05lf.jdzn2kg05lf_entity import (
    DeviceJdzn2kg05lfEntity1,
    DeviceJdzn2kg05lfEntity2,
)
from .jd._jdzn3kg03lf.jdzn3kg03lf_entity import (
    DeviceJdzn3kg03lfEntity1,
    DeviceJdzn3kg03lfEntity2,
    DeviceJdzn3kg03lfEntity3,
)
from .jd._jdzn3kg06lf.jdzn3kg06lf_entity import (
    DeviceJdzn3kg06lfEntity1,
    DeviceJdzn3kg06lfEntity2,
    DeviceJdzn3kg06lfEntity3,
)

__all__ = [
    "DeviceJdzn1kg01lfEntity",
    "DeviceJdzn1kg04lfEntity",
    "DeviceJdzn2kg02lfEntity1",
    "DeviceJdzn2kg02lfEntity2",
    "DeviceJdzn2kg05lfEntity1",
    "DeviceJdzn2kg05lfEntity2",
    "DeviceJdzn3kg03lfEntity1",
    "DeviceJdzn3kg03lfEntity2",
    "DeviceJdzn3kg03lfEntity3",
    "DeviceJdzn3kg06lfEntity1",
    "DeviceJdzn3kg06lfEntity2",
    "DeviceJdzn3kg06lfEntity3"
]
