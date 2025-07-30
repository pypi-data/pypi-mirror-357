import asyncio
import pydantic

from websockets import ServerConnection
from typing import Any, Iterable, Union, Optional, TYPE_CHECKING

from .packets import Packet
from .enum import PacketSource, ConnectionState
from .exceptions import MessageError

if TYPE_CHECKING:
    from .handler import WebSocketHandler


class ClientConnection:
    """
    Represents a single client connection to the WebSocket server.

    This class wraps the underlying `websockets.ServerConnection` and provides
    convenient access to session-specific state and channel management.
    It allows setting and getting attributes dynamically, which are stored
    in an internal `session_state` dictionary.
    """

    def __init__(
        self, websocket_protocol: ServerConnection, handler: "WebSocketHandler"
    ) -> None:
        object.__setattr__(self, "_protocol", websocket_protocol)
        object.__setattr__(self, "_handler", handler)
        object.__setattr__(self, "connection_state", ConnectionState.CONNECTED)
        object.__setattr__(self, "session_state", dict())

    @property
    def subscribed_channel(self) -> set[str]:
        """A property that gets the authoritative list of channels from the handler."""
        return self._handler.reversed_channels.get(self, set())

    async def send(self, data: Union[str, bytes, Packet]) -> None:
        """
        Sends data over the connection. This is a "smart" method that
        ensures all data is sent in a structured Packet format.

        - If given a Pydantic `Packet` object, it serializes and sends it.
        - If given a raw `str` or `bytes`, it automatically wraps it in a
        default `Packet` before serializing and sending.
        """

        packet: Packet

        if isinstance(data, Packet):
            packet = data

        elif isinstance(data, (str, bytes)):
            packet = Packet(
                data=data,
                source=PacketSource.CUSTOM,
                channel=None,
            )

        else:
            raise TypeError(
                "Data for send must be a Packet, str, or bytes, not %s" % type(data)
            )

        await self._protocol.send(packet.model_dump_json())

    async def recv(self, timeout: Optional[float] = 30.0) -> Packet:
        """
        Receives the next message and parses it into a validated Packet object.

        Args:
            timeout: Max seconds to wait for a message. Defaults to 30.

        Raises:
            TypeError: If an on_receive_callback is active.
            ConnectionError: If the client is not connected.
            TimeoutError: If no message is received within the timeout period.
            MessageError: If the received data fails to parse as a valid Packet.

        Returns:
            A validated Packet object.
        """

        # if self.on_receive_callback:
        #     raise TypeError("Cannot use manual recv() when an on_receive callback is active.")
        packet: Packet

        if not self._protocol or self.connection_state == ConnectionState.DISCONNECTED:
            raise ConnectionError("Cannot receive data: client is not connected.")

        try:
            raw_data = await asyncio.wait_for(self._protocol.recv(), timeout=timeout)

            try:
                packet = Packet.model_validate_json(raw_data)
                return packet

            except pydantic.ValidationError as err:
                raise MessageError(
                    "Received malformed or invalid packet data."
                ) from err

        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Receive operation timed out after {timeout} seconds."
            ) from None

    def subscribe(self, channel: Union[str, Iterable[str]]) -> None:
        """A shortcut method for this connection to join one or more channels."""
        self._handler.subscribe(self, channel)

    def unsubscribe(self, channel: Union[str, Iterable[str]]) -> None:
        """A shortcut method for this connection to leave one or more channels."""
        self._handler.unsubscribe(self, channel)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Called when setting an attribute. All assignments are redirected
        to the session_state dictionary.
        """
        # self.session_state[name] = value
        self.__dict__["session_state"][name] = value

    def __getattr__(self, name: str) -> Any:
        """
        Called when getting an attribute. The lookup order is:
            1. Check the session_state dictionary.
            2. Check the underlying websocket protocol object.
            3. Raise an AttributeError if not found anywhere.
        """
        try:
            return self.__dict__["session_state"][name]
        except KeyError:
            try:
                return getattr(self._protocol, name)
            except AttributeError:
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{name}'"
                ) from None

    def __delattr__(self, name: str) -> None:
        """Called when deleting an attribute (e.g., `del connection.username`)."""

        if name in self.__dict__["session_state"]:
            del self.__dict__["session_state"][name]
        else:
            super().__delattr__(name)

    def __setitem__(self, name: str, value: Any) -> None:
        """Allows setting state via `connection['key'] = value`."""
        self.__setattr__(name, value)

    def __delitem__(self, name: str) -> None:
        """Allows deleting state via `del connection['key']`."""
        self.__delattr__(name)

    # --- The missing piece ---
    def __getitem__(self, name: str) -> Any:
        """Allows reading state via `value = connection['key']`."""
        try:
            return self.__getattr__(name)
        except AttributeError:
            # Raise a KeyError for dictionary-style access, which is the expected behavior.
            raise KeyError(name) from None

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__}("
            f"uid={self.uid}, "
            f"remote_address='{self.remote_address}', "
            f"state={self.session_state}"
            f")>"
        )

    def __hash__(self):
        return hash(self._protocol)

    def __eq__(self, other):
        return isinstance(other, ClientConnection) and self._protocol == other._protocol
