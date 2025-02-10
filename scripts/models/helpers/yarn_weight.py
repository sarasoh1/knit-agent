from pydantic import BaseModel
from typing import Optional


class YarnWeight(BaseModel):
    name: str
    ply: Optional[str]
    wpi: Optional[str]
