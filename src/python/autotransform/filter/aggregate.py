# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the AggregateFilter."""

from typing import Any, ClassVar, Dict, Sequence, Type

from autotransform.filter.base import FACTORY as filter_factory
from autotransform.filter.base import Filter, FilterName
from autotransform.item.base import Item
from autotransform.step.condition.aggregate import AggregatorType


class AggregateFilter(Filter):
    """A Filter which aggregates a list of Filters using the supplied aggregator and
    returns the result of the aggregation.

    Attributes:
        aggregator (AggregatorType): How to aggregate the filters, using any or all.
        filters (Sequence[Filter]): The filters to be aggregated.
        name (ClassVar[FilterName]): The name of the Component.
    """

    aggregator: AggregatorType
    filters: Sequence[Filter]

    name: ClassVar[FilterName] = FilterName.AGGREGATE

    def _is_valid(self, item: Item) -> bool:
        """Checks whether the aggregation of all filters passes.

        Args:
            item (Item): The Item the Filter is checking.

        Returns:
            bool: Whether the Item passes the Filter.
        """

        aggregator_func = all if self.aggregator == AggregatorType.ALL else any
        return aggregator_func(filter.is_valid(item) for filter in self.filters)

    @classmethod
    def from_data(cls: Type["AggregateFilter"], data: Dict[str, Any]) -> "AggregateFilter":
        """Produces an instance of the component from decoded data.

        Args:
            data (Dict[str, Any]): The JSON decoded data.

        Returns:
            AggregateFilter: An instance of the component.
        """

        aggregator = AggregatorType(data["aggregator"])
        filters = [filter_factory.get_instance(filter) for filter in data["filters"]]
        return cls(aggregator=aggregator, filters=filters)
