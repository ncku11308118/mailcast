from pydantic import (
    BaseModel,
    Field,
)
from pydantic.types import NonNegativeInt


class Concurrency(BaseModel):
    interval: NonNegativeInt = Field(default=0)
