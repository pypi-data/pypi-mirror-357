# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Optional, cast
from typing_extensions import Literal

import httpx

from ..types import image_list_params, image_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..types.image import Image
from .._base_client import make_request_options
from ..types.image_list_response import ImageListResponse
from ..types.image_retrieve_response import ImageRetrieveResponse
from ..types.image_list_styles_response import ImageListStylesResponse

__all__ = ["ImagesResource", "AsyncImagesResource"]


class ImagesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ImagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ImagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ImagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return ImagesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        aspect_ratio: Literal["9:16", "16:9", "1:1"],
        prompt: str,
        image_style_id: Optional[str] | NotGiven = NOT_GIVEN,
        scene_id: Optional[str] | NotGiven = NOT_GIVEN,
        wait_for_generation: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Image:
        """
        Create an image from a prompt.

        Args:
          aspect_ratio: The aspect ratio of the image.

          prompt: The prompt to generate the image from.

          image_style_id: The ID of the image style to use. Use the
              [List image styles](#tag/images/GET/presets/{type}) endpoint to get a list of
              available image styles.

          scene_id: If you want to add the generated image to a video scene you can specify it here.

          wait_for_generation: If false, this endpoint immediately returns the incomplete image record, and you
              can poll the [Get image](#tag/images/GET/media/get/{id}) endpoint until the task
              completes. If true, this endpoint waits until the image generation completes,
              then returns the complete image record. Defaults to false.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/images",
            body=maybe_transform(
                {
                    "aspect_ratio": aspect_ratio,
                    "prompt": prompt,
                    "image_style_id": image_style_id,
                    "scene_id": scene_id,
                    "wait_for_generation": wait_for_generation,
                },
                image_create_params.ImageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Image,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImageRetrieveResponse:
        """
        Get image

        Args:
          id: The unique ID of the image record to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return cast(
            ImageRetrieveResponse,
            self._get(
                f"/images/{id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ImageRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list(
        self,
        *,
        limit: float | NotGiven = NOT_GIVEN,
        page: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImageListResponse:
        """
        Get all the images you have generated.

        Args:
          limit: The maximum number of items per page.

          page: The page number to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/images",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                    },
                    image_list_params.ImageListParams,
                ),
            ),
            cast_to=ImageListResponse,
        )

    def list_styles(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImageListStylesResponse:
        """Get all the image styles available for creating images."""
        return self._get(
            "/images/styles",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImageListStylesResponse,
        )


class AsyncImagesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncImagesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncImagesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncImagesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return AsyncImagesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        aspect_ratio: Literal["9:16", "16:9", "1:1"],
        prompt: str,
        image_style_id: Optional[str] | NotGiven = NOT_GIVEN,
        scene_id: Optional[str] | NotGiven = NOT_GIVEN,
        wait_for_generation: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Image:
        """
        Create an image from a prompt.

        Args:
          aspect_ratio: The aspect ratio of the image.

          prompt: The prompt to generate the image from.

          image_style_id: The ID of the image style to use. Use the
              [List image styles](#tag/images/GET/presets/{type}) endpoint to get a list of
              available image styles.

          scene_id: If you want to add the generated image to a video scene you can specify it here.

          wait_for_generation: If false, this endpoint immediately returns the incomplete image record, and you
              can poll the [Get image](#tag/images/GET/media/get/{id}) endpoint until the task
              completes. If true, this endpoint waits until the image generation completes,
              then returns the complete image record. Defaults to false.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/images",
            body=await async_maybe_transform(
                {
                    "aspect_ratio": aspect_ratio,
                    "prompt": prompt,
                    "image_style_id": image_style_id,
                    "scene_id": scene_id,
                    "wait_for_generation": wait_for_generation,
                },
                image_create_params.ImageCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Image,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImageRetrieveResponse:
        """
        Get image

        Args:
          id: The unique ID of the image record to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return cast(
            ImageRetrieveResponse,
            await self._get(
                f"/images/{id}",
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ImageRetrieveResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def list(
        self,
        *,
        limit: float | NotGiven = NOT_GIVEN,
        page: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImageListResponse:
        """
        Get all the images you have generated.

        Args:
          limit: The maximum number of items per page.

          page: The page number to retrieve.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/images",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "page": page,
                    },
                    image_list_params.ImageListParams,
                ),
            ),
            cast_to=ImageListResponse,
        )

    async def list_styles(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ImageListStylesResponse:
        """Get all the image styles available for creating images."""
        return await self._get(
            "/images/styles",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ImageListStylesResponse,
        )


class ImagesResourceWithRawResponse:
    def __init__(self, images: ImagesResource) -> None:
        self._images = images

        self.create = to_raw_response_wrapper(
            images.create,
        )
        self.retrieve = to_raw_response_wrapper(
            images.retrieve,
        )
        self.list = to_raw_response_wrapper(
            images.list,
        )
        self.list_styles = to_raw_response_wrapper(
            images.list_styles,
        )


class AsyncImagesResourceWithRawResponse:
    def __init__(self, images: AsyncImagesResource) -> None:
        self._images = images

        self.create = async_to_raw_response_wrapper(
            images.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            images.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            images.list,
        )
        self.list_styles = async_to_raw_response_wrapper(
            images.list_styles,
        )


class ImagesResourceWithStreamingResponse:
    def __init__(self, images: ImagesResource) -> None:
        self._images = images

        self.create = to_streamed_response_wrapper(
            images.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            images.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            images.list,
        )
        self.list_styles = to_streamed_response_wrapper(
            images.list_styles,
        )


class AsyncImagesResourceWithStreamingResponse:
    def __init__(self, images: AsyncImagesResource) -> None:
        self._images = images

        self.create = async_to_streamed_response_wrapper(
            images.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            images.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            images.list,
        )
        self.list_styles = async_to_streamed_response_wrapper(
            images.list_styles,
        )
