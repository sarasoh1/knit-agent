from typing import Optional
from pydantic import BaseModel, model_validator

class PatternNeedleSize(BaseModel):
    id: int
    us: str
    metric: float
    is_knit: bool
    is_crochet: bool
    name: str
    pretty_metric: str
    hook: Optional[str]

    @model_validator(mode='after')
    def check_hook_present_if_crochet(self):
        """Check that a hook size is present if the pattern is crochet.

        Raises:
            ValueError: If the pattern is crochet and a hook size is not present.
        """
        if self.is_crochet and not self.hook:
            raise ValueError('Hook size is required for crochet patterns')



