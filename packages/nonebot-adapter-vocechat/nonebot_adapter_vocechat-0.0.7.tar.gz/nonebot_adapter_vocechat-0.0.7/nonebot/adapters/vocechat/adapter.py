from nonebot import get_plugin_config
from nonebot.drivers import (
    Request,
    ASGIMixin,
    HTTPClientMixin,
    HTTPServerSetup,
    URL
)
from nonebot.drivers import Response, Driver
from nonebot.internal.adapter import Adapter as BaseAdapter

from typing_extensions import override
from typing import Any, Dict, Optional

from .bot import Bot
from .config import Config
from .event import *
from .utils import log

class Adapter(BaseAdapter):
    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)

        self.adapter_config: Config = get_plugin_config(Config)

        for vocechat_bot in self.adapter_config.vocechat_bots:
            self.bot_connect(
                Bot(
                    adapter= self,
                    self_id= vocechat_bot.name,
                    user_id = vocechat_bot.user_id,
                    api_key= vocechat_bot.api_key,
                    server_base= vocechat_bot.server
                    )
                )

        self.setup()

    @classmethod
    @override
    def get_name(cls) -> str:
        """适配器名称"""
        return "VoceChat"

    def setup(self) -> None:
        if not isinstance(self.driver, ASGIMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} doesn't support asgi server!"
                f"{self.get_name()} Adapter need a asgi server driver to work."
            )
        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(
                f"Current driver {self.config.driver} does not support http client requests! "
                f"{self.get_name()} Adapter need a HTTPClient Driver to work."
            )

        self.setup_http_server(
            HTTPServerSetup(
                URL("/vocechat/webhook"),
                "POST",
                f"{self.get_name()} Webhook",
                self._handle_http,
            ),
        )
        self.setup_http_server(
            HTTPServerSetup(
                URL("/vocechat/webhook/"),
                "POST",
                f"{self.get_name()} Webhook Slash",
                self._handle_http,
            ),
        )

        self.setup_http_server(
            HTTPServerSetup(
                URL("/vocechat/webhook"),
                "GET",
                f"{self.get_name()} Webhook",
                self._handle_http,
            ),
        )
        self.setup_http_server(
            HTTPServerSetup(
                URL("/vocechat/webhook/"),
                "GET",
                f"{self.get_name()} Webhook Slash",
                self._handle_http,
            ),
        )

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        """`Adapter` 实际调用 api 的逻辑实现函数，实现该方法以调用 api。

        参数:
            api: API 名称
            data: API 数据
        """

        log("DEBUG", f"call api {api}")

        if _request := data.get("request", None):
            
            _request.headers["x-api-key"] = bot.api_key
            _request.url = URL(f"{bot.server_base}{_request.url}")

            return await self.request(_request)


    async def _handle_http(self, request: Request) -> Response:
        """处理VoceChat Webhook请求"""
        try:
            bot_name = request.url.query.get("bot")
            
            if not bot_name:
                return Response(status_code=404, content="Not Found")

            if request.method == "GET": # 添加机器人需要验证
                return Response(status_code=200)
            
            bot = self.bots.get(bot_name)

            if not bot:
                return Response(status_code=404, content="Not Found Bot")

            try:
                payload = request.json
            except ValueError:
                return Response(status_code=400, content="Invalid JSON")
            
            event = self._parse_event(payload, bot)

            if event:
                await bot.handle_event(event)

            return Response(status_code=200)
        
        except Exception as e:
            log("ERROR", "Error handling VoceChat webhook", Exception)
            return Response(status_code=500, content=str(e))

    def _parse_event(self, payload: Dict[str, Any], bot: Bot) -> Optional[Event]:
        """解析VoceChat事件"""
        try:
            # 基础事件字段
            event_data = {
                "created_at": payload.get("created_at", 0),
                "from_uid": payload.get("from_uid", 0),
                "mid": payload.get("mid", 0),
                "target": payload.get("target", {}),
                "self_uid": bot.user_id,  # 注入机器人自身ID
            }
            
            # 根据事件类型创建不同的事件对象
            detail = payload.get("detail", {})
            
            if isinstance(detail, dict):
                # 新消息事件
                if detail.get("type") == "normal":
                    event_data["detail"] = detail
                    
                    # 文件消息特殊处理
                    if detail.get("content_type") == "vocechat/file":
                        return FileMessageEvent.model_validate(event_data)
                    
                    return MessageNewEvent.model_validate(event_data)
                
                # 回复消息
                elif detail.get("type") == "reply":
                    event_data["detail"] = detail
                    event_data["reply_to_mid"] = detail.get("mid")
                    return MessageReplyEvent.model_validate(event_data)
            
            elif isinstance(detail, dict) and detail.get("type") == "reaction":
                reaction_detail = detail.get("detail", {})
                
                # 编辑消息
                if reaction_detail.get("type") == "edit":
                    event_data["detail"] = detail
                    return MessageEditEvent.model_validate(event_data)
                
                # 删除消息
                elif reaction_detail.get("type") == "delete":
                    event_data["detail"] = detail
                    return MessageDeleteEvent.model_validate(event_data)
            
            log("WARNING", f"Unknown event type: {payload}")
            return None
            
        except Exception as e:
            log("ERROR", "Error parsing VoceChat event", e)
            return None