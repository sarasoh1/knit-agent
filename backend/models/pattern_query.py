from typing import Optional, List
from pydantic import BaseModel
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
    FilterCondition,
)


class PatternQuery(BaseModel):
    craft_type: str
    clothing_category: str
    pattern_attributes: Optional[List[str]]
    yarn_weight: Optional[str]

    def create_pattern_query_filters(self) -> MetadataFilters:
        """
        Creates a pattern query for the pattern query engine

        Returns:
            MetadataFilters: A pattern query for the pattern query engine
        """
        filters = MetadataFilters(
            filters=[
                MetadataFilter(
                    key="craft", operator=FilterOperator.EQ, value=self.craft_type
                ),
                MetadataFilter(
                    key="pattern_categories.permalink",
                    operator=FilterOperator.ANY,
                    value=self.clothing_category,
                ),
            ],
            condition=FilterCondition.AND,
        )

        optional_filters = []
        if self.pattern_attributes:
            for attribute in self.pattern_attributes:
                attribute = attribute.replace(" ", "-").lower()
                optional_filters.append(
                    MetadataFilter(
                        key="pattern_attributes.permalink",
                        operator=FilterOperator.ANY,
                        value=attribute,
                    )
                )

        if self.yarn_weight:
            optional_filters.append(
                MetadataFilter(
                    key="gauge.yarn_weight_description",
                    operator=FilterOperator.TEXT_MATCH_INSENSITIVE,
                    value=self.yarn_weight,
                )
            )

        if len(optional_filters) > 0:
            optional_metadata_filters = MetadataFilters(
                filters=optional_filters, condition=FilterCondition.OR
            )
            full_filters = MetadataFilters(
                filters=[filters, optional_metadata_filters],
                condition=FilterCondition.AND,
            )

            return full_filters

        else:
            return filters
