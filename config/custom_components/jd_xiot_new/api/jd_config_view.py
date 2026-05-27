"""JingDong Config API."""

import json
import logging

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

class JingdongConfigView(HomeAssistantView):
    """Jingdong Config Http Service."""
    url = "/api/jd_xiot_new/config"
    name = "api:jd_xiot_new:config"
    requires_auth = False  # 测试用，正式环境建议开启 auth

    async def get(self, request):
        """GET /api/jd_xiot_new/config."""
        hass = request.app["hass"]

        # 找到 jd_xiot_new 配置条目
        entries = hass.config_entries.async_entries("jd_xiot_new")
        if not entries:
            _LOGGER.debug("Not Found jd_xiot_new entries: %s", len(entries))
            return web.json_response({"error": "jd_xiot_new not found"}, status=404)

        entry = entries[0]
        # 关键修复：将 mappingproxy 转为普通字典
        entry_data = dict(entry.data) if entry.data else {}
        entry_options = dict(entry.options) if entry.options else {}

        return web.json_response({
            "entry_id": entry.entry_id,
            "data": entry_data,
            "options": entry_options
        })

    async def post(self, request):
        """POST /api/jd_xiot_new/config."""
        hass = request.app["hass"]
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "无效的 JSON 格式"},
                status=400
            )

        entries = hass.config_entries.async_entries("jd_xiot_new")
        if not entries:
            return web.json_response({"error": "jd_xiot_new not found"}, status=404)

        entry = entries[0]

        # 更新配置
        updates = {}
        if "data" in data:
            updates["data"] = data["data"]
        if "options" in data:
            updates["options"] = data["options"]

        try:
            # 执行更新
            await hass.config_entries.async_update_entry(
                entry,
                data=updates.get("data", entry.data),
                options=updates.get("options", entry.options)
            )

            # 重载集成生效
            await hass.config_entries.async_reload(entry.entry_id)

            return web.json_response({
                "status": "success",
                "message": "配置已更新并自动重载生效"
            })
        except HomeAssistantError as e:
            # 捕获更新过程中的异常，返回友好提示
            _LOGGER.error("Update jd_xiot_new config failed: %s", str(e))
            return web.json_response(
                {"error": f"更新配置失败: {e!s}"},
                status=500
            )


async def register_jd_config_api(hass):
    """Register jd config api."""
    hass.http.register_view(JingdongConfigView)
