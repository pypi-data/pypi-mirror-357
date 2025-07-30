"""
A robust, asyncio-based WebSocket library providing easy-to-use
client and server abstractions.
"""

__version__ = "0.1.0"
__author__ = "LeftandRights"
__license__ = "MIT"

from .handler import DefaultWebSocketHandler, WebSocketHandler
from .enum import ServerState, ConnectionState, PacketSource
from .typing import CertificatePaths
from .connection import ClientConnection
from .packets import Packet
from .websocket import (
    server as WebSocketServer,
    client as WebSocketClient,
)

__all__ = [
    # Handler
    "DefaultWebSocketHandler",
    "WebSocketHandler",
    # Enums
    "ServerState",
    "ConnectionState",
    "PacketSource",
    # Typing
    "CertificatePaths",
    # Connection
    "ClientConnection",
    # Packets
    "Packet",
    # Websocket
    "WebSocketServer",
    "WebSocketClient",
]
