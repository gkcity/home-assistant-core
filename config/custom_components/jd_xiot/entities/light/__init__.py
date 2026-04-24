"""Type definitions and utilities for JingDong XIoT integration."""

# 注册灯光实体类到jd_light_mapping中
from ._jdznsd01sy.jdznsd01sy_entity import Jdznsd01syEntity
from ._jdznsd02sy.jdznsd02sy_entity import Jdznsd02syEntity
from ._jdznsd03sy.jdznsd03sy_entity import Jdznsd03syEntity
from ._jdznsd04sy.jdznsd04sy_entity import Jdznsd04syEntity
from ._jdzntd01sy.jdzntd01sy_entity import Jdzntd01syEntity
from ._jdzntd02sy.jdzntd02sy_entity import Jdzntd02syEntity
from ._jdznxtd01sy.jdznxtd01sy_entity import Jdznxtd01syEntity
from ._jdznxtd02sy.jdznxtd02sy_entity import Jdznxtd02syEntity
from ._jdznxtd03sy.jdznxtd03sy_entity import Jdznxtd03syEntity

__all__ = [
    "Jdznsd01syEntity",
    "Jdznsd02syEntity",
    "Jdznsd03syEntity",
    "Jdznsd04syEntity",
    "Jdzntd01syEntity",
    "Jdzntd02syEntity",
    "Jdznxtd01syEntity",
    "Jdznxtd02syEntity",
    "Jdznxtd03syEntity",
]
