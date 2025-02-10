from typing import Optional, List
from pydantic import BaseModel
from models.helpers.pattern_needle_size import PatternNeedleSize


class Gauge(BaseModel):
    gauge: Optional[float]
    gauge_divisor: Optional[int]
    gauge_pattern: Optional[str]
    row_gauge: Optional[float]
    yardage: Optional[int]
    yardage_max: Optional[int]
    gauge_description: Optional[str]
    yarn_weight_description: Optional[str]
    yardage_description: Optional[str]
    pattern_needle_sizes: Optional[List[PatternNeedleSize]]

    # TODO: Add validation for gauges
