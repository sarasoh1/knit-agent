from pydantic import BaseModel
from typing import Optional
from backend.models.pattern_query import PatternQuery


class RawPatternQuery(BaseModel):
    craft_type: str
    clothing_category: str
    pattern_attributes: Optional[str]
    yarn_weight: Optional[str]

    def clean_query(self) -> PatternQuery:
        """
        Transforms the raw pattern query from front end
        to be used in the backend

        Returns:
            PatternQuery: PatternQuery to be used on the backend
        """
        return PatternQuery(
            craft_type=self.craft_type,
            clothing_category=self.clothing_category,
            pattern_attributes=(
                [attr.strip() for attr in self.pattern_attributes.split(",")]
                if self.pattern_attributes
                else None
            ),
            yarn_weight=self.yarn_weight,
        )
