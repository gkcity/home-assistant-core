"""Type definitions and utilities for JingDong XIoT integration."""

# 注册灯光实体类到jd_light_mapping中
from ._jdznsd01sy.jdznsd01sy_entity import Jdznsd01syEntity

__all__ = [
    "Jdznsd01syEntity",
]
