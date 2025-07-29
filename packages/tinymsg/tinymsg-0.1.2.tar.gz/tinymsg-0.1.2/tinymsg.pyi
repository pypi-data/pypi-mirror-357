from typing import Self

from pydantic import BaseModel

class Message(BaseModel):
    """
    Base class for user-defined message types supporting serialization and deserialization.

    Sub-class this with regular Pydantic field definitions — no extra boilerplate is required.
    Nested `Message` (or any `BaseModel`) types, lists, dicts, and built-ins are handled
    automatically.
    """

    def pack(self: Self) -> bytes:
        """
        Serialize to a MessagePack byte string.

        :return: A MessagePack byte string.
        """
        ...

    @classmethod
    def unpack(cls: type[Self], data: bytes) -> Self:
        """
        Deserialize from bytes produced by :py:meth:`pack`.

        :param data: The bytes to deserialize.
        :return: The deserialized object.
        """
        ...
