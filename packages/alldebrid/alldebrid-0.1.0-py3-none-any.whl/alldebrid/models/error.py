from attrs import define


@define(kw_only=True)
class ErrorMessage:
    code: str
    message: str
