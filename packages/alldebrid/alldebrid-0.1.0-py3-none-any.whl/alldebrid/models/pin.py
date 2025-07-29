from typing import Optional

from attrs import define


@define(kw_only=True)
class PinGet:
    pin: str
    check: str
    expires_in: int
    user_url: str
    base_url: str
    check_url: str


@define(kw_only=True)
class PinCheck:
    activated: bool
    expires_in: int
    apikey: Optional[str]
