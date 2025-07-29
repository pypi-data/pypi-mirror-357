from __future__ import annotations

from typing import Optional, Union

from attrs import define

from .error import ErrorMessage


@define(kw_only=True)
class LinkInfoError:
    link: str
    error: ErrorMessage


@define(kw_only=True)
class LinkInfo:
    link: str
    filename: str
    size: int
    host: str
    hostDomain: str


@define(kw_only=True)
class LinkInfos:
    infos: list[Union[LinkInfo, LinkInfoError]]


@define(kw_only=True)
class LinkRedirect:
    links: list[str]


@define(kw_only=True)
class LinkUnlockStream:
    id: str
    ext: str
    quality: str
    filesize: int
    name: str
    proto: Optional[str]
    link: Optional[str]


@define(kw_only=True)
class LinkUnlock:
    id: str
    filename: str
    host: str
    hostDomain: Optional[str] = None
    filesize: int
    link: Optional[str] = None
    streams: Optional[list[LinkUnlockStream]] = None
    delayed: Optional[str] = None


@define(kw_only=True)
class LinkStream:
    link: str
    filename: str
    filesize: int
    delayed: Optional[int]


@define(kw_only=True)
class LinkDelayed:
    status: int
    time_left: int
    link: Optional[str]
