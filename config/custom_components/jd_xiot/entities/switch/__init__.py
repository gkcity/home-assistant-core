"""Switch Entities for JingDong XIoT integration."""

from .jd._jdzn1kg01lf.jdzn1kg01lf_entity import Jdzn1kg01lfEntity
from .jd._jdzn1kg04lf.jdzn1kg04lf_entity import Jdzn1kg04lfEntity
from .jd._jdzn2kg02lf.jdzn2kg02lf_entity import Jdzn2kg02lfEntity1, Jdzn2kg02lfEntity2
from .jd._jdzn2kg05lf.jdzn2kg05lf_entity import Jdzn2kg05lfEntity1, Jdzn2kg05lfEntity2
from .jd._jdzn3kg03lf.jdzn3kg03lf_entity import (
    Jdzn3kg03lfEntity1,
    Jdzn3kg03lfEntity2,
    Jdzn3kg03lfEntity3,
)
from .jd._jdzn3kg06lf.jdzn3kg06lf_entity import (
    Jdzn3kg06lfEntity1,
    Jdzn3kg06lfEntity2,
    Jdzn3kg06lfEntity3,
)

__all__ = [
    "Jdzn1kg01lfEntity",
    "Jdzn1kg04lfEntity",
    "Jdzn2kg02lfEntity1",
    "Jdzn2kg02lfEntity2",
    "Jdzn2kg05lfEntity1",
    "Jdzn2kg05lfEntity2",
    "Jdzn3kg03lfEntity1",
    "Jdzn3kg03lfEntity2",
    "Jdzn3kg03lfEntity3",
    "Jdzn3kg06lfEntity1",
    "Jdzn3kg06lfEntity2",
    "Jdzn3kg06lfEntity3"
]
