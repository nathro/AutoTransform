# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""An interface for transformers that operate on single files with no metadata needs."""


from abc import abstractmethod
from typing import Any, Generic, TypeVar

from build import Mapping

from autotransform.batcher.base import Batch
from autotransform.common.cachedfile import CachedFile
from autotransform.transformer.base import Transformer

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class SingleTransformer(Generic[TParams], Transformer[TParams]):
    """A simple interface for writing a transformer that operates on an individual file level."""

    @abstractmethod
    def _transform_file(self, file: CachedFile) -> None:
        """Executes a transformation on a single file.

        Args:
            file (CachedFile): The file that is being transformed
        """

    def transform(self, batch: Batch) -> None:
        """Splits out all files to be transformed.

        Args:
            batch (Batch): The batch being transformed
        """

        # pylint: disable=unspecified-encoding
        for file in batch["files"]:
            self._transform_file(file)
