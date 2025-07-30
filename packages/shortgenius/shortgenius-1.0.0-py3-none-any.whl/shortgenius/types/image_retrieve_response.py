# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = [
    "ImageRetrieveResponse",
    "UnionMember0",
    "UnionMember1",
    "UnionMember2",
    "UnionMember3",
    "UnionMember4",
    "UnionMember5",
    "UnionMember6",
    "UnionMember7",
    "UnionMember8",
    "UnionMember9",
    "UnionMember10",
    "UnionMember11",
    "UnionMember12",
    "UnionMember13",
]


class UnionMember0(BaseModel):
    id: str

    aspect_ratio: Literal["9:16", "16:9", "1:1"]

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    is_nsfw: bool

    prompt: str

    state: Literal["pending", "generating", "completed", "error", "request_smart_motion", "placeholder"]

    type: Literal["GeneratedImage"]

    url: Optional[str] = None

    image_style_id: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember1(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["pending", "generating", "completed", "error"]

    type: Literal["GeneratedVideo"]

    url: Optional[str] = None

    first_frame_image_id: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember2(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["pending", "generating", "completed", "error"]

    type: Literal["LumaGeneratedVideo"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember3(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["pending", "generating", "completed", "error"]

    type: Literal["Segmentation"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember4(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["completed"]

    type: Literal["Image"]

    url: Optional[str] = None

    user_id: str

    updated_at: Optional[str] = None


class UnionMember5(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["completed"]

    type: Literal["Video"]

    url: Optional[str] = None

    user_id: str

    updated_at: Optional[str] = None


class UnionMember6(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["completed"]

    type: Literal["UgcCreator"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember7(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["pending", "generating", "completed", "error"]

    type: Literal["UgcVideo"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember8(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["completed"]

    type: Literal["VideoClip"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember9(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["pending", "generating", "completed", "error"]

    type: Literal["Segmentation"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember10(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["uploading", "error", "completed", "request_smart_motion"]

    type: Literal["UserImage"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember11(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["uploading", "error", "completed", "request_smart_motion"]

    type: Literal["UserImageFromPicker"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember12(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["uploading", "error", "completed", "request_smart_motion"]

    type: Literal["UserVideo"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


class UnionMember13(BaseModel):
    id: str

    created_at: str
    """Date and time (ISO 8601) when the media was created."""

    state: Literal["pending", "generating", "error", "completed"]

    type: Literal["UserImageSegmentation"]

    url: Optional[str] = None

    updated_at: Optional[str] = None


ImageRetrieveResponse: TypeAlias = Union[
    UnionMember0,
    UnionMember1,
    UnionMember2,
    UnionMember3,
    UnionMember4,
    UnionMember5,
    UnionMember6,
    UnionMember7,
    UnionMember8,
    UnionMember9,
    UnionMember10,
    UnionMember11,
    UnionMember12,
    UnionMember13,
]
