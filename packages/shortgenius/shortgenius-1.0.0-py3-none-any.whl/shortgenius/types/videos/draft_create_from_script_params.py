# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DraftCreateFromScriptParams"]


class DraftCreateFromScriptParams(TypedDict, total=False):
    script: Required[str]
    """The content you want the AI to narrate.

    It will split it up into logical scenes, and illustrate each scene.
    """
