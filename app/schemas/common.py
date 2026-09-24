from pydantic import BaseModel

__all__ = ["ErrorResponse"]


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
