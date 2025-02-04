from typing import Optional
from pydantic import BaseModel

class Ratings(BaseModel):
    rating_average: Optional[float]
    rating_count: Optional[int]
    difficulty_average: Optional[float]
    difficulty_count: Optional[int]
    favorites_count: Optional[int]
    projects_count: Optional[int]