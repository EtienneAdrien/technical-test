import enum

from pydantic import BaseModel, ConfigDict


class Status(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


class APIReturn(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: Status
    message: str


class Success(APIReturn):
    status: Status = Status.SUCCESS


class Failed(APIReturn):
    status: Status = Status.FAILED


class UnexpectedError(APIReturn):
    status: Status = Status.FAILED
    message: str = "An unexpected error happened"
