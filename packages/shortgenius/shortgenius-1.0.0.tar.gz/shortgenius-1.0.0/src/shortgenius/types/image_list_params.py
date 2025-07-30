# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ImageListParams"]


class ImageListParams(TypedDict, total=False):
    limit: float
    """The maximum number of items per page."""

    page: float
    """The page number to retrieve."""
