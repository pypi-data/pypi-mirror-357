# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from shortgenius import Shortgenius, AsyncShortgenius
from tests.utils import assert_matches_type
from shortgenius.types import (
    Image,
    ImageListResponse,
    ImageRetrieveResponse,
    ImageListStylesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestImages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Shortgenius) -> None:
        image = client.images.create(
            aspect_ratio="9:16",
            prompt="prompt",
        )
        assert_matches_type(Image, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Shortgenius) -> None:
        image = client.images.create(
            aspect_ratio="9:16",
            prompt="prompt",
            image_style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            scene_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            wait_for_generation=True,
        )
        assert_matches_type(Image, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Shortgenius) -> None:
        response = client.images.with_raw_response.create(
            aspect_ratio="9:16",
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(Image, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Shortgenius) -> None:
        with client.images.with_streaming_response.create(
            aspect_ratio="9:16",
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = response.parse()
            assert_matches_type(Image, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Shortgenius) -> None:
        image = client.images.retrieve(
            "id",
        )
        assert_matches_type(ImageRetrieveResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Shortgenius) -> None:
        response = client.images.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImageRetrieveResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Shortgenius) -> None:
        with client.images.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = response.parse()
            assert_matches_type(ImageRetrieveResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Shortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.images.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Shortgenius) -> None:
        image = client.images.list()
        assert_matches_type(ImageListResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Shortgenius) -> None:
        image = client.images.list(
            limit=200,
            page=0,
        )
        assert_matches_type(ImageListResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Shortgenius) -> None:
        response = client.images.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImageListResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Shortgenius) -> None:
        with client.images.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = response.parse()
            assert_matches_type(ImageListResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_styles(self, client: Shortgenius) -> None:
        image = client.images.list_styles()
        assert_matches_type(ImageListStylesResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_styles(self, client: Shortgenius) -> None:
        response = client.images.with_raw_response.list_styles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImageListStylesResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_styles(self, client: Shortgenius) -> None:
        with client.images.with_streaming_response.list_styles() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = response.parse()
            assert_matches_type(ImageListStylesResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncImages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncShortgenius) -> None:
        image = await async_client.images.create(
            aspect_ratio="9:16",
            prompt="prompt",
        )
        assert_matches_type(Image, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncShortgenius) -> None:
        image = await async_client.images.create(
            aspect_ratio="9:16",
            prompt="prompt",
            image_style_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            scene_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            wait_for_generation=True,
        )
        assert_matches_type(Image, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.images.with_raw_response.create(
            aspect_ratio="9:16",
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = await response.parse()
        assert_matches_type(Image, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncShortgenius) -> None:
        async with async_client.images.with_streaming_response.create(
            aspect_ratio="9:16",
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = await response.parse()
            assert_matches_type(Image, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncShortgenius) -> None:
        image = await async_client.images.retrieve(
            "id",
        )
        assert_matches_type(ImageRetrieveResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.images.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = await response.parse()
        assert_matches_type(ImageRetrieveResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncShortgenius) -> None:
        async with async_client.images.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = await response.parse()
            assert_matches_type(ImageRetrieveResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncShortgenius) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.images.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncShortgenius) -> None:
        image = await async_client.images.list()
        assert_matches_type(ImageListResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncShortgenius) -> None:
        image = await async_client.images.list(
            limit=200,
            page=0,
        )
        assert_matches_type(ImageListResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.images.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = await response.parse()
        assert_matches_type(ImageListResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncShortgenius) -> None:
        async with async_client.images.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = await response.parse()
            assert_matches_type(ImageListResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_styles(self, async_client: AsyncShortgenius) -> None:
        image = await async_client.images.list_styles()
        assert_matches_type(ImageListStylesResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_styles(self, async_client: AsyncShortgenius) -> None:
        response = await async_client.images.with_raw_response.list_styles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = await response.parse()
        assert_matches_type(ImageListStylesResponse, image, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_styles(self, async_client: AsyncShortgenius) -> None:
        async with async_client.images.with_streaming_response.list_styles() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = await response.parse()
            assert_matches_type(ImageListStylesResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True
