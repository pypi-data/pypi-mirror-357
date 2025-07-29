from aivk.api import FastAIVK
from logging import getLogger
from .backend.aivkw import init

logger = getLogger("aivk.web")

@FastAIVK.meta
class AIVKW():
    id = "web"
    level = -1 #必须最后加载 且不允许同等级别模块一起加载

@AIVKW.onLoad
async def onLoad():
    logger.info("AIVK Web loaded")
    aivkw = await init()
    aivkw.start(
        host="0.0.0.0",
        port=10141
    )

@AIVKW.onUnload
async def onUnload():
    logger.info("AIVK Web unloaded")

