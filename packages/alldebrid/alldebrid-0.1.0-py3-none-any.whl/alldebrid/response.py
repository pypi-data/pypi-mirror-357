from typing import Generic, Literal, Optional, TypeVar, Union, cast

from attrs import define

from .models.error import ErrorMessage

T = TypeVar("T")


class ApiError(Exception):
    pass


@define
class Response(Generic[T]):
    status: Union[Literal["success"], Literal["error"]]
    data: Optional[T] = None
    error: Optional[ErrorMessage] = None

    def __attrs_post_init__(self):
        if self.status == "success" and self.data is None:
            raise ValueError("data missing when response is successful")
        elif self.status == "error" and self.error is None:
            raise ValueError("error missing when response is error")

    def unwrap(self) -> T:
        if self.status == "success":
            return cast(T, self.data)
        else:
            raise ApiError(self.error)
