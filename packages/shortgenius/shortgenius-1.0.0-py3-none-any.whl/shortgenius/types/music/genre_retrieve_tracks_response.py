# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from ..._models import BaseModel

__all__ = ["GenreRetrieveTracksResponse", "GenreRetrieveTracksResponseItem"]


class GenreRetrieveTracksResponseItem(BaseModel):
    id: str
    """Unique ID of the track."""

    name: str

    preview_url: str


GenreRetrieveTracksResponse: TypeAlias = List[GenreRetrieveTracksResponseItem]
