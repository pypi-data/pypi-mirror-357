import sys
import threading
import signal
import types
import time

from click import get_current_context
from robyn import Robyn
from aivk.api import FastAIVK
from aivk.api.setlogger import set_logger_style
from logging import getLogger
from .backend.aivkw import init


logger = getLogger("aivk.web")
set_logger_style(logger, "aivk_web")  # 设置日志样式为 aivk_web

exit_event = threading.Event()

def aivkw_exit(signum: int, frame: types.FrameType | None) -> None:
    logger.debug(f"收到退出信号: {signum}")
    exit_event.set()
    sys.exit(0)

@FastAIVK.meta
class AIVKW():
    id = "web"
    level = -1 #必须最后加载 且不允许同等级别模块一起加载

def run_server(aivkw: Robyn, host: str, port: int) -> None:
    try:
        aivkw.start(host=host, port=port)
    finally:
        exit_event.set()

@AIVKW.onLoad
async def onLoad() -> None:
    logger.info("AIVK Web loaded")
    ctx = get_current_context()
    host = ctx.obj.get('web_host', '0.0.0.0')
    port = ctx.obj.get('web_port', 10141)
    logger.debug(f"Starting AIVK Web on {host}:{port}")
    aivkw = await init()
    signal.signal(signal.SIGINT, aivkw_exit)
    signal.signal(signal.SIGTERM, aivkw_exit)

    logger.info("AIVK Web: 后端启动后连续两次Ctrl+C退出")
    server_thread = threading.Thread(
        target=run_server,
        args=(aivkw, host, port),
        daemon=True
    )
    server_thread.start()
    while not exit_event.is_set() and server_thread.is_alive():
        time.sleep(0.2)
    logger.info("AIVK Web: Bye bye!")
    sys.exit(0)

@AIVKW.onUnload
async def onUnload():
    logger.info("AIVK Web unloaded")
    exit_event.set()

