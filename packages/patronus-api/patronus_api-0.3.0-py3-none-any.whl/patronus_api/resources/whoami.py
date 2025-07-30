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
from ..types.whoami_retrieve_response import WhoamiRetrieveResponse

__all__ = ["WhoamiResource", "AsyncWhoamiResource"]


class WhoamiResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WhoamiResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/patronus-ai/patronus-api-python#accessing-raw-response-data-eg-headers
        """
        return WhoamiResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WhoamiResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/patronus-ai/patronus-api-python#with_streaming_response
        """
        return WhoamiResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WhoamiRetrieveResponse:
        """Whoami"""
        return self._get(
            "/v1/whoami",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WhoamiRetrieveResponse,
        )


class AsyncWhoamiResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWhoamiResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/patronus-ai/patronus-api-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWhoamiResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWhoamiResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/patronus-ai/patronus-api-python#with_streaming_response
        """
        return AsyncWhoamiResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WhoamiRetrieveResponse:
        """Whoami"""
        return await self._get(
            "/v1/whoami",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WhoamiRetrieveResponse,
        )


class WhoamiResourceWithRawResponse:
    def __init__(self, whoami: WhoamiResource) -> None:
        self._whoami = whoami

        self.retrieve = to_raw_response_wrapper(
            whoami.retrieve,
        )


class AsyncWhoamiResourceWithRawResponse:
    def __init__(self, whoami: AsyncWhoamiResource) -> None:
        self._whoami = whoami

        self.retrieve = async_to_raw_response_wrapper(
            whoami.retrieve,
        )


class WhoamiResourceWithStreamingResponse:
    def __init__(self, whoami: WhoamiResource) -> None:
        self._whoami = whoami

        self.retrieve = to_streamed_response_wrapper(
            whoami.retrieve,
        )


class AsyncWhoamiResourceWithStreamingResponse:
    def __init__(self, whoami: AsyncWhoamiResource) -> None:
        self._whoami = whoami

        self.retrieve = async_to_streamed_response_wrapper(
            whoami.retrieve,
        )
