from typing import TypeVar

from pydantic import BaseModel

M = TypeVar("M", bound="Message")

class Message(BaseModel):
    """
    Base class for user-defined message types supporting serialization and deserialization.

    Sub-class this with regular Pydantic field definitions — no extra boilerplate is required.
    Nested `Message` (or any `BaseModel`) types, lists, dicts, and built-ins are handled
    automatically.
    """

    def pack(self: M) -> bytes:
        """
        Serialize to a MessagePack byte string.

        :return: A MessagePack byte string.
        """
        ...

    @classmethod
    def unpack(cls: type[M], data: bytes) -> M:
        """
        Deserialize from bytes produced by :py:meth:`pack`.

        :param data: The bytes to deserialize.
        :return: The deserialized object.
        """
        ...
