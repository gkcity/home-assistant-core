
"""Cover DeviceJdzhp01qs."""

import logging
from typing import Any

from custom_components.jd_xiot_new.api.const import DOMAIN
from custom_components.jd_xiot_new.api.jd_client import JingDongClient
from custom_components.jd_xiot_new.api.typedef.joy_device_detail import JoyDeviceDetail
from custom_components.jd_xiot_new.entities.mediaplayer.jd_media_player_mapping import (
    register_media_player_entity,
)
from xiot_core.support.typedef.controller.device_controller import DeviceController
from xiot_core_device_controller.jd._gateway._jdzhp01qs.device_jdzhp01qs import (
    DeviceJdzhp01qs,
)

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.helpers.device_registry import DeviceInfo

_LOGGER = logging.getLogger(__name__)


@register_media_player_entity
class DeviceJdzhp01qsEntity(MediaPlayerEntity):
    """DeviceJdzhp01qs Entity."""

    TYPE: str = DeviceJdzhp01qs.TYPE

    def __init__(
        self,
        controller: DeviceController,
        client: JingDongClient,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Cover Entity."""
        self._client: JingDongClient = client
        self._detail: JoyDeviceDetail = detail
        self._device: DeviceJdzhp01qs | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_new_{controller.did}"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        # 支持：打开、关闭、暂停、百分比位置
        self._attr_supported_features = (
            MediaPlayerEntityFeature.PLAY_MEDIA
                # MediaPlayerEntityFeature.PLAY
                # | MediaPlayerEntityFeature.PAUSE
                # | MediaPlayerEntityFeature.STOP
                # | MediaPlayerEntityFeature.VOLUME_SET
                # | MediaPlayerEntityFeature.VOLUME_MUTE
                # | MediaPlayerEntityFeature.PLAY_MEDIA
        )

        # 初始状态
        self._attr_state: MediaPlayerState = MediaPlayerState.IDLE
        self._attr_volume_level: float = 0.5  # 初始音量50%
        self._attr_is_volume_muted: bool = False
        self._attr_media_type: MediaType = MediaType.MUSIC
        self._attr_media_title: str | None = None
        self._attr_media_artist: str | None = None
        self._attr_source_list: list[str] = ["蓝牙", "本地", "网络电台", "USB"]  # 音源列表
        self._attr_source: str = "本地"  # 当前音源

        # 设备信息
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, detail["did"])},
            name = detail['additional']['name'],
            manufacturer = "京东小家",
            model = f"{detail["summary"].type.model}",
        )

        # 绑定设备控制器
        if isinstance(controller, DeviceJdzhp01qs):
            self._device = controller
            self._device.set_operator(
                client.get_property,
                client.set_property,
                client.invoke_action,
                detail["userDeviceId"]
            )
            _LOGGER.info("初始化媒体播放器成功: %s", self._attr_unique_id)
        else:
            self._device = None
            self._attr_available = False
            _LOGGER.error("媒体播放器控制器类型不匹配: %s", type(controller).__name__)

    @property
    def extra_state_attributes(self):
        """Extra Attributes."""
        return {
            "ip": self._client.ip,
        }

    # # ------------------------------------------------------
    # # 核心：播放媒体
    # # ------------------------------------------------------
    # async def async_media_play(self, **kwargs: Any) -> None:
    #     """Play."""
    #     _LOGGER.info("Play")
    #
    #     self._attr_state = MediaPlayerState.PLAYING
    #
    #     try:
    #         # await self._device.service_voice().action_say().invoke(0, media_url)
    #         self._attr_state = MediaPlayerState.PLAYING
    #     except ValueError as e:
    #         _LOGGER.error("Play failed: %s", e)
    #     self.async_write_ha_state()

    # ------------------------------------------------------
    # 【关键】真正能接收 URL 的方法
    # ------------------------------------------------------
    async def async_play_media(
            self,
            media_type: str,
            media_id: str,
            **kwargs: Any
    ) -> None:
        """Play Media."""

        _LOGGER.info("Play Media: %s", media_type)
        _LOGGER.info("URL: %s", media_id)  # <--- 这里就是你要的 URL！

        try:
            # 直接把 URL 传给设备
            await self._device.service_voice().action_say().invoke(0, media_id)
            self._attr_state = MediaPlayerState.PLAYING
            self.async_write_ha_state()
        except ValueError as e:
            _LOGGER.error("播放失败: %s", e)

    # ------------------------------------------------------
    # 核心：暂停媒体
    # ------------------------------------------------------
    async def async_media_pause(self, **kwargs: Any) -> None:
        """Pause."""
        _LOGGER.info("Pause: %s", self._attr_unique_id)
        try:
            # await self._device.service_media().action_pause().invoke()
            self._attr_state = MediaPlayerState.PAUSED
        except ValueError as e:
            _LOGGER.error("暂停媒体失败: %s", e)
        self.async_write_ha_state()

    # ------------------------------------------------------
    # 核心：停止媒体
    # ------------------------------------------------------
    async def async_media_stop(self, **kwargs: Any) -> None:
        """Stop."""
        _LOGGER.info("Stop: %s", self._attr_unique_id)
        try:
            # await self._device.service_media().action_stop().invoke()
            self._attr_state = MediaPlayerState.STANDBY
        except ValueError as e:
            _LOGGER.error("停止媒体失败: %s", e)
        self.async_write_ha_state()

    # # ------------------------------------------------------
    # # 核心：下一曲
    # # ------------------------------------------------------
    # async def async_media_next_track(self, **kwargs: Any) -> None:
    #     """下一曲"""
    #     _LOGGER.info("媒体播放器下一曲: %s", self._attr_unique_id)
    #     try:
    #         await self._device.service_media().action_next_track().invoke()
    #         # 可根据实际设备返回更新媒体信息
    #         # self._attr_media_title = "新曲目名称"
    #     except ValueError as e:
    #         _LOGGER.error("下一曲失败: %s", e)
    #     self.async_write_ha_state()
    #
    # # ------------------------------------------------------
    # # 核心：上一曲
    # # ------------------------------------------------------
    # async def async_media_previous_track(self, **kwargs: Any) -> None:
    #     """上一曲"""
    #     _LOGGER.info("媒体播放器上一曲: %s", self._attr_unique_id)
    #     try:
    #         await self._device.service_media().action_prev_track().invoke()
    #         # 可根据实际设备返回更新媒体信息
    #     except ValueError as e:
    #         _LOGGER.error("上一曲失败: %s", e)
    #     self.async_write_ha_state()

    # ------------------------------------------------------
    # 核心：设置音量（0.0~1.0）
    # ------------------------------------------------------
    async def async_set_volume_level(self, volume: float, **kwargs: Any) -> None:
        """SetVolume."""
        _LOGGER.info("设置媒体播放器音量: %s -> %s", self._attr_unique_id, volume)
        try:
            # 转换为设备需要的音量范围（如0~100）
            # volume_percent = int(volume * 100)
            # await self._device.service_media().property_volume().set(volume_percent)
            self._attr_volume_level = volume
            self._attr_is_volume_muted = False  # 调整音量时取消静音
        except ValueError as e:
            _LOGGER.error("SetVolume Failed: %s", e)
        self.async_write_ha_state()

    # ------------------------------------------------------
    # 核心：静音/取消静音
    # ------------------------------------------------------
    async def async_mute_volume(self, mute: bool, **kwargs: Any) -> None:
        """Mute."""
        _LOGGER.info("Mute: %s -> %s", self._attr_unique_id, mute)
        try:
            # await self._device.service_media().property_mute().set(mute)
            self._attr_is_volume_muted = mute
        except ValueError as e:
            _LOGGER.error("Mute Failed: %s", e)
        self.async_write_ha_state()

    # # ------------------------------------------------------
    # # 核心：切换音源
    # # ------------------------------------------------------
    # async def async_select_source(self, source: str, **kwargs: Any) -> None:
    #     """切换音源"""
    #     _LOGGER.info("切换媒体播放器音源: %s -> %s", self._attr_unique_id, source)
    #     if source not in self._attr_source_list:
    #         _LOGGER.error("不支持的音源: %s", source)
    #         return
    #
    #     try:
    #         # 转换音源名称为设备识别的编码（示例）
    #         source_code = {
    #             "蓝牙": "bluetooth",
    #             "本地": "local",
    #             "网络电台": "radio",
    #             "USB": "usb"
    #         }.get(source, "local")
    #         await self._device.service_media().property_source().set(source_code)
    #         self._attr_source = source
    #     except ValueError as e:
    #         _LOGGER.error("切换音源失败: %s", e)
    #     self.async_write_ha_state()

    # ------------------------------------------------------
    # HA 自动刷新状态
    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update."""
        _LOGGER.debug("Update: %s", self._attr_unique_id)

        if not self._device:
            self._attr_available = False
            return

        self._attr_available = True

        # try:
        #     # 获取当前播放状态
        #     play_state = await self._device.service_media().property_play_state().get()
        #     if play_state == "playing":
        #         self._attr_state = MediaPlayerState.PLAYING
        #     elif play_state == "paused":
        #         self._attr_state = MediaPlayerState.PAUSED
        #     elif play_state == "stopped":
        #         self._attr_state = MediaPlayerState.STOPPED
        #     else:
        #         self._attr_state = MediaPlayerState.IDLE
        #
        #     # 获取当前音量（转换为0.0~1.0）
        #     volume = await self._device.service_media().property_volume().get()
        #     self._attr_volume_level = volume / 100 if volume is not None else 0.5
        #
        #     # 获取静音状态
        #     mute = await self._device.service_media().property_mute().get()
        #     self._attr_is_volume_muted = mute if mute is not None else False
        #
        #     # 获取当前媒体信息
        #     self._attr_media_title = await self._device.service_media().property_song_name().get()
        #     self._attr_media_artist = await self._device.service_media().property_singer().get()
        #
        #     # 获取当前音源
        #     source_code = await self._device.service_media().property_source().get()
        #     source_map = {
        #         "bluetooth": "蓝牙",
        #         "local": "本地",
        #         "radio": "网络电台",
        #         "usb": "USB"
        #     }
        #     self._attr_source = source_map.get(source_code, "本地")
        #
        # except ValueError as e:
        #     _LOGGER.error("更新媒体播放器状态失败: %s", e)
        #     self._attr_available = False

        self.async_write_ha_state()
