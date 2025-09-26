# main.py

import httpx
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register(
    name="random_poem",
    author="kuank",
    desc="一个在用户输入'/今日诗词'时，提供一句随机古诗的插件",
    version="1.0.1"
)
class PoemPlugin(Star):
    """
    随机古诗插件，响应'/古诗'指令。
    """

    def __init__(self, context: Context):
        super().__init__(context)
        # 遵循文档建议，使用异步库进行网络请求
        self.http_client = httpx.AsyncClient()

    @filter.command("今日诗词")
    async def get_random_poem(self, event: AstrMessageEvent):
        """这是一个获取随机古诗的指令"""
        poem_url = "https://v1.jinrishici.com/all.txt"
        try:
            # 发起异步GET请求
            response = await self.http_client.get(poem_url, timeout=15.0)
            # 如果请求失败（如404, 500等），则抛出异常
            response.raise_for_status()
            poem_content = response.text
            # 使用yield发送纯文本消息
            yield event.plain_result(poem_content)
        except httpx.RequestError as e:
            logger.error(f"请求随机古诗URL失败: {e}")
            yield event.plain_result("抱歉，获取古诗失败了，请稍后再试。")
        except Exception as e:
            logger.error(f"处理随机古诗时发生未知错误: {e}")
            yield event.plain_result("抱歉，插件出了一点问题，请联系管理员。")

    async def terminate(self):
        """当插件被卸载或停用时调用，用于资源清理。"""
        if not self.http_client.is_closed:
            await self.http_client.aclose()
        logger.info("随机古诗插件已停用，网络客户端已关闭。")