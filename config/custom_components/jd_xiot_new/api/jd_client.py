"""Abstract JingDong Client."""

from abc import ABC, abstractmethod

from aiohttp import ClientSession, ClientTimeout
from xiot_core.spec.typedef.operation.action_operation import ActionOperation
from xiot_core.spec.typedef.operation.property_operation import PropertyOperation

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .jd_config_data import JdConfigData
from .typedef.joy_device_detail import JoyDeviceDetail
from .typedef.joy_house import JoyHouse


class JingDongClient(ABC):
    """JingDong Client."""

    def __init__(self, hass: HomeAssistant, data: JdConfigData) -> None:
        """Initialize the API client."""
        self.__hass = hass
        self.__data: JdConfigData = data
        self.__timeout = ClientTimeout(connect=3.0, sock_read=3.0, total=6.0)
        self.__session = aiohttp_client.async_get_clientsession(hass)

    @property
    def ip(self) -> str:
        """Get IP Address."""
        return self.__data.screen_ip

    @property
    def data(self) -> JdConfigData:
        """Get Config Data."""
        return self.__data

    @property
    def session(self) -> ClientSession:
        """Get Session."""
        return self.__session

    @property
    def timeout(self) -> ClientTimeout:
        """Get Timeout."""
        return self.__timeout

    @abstractmethod
    async def async_get_houses(self) -> tuple[bool, list[JoyHouse]]:
        """Get Houses."""

    @abstractmethod
    async def async_get_devices(self) -> list[JoyDeviceDetail]:
        """Get Devices."""

    @abstractmethod
    async def async_get_devices_info(self, deviceIds: list[str]) -> list[JoyDeviceDetail]:
        """Get Device."""

    @abstractmethod
    async def set_property(self, p: PropertyOperation) -> PropertyOperation:
        """Set Property."""

    @abstractmethod
    async def get_property(self, p: PropertyOperation) -> PropertyOperation:
        """Get Property."""

    @abstractmethod
    async def invoke_action(self, a: ActionOperation) -> ActionOperation:
        """Invoke Action."""
