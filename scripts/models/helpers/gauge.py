from typing import Optional, List
from pydantic import BaseModel
from models.helpers.pattern_needle_size import PatternNeedleSize
from models.helpers.yarn_weights import YarnWeights

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
    def map_yarn_weight(self):
        """
        Cleans the yarn weight description and maps it to a weight class

        Returns:
            Yarn Weight class
        """
        yarn_weight = self.yarn_weight_description.lower()
        if "light fingering" in yarn_weight:
            return YarnWeights.FINE
        
        if "super bulky" in yarn_weight:
            return YarnWeights.SUPER_BULKY
        
        clean_yarn_weight = yarn_weight.split(" ")[0]
        return YarnWeights.get_group(clean_yarn_weight)
