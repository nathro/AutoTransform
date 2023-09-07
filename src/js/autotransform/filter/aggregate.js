// AutoTransform
// Large scale, component based code modification library
//
// Licensed under the MIT License <http://opensource.org/licenses/MIT>
// SPDX-License-Identifier: MIT
// Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

// @black_format

/* The implementation for the AggregateFilter. */

import { FACTORY as filter_factory } from 'autotransform/filter/base';
import { Filter, FilterName } from 'autotransform/filter/base';
import { Item } from 'autotransform/item/base';
import { AggregatorType } from 'autotransform/step/condition/aggregate';

class AggregateFilter extends Filter {
    /* A Filter which aggregates a list of Filters using the supplied aggregator and
    returns the result of the aggregation.

    Attributes:
        aggregator (AggregatorType): How to aggregate the filters, using any or all.
        filters (Sequence[Filter]): The filters to be aggregated.
        name (ClassVar[FilterName]): The name of the Component.
    */

    static name = FilterName.AGGREGATE;

    constructor(aggregator, filters) {
        super();
        this.aggregator = aggregator;
        this.filters = filters;
    }

    _is_valid(item) {
        /* Checks whether the aggregation of all filters passes.

        Args:
            item (Item): The Item the Filter is checking.

        Returns:
            bool: Whether the Item passes the Filter.
        */

        if (this.aggregator === AggregatorType.ALL) {
            return this.filters.every(filter => filter.is_valid(item));
        }

        if (this.aggregator === AggregatorType.ANY) {
            return this.filters.some(filter => filter.is_valid(item));
        }

        throw new Error(`Unknown aggregator type ${this.aggregator}`);
    }

    static from_data(data) {
        /* Produces an instance of the component from decoded data.

        Args:
            data (Dict[str, Any]): The JSON decoded data.

        Returns:
            AggregateFilter: An instance of the component.
        */

        const aggregator = (
            data["aggregator"]
            if (data["aggregator"] instanceof AggregatorType)
            else new AggregatorType(data["aggregator"])
        );
        const filters = data["filters"].map(filter => filter_factory.get_instance(filter));
        return new AggregateFilter(aggregator, filters);
    }
}

export { AggregateFilter };