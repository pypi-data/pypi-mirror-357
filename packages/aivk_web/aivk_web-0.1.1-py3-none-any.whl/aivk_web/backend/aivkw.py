import asyncio
import sqlite3
from robyn import Robyn
from robyn.openapi import OpenAPI, OpenAPIInfo, Contact, License, Server, ExternalDocumentation, Components
from aivk.api import AivkContext

async def init():
    ctx = AivkContext()
    info = OpenAPIInfo(
        title="AIVK Web",
        version="0.1.0",
        description="AIVK的web拓展",
        termsOfService="https://github.com/LIghtJUNction/AIVKW",
        contact=Contact(
            name="AIVK Team",
            url="https://github.com/LIghtJUNction/AIVKW",
            email="lightjuncion.me@gmail.com"
        ),
        license=License(
            name="MIT",
            url="https://opensource.org/licenses/MIT"
        ),
        servers=[Server(url="http://localhost:10141", description="本地开发服务器")],
        externalDocs=ExternalDocumentation(
            description="AIVK Web Documentation",
            url="https://github.com/LIghtJUNction/AIVKW/docs"
        ),
        components=Components()
    )

    aivkw_openapi = OpenAPI(
        info=info
    )

    aivkw = Robyn(
        __file__,
        openapi=aivkw_openapi,
    )

    async with ctx.env("web") as fs:
        @aivkw.get("/")
        def index(): # type: ignore
            db = fs.data / "aivkw.db"
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS test")
            cur.execute("CREATE TABLE test(column_1, column_2)")
            res = cur.execute("SELECT name FROM sqlite_master")
            th = res.fetchone()
            table_name = th[0]
            return f"Hello World! {table_name}"
        



    return aivkw


# 导出至 __init__.py : onLoad 

if __name__ == "__main__":
    aivkw = asyncio.run(init())
    aivkw.start(host="0.0.0.0", port=10141)
