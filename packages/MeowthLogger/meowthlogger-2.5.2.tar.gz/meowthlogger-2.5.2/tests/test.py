import asyncio

from fastapi import FastAPI
from uvicorn import Config, Server

from MeowthLogger import Logger
from MeowthLogger.utilities.fastapi.log_stream import StreamManager
from MeowthLogger.utilities.fastapi.views import get_log_stream_views_router


loop = asyncio.new_event_loop()
managa = StreamManager(loop)
api = FastAPI()


@api.get("/")
async def home() -> dict[str, bool]:
    return {"ok": True}


logger = Logger(use_files=True, use_uvicorn=True, stream=managa)
logger.info("TEST")


api.include_router(get_log_stream_views_router(logger))


config = Config(app=api, host="0.0.0.0", log_config=None)

server = Server(config)


async def main() -> None:
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
