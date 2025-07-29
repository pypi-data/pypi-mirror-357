from aivk.api import FastAIVK
from logging import getLogger
from .backend.aivkw import init

logger = getLogger("aivk.web")

@FastAIVK.meta
class AIVKW():
    id = "web"
    Level = 0

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

