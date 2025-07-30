# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.connection_list_response import ConnectionListResponse

__all__ = ["ConnectionsResource", "AsyncConnectionsResource"]


class ConnectionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConnectionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ConnectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConnectionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return ConnectionsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectionListResponse:
        """List all the video publishing destinations you have configured."""
        return self._get(
            "/connections",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionListResponse,
        )


class AsyncConnectionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConnectionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncConnectionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConnectionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ShortGenius/shortgenius-sdk-python#with_streaming_response
        """
        return AsyncConnectionsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConnectionListResponse:
        """List all the video publishing destinations you have configured."""
        return await self._get(
            "/connections",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectionListResponse,
        )


class ConnectionsResourceWithRawResponse:
    def __init__(self, connections: ConnectionsResource) -> None:
        self._connections = connections

        self.list = to_raw_response_wrapper(
            connections.list,
        )


class AsyncConnectionsResourceWithRawResponse:
    def __init__(self, connections: AsyncConnectionsResource) -> None:
        self._connections = connections

        self.list = async_to_raw_response_wrapper(
            connections.list,
        )


class ConnectionsResourceWithStreamingResponse:
    def __init__(self, connections: ConnectionsResource) -> None:
        self._connections = connections

        self.list = to_streamed_response_wrapper(
            connections.list,
        )


class AsyncConnectionsResourceWithStreamingResponse:
    def __init__(self, connections: AsyncConnectionsResource) -> None:
        self._connections = connections

        self.list = async_to_streamed_response_wrapper(
            connections.list,
        )
