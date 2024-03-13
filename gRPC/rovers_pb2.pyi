from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class mapRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class mapReply(_message.Message):
    __slots__ = ("map", "rows", "cols")
    MAP_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    COLS_FIELD_NUMBER: _ClassVar[int]
    map: _containers.RepeatedScalarFieldContainer[str]
    rows: int
    cols: int
    def __init__(self, map: _Optional[_Iterable[str]] = ..., rows: _Optional[int] = ..., cols: _Optional[int] = ...) -> None: ...

class commandStreamRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class commandStreamReply(_message.Message):
    __slots__ = ("cmds",)
    CMDS_FIELD_NUMBER: _ClassVar[int]
    cmds: str
    def __init__(self, cmds: _Optional[str] = ...) -> None: ...

class serialNumRequest(_message.Message):
    __slots__ = ("id", "i", "j")
    ID_FIELD_NUMBER: _ClassVar[int]
    I_FIELD_NUMBER: _ClassVar[int]
    J_FIELD_NUMBER: _ClassVar[int]
    id: str
    i: int
    j: int
    def __init__(self, id: _Optional[str] = ..., i: _Optional[int] = ..., j: _Optional[int] = ...) -> None: ...

class serialNumReply(_message.Message):
    __slots__ = ("serialNum",)
    SERIALNUM_FIELD_NUMBER: _ClassVar[int]
    serialNum: str
    def __init__(self, serialNum: _Optional[str] = ...) -> None: ...

class completedRequest(_message.Message):
    __slots__ = ("id", "code")
    ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    id: str
    code: int
    def __init__(self, id: _Optional[str] = ..., code: _Optional[int] = ...) -> None: ...

class completedReply(_message.Message):
    __slots__ = ("ack",)
    ACK_FIELD_NUMBER: _ClassVar[int]
    ack: str
    def __init__(self, ack: _Optional[str] = ...) -> None: ...

class pinRequest(_message.Message):
    __slots__ = ("id", "serialNum", "pin")
    ID_FIELD_NUMBER: _ClassVar[int]
    SERIALNUM_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    id: str
    serialNum: str
    pin: str
    def __init__(self, id: _Optional[str] = ..., serialNum: _Optional[str] = ..., pin: _Optional[str] = ...) -> None: ...

class pinReply(_message.Message):
    __slots__ = ("ack",)
    ACK_FIELD_NUMBER: _ClassVar[int]
    ack: str
    def __init__(self, ack: _Optional[str] = ...) -> None: ...
