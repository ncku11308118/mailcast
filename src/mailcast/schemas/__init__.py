from pydantic import BaseModel


class HardSchema(BaseModel, extra="forbid"): ...


class SoftSchema(BaseModel, extra="allow"): ...
