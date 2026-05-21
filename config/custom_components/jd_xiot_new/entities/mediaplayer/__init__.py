"""MediaPlayer entities for JingDong XIoT integration."""

from .jd._jdzhp01qs.jdzhp01qs_entity import DeviceJdzhp01qsEntity
from .jd._jdzhp02qs.jdzhp02qs_entity import DeviceJdzhp02qsEntity

__all__ = [
    "DeviceJdzhp01qsEntity",
    "DeviceJdzhp02qsEntity",
]
