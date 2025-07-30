import json
import time
import uuid

from typing import Optional
from pydantic import BaseModel, Field
from .enum import PacketSource


class Packet(BaseModel):
    """
    A structured data packet for WebSocket communication.
    """

    data: str | bytes
    source: PacketSource
    channel: Optional[str] = ""
    timestamp: float = Field(default_factory=time.time)
    correlation_id: Optional[uuid.UUID] = None

    @property
    def length(self) -> int:
        """A computed property that returns the length of the data payload."""

        if isinstance(self.data, (str, bytes)):
            return len(self.data)

        try:
            return len(json.loads(self.data))

        except TypeError:
            return 0
