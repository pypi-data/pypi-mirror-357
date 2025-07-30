from datetime import datetime, timedelta

from fastapi import WebSocket

from MeowthLogger.constants import REQUEST_DATESTRING_FORMAT
from MeowthLogger.utilities.dates import set_null_minutes

from ..log_streaming.stream_manager import Stream


class StreamManager(Stream):
    def __init__(self, loop) -> None:  # noqa: ANN001
        self.active_connections: list[WebSocket] = []
        self.loop = loop

    @property
    def _prev_logs(self) -> str:
        prev_date = datetime.now()
        prev_date = set_null_minutes(prev_date) - timedelta(hours=1)
        prev_date = datetime.strftime(prev_date, REQUEST_DATESTRING_FORMAT)
        file = self.logger.stream_logs(date_from=prev_date)

        logs_lines = []
        while True:
            line = file.readline().decode("utf-8")
            if not line:
                break
            logs_lines.append(line)
        return "ROOTMSG" + "".join([line for line in logs_lines[-1000:]])

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text(self._prev_logs)
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    def write(self, message: str) -> None:
        self.loop.create_task(self.broadcast(message))

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)
