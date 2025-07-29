import itertools
from typing import Any, Iterable, Optional, Type, Union

from attrs import define, field

from .converter import JSON_CONVERTER
from .error import ErrorMessage


@define(kw_only=True)
class MagnetErrorURI:
    magnet: str
    error: ErrorMessage


@define(kw_only=True)
class MagnetErrorFile:
    file: str
    error: ErrorMessage


@define(kw_only=True)
class MagnetUploadURI:
    magnet: str
    name: str
    id: int
    hash: str
    size: int
    ready: bool


@define(kw_only=True)
class MagnetUploadFile:
    file: str
    name: str
    id: int
    hash: str
    size: int
    ready: bool


@define(kw_only=True)
class MagnetInstantURI:
    magnet: str
    hash: str
    instant: bool


@define(kw_only=True)
class MagnetLinkEntryNormal:
    path: str
    fname: str
    size: int


@define(kw_only=True)
class MagnetLinkEntry:
    n: str
    e: Optional[list["MagnetLinkEntry"]] = field(default=None)
    s: Optional[int] = field(default=None)

    @classmethod
    def parse(cls, v: dict[str, Any]):
        if "e" not in v:
            return MagnetLinkEntry(**v)
        v["e"] = [cls.parse(f) for f in v["e"]]
        return MagnetLinkEntry(**v)

    def walk(self, path: str) -> Iterable[MagnetLinkEntryNormal]:
        if self.e is not None:
            for entry in self.e:
                yield from entry.walk(path + self.n + "/")
        else:
            assert self.s is not None
            yield MagnetLinkEntryNormal(path=path, fname=self.n, size=self.s)


@define(kw_only=True)
class MagnetLink:
    link: str
    filename: str
    size: int
    files: list[MagnetLinkEntryNormal] = field(
        factory=list,
        converter=lambda x: list(itertools.chain(*(MagnetLinkEntry.parse(f).walk("") for f in x))),
    )


@define(kw_only=True)
class MagnetStatus:
    id: int
    filename: str
    size: int
    hash: str
    status: str
    statusCode: int
    downloaded: int
    uploaded: int
    seeders: int
    downloadSpeed: int
    uploadSpeed: int
    uploadDate: int
    completionDate: int
    links: list[MagnetLink]
    type: str
    notified: bool
    version: int


@define(kw_only=True)
class MagnetUploadFiles:
    files: list[Union[MagnetUploadFile, MagnetErrorFile]]


@define(kw_only=True)
class MagnetUploadURIs:
    magnets: list[Union[MagnetUploadURI, MagnetErrorURI]]


@define(kw_only=True)
class MagnetInstants:
    magnets: list[Union[MagnetInstantURI, MagnetErrorURI]]


@define(kw_only=True)
class MagnetStatusesList:
    magnets: list[MagnetStatus]


@define(kw_only=True)
class MagnetStatusesDict:
    magnets: dict[str, MagnetStatus]


@define(kw_only=True)
class MagnetStatusesOne:
    magnets: MagnetStatus


MagnetStatuses = MagnetStatusesDict | MagnetStatusesList | MagnetStatusesOne


def parse_magnet_status(data: Any, typ_: Type[Any]) -> MagnetStatuses:
    if isinstance(data["magnets"], list):
        return JSON_CONVERTER.structure(data, MagnetStatusesList)
    if isinstance(data["magnets"], dict):
        return JSON_CONVERTER.structure(data, MagnetStatusesDict)
    return JSON_CONVERTER.structure(data, MagnetStatusesOne)


JSON_CONVERTER.register_structure_hook(MagnetStatuses, parse_magnet_status)
