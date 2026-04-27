"""Light entities for JingDong XIoT integration."""

# 注册灯光实体类到jd_light_mapping中
from .jd._jdznsd01sy.jdznsd01sy_entity import DeviceJdznsd01syEntity
from .jd._jdznsd02sy.jdznsd02sy_entity import DeviceJdznsd02syEntity
from .jd._jdznsd03sy.jdznsd03sy_entity import DeviceJdznsd03syEntity
from .jd._jdznsd04sy.jdznsd04sy_entity import DeviceJdznsd04syEntity
from .jd._jdzntd01sy.jdzntd01sy_entity import DeviceJdzntd01syEntity
from .jd._jdzntd02sy.jdzntd02sy_entity import DeviceJdzntd02syEntity
from .jd._jdznxtd01sy.jdznxtd01sy_entity import DeviceJdznxtd01syEntity
from .jd._jdznxtd02sy.jdznxtd02sy_entity import DeviceJdznxtd02syEntity
from .jd._jdznxtd03sy.jdznxtd03sy_entity import DeviceJdznxtd03syEntity

__all__ = [
    "DeviceJdznsd01syEntity",
    "DeviceJdznsd02syEntity",
    "DeviceJdznsd03syEntity",
    "DeviceJdznsd04syEntity",
    "DeviceJdzntd01syEntity",
    "DeviceJdzntd02syEntity",
    "DeviceJdznxtd01syEntity",
    "DeviceJdznxtd02syEntity",
    "DeviceJdznxtd03syEntity",
]
