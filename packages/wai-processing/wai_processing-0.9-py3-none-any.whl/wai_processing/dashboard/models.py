from pydantic import BaseModel


class ErrorRequest(BaseModel):
    dataset: str
    page: int


class HealthCheck(BaseModel):
    status: str = "OK"
