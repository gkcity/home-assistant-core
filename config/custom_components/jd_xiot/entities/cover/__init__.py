"""Light entities for JingDong XIoT integration."""

# 注册灯光实体类到jd_light_mapping中
from .jd._jdzncl01dy.jdzncl01dy_entity import Jdzncl01dyEntity

__all__ = [
    "Jdzncl01dyEntity",
]
