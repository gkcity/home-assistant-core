"""Switch Entities for JingDong XIoT integration."""

from .jd._jdzn1kg01lf.jdzn1kg01lf_entity import Jdzn1kg01lfEntity
from .jd._jdzn1kg04lf.jdzn1kg04lf_entity import Jdzn1kg04lfEntity
from .jd._jdzn2kg02lf.jdzn2kg02lf_entity import Jdzn2kg02lfEntity1, Jdzn2kg02lfEntity2

__all__ = [
    "Jdzn1kg01lfEntity",
    "Jdzn1kg04lfEntity",
    "Jdzn2kg02lfEntity1",
    "Jdzn2kg02lfEntity2"
]
